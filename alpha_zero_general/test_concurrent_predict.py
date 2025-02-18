import torch
import torch.multiprocessing as mp
from functools import partial
from tqdm import tqdm
from utils import *
from chinese_chess.pytorch.ChineseChessNNet import CChessModel
from chinese_chess.ChineseChessGame import ChineseChessGame

# 必须设置共享内存策略
torch.multiprocessing.set_sharing_strategy('file_system')

class ModelTester:
    def __init__(self, game, args):
        self.game = game
        self.args = args
        
        # 只保存初始化参数，不创建实际模型
        self.model_weights = self._load_base_weights()

    def _load_base_weights(self):
        """单独加载权重文件，避免持有模型实例"""
        model = CChessModel(self.game, self.args)
        return model.state_dict()

    def _prepare_input(self):
        """生成测试输入数据（使用共享内存）"""
        data = torch.randn(1, self.game.getBoardSize()[0], self.game.getBoardSize()[1], self.game.getBoardSize()[2])
        return data.share_memory_()

    # GPU工作进程初始化
    @staticmethod
    def _gpu_worker_init(game, args, weights):
        global _gpu_model
        torch.cuda.init()  # 显式初始化CUDA上下文
        _gpu_model = CChessModel(game, args).to('cuda:0')
        _gpu_model.load_state_dict(weights)
        _gpu_model.eval()

    # CPU工作进程初始化
    @staticmethod
    def _cpu_worker_init(game, args, weights):
        global _cpu_model
        _cpu_model = CChessModel(game, args).to('cpu')
        _cpu_model.load_state_dict(weights)
        _cpu_model.eval()

    # GPU任务包装器
    @staticmethod
    def _gpu_task(data):
        with torch.no_grad():
            data = data.to('cuda:0')
            pi, v = _gpu_model(data)
            return pi.cpu(), v.cpu()

    # CPU任务包装器
    @staticmethod
    def _cpu_task(data):
        with torch.no_grad():
            data = data.to('cpu')
            pi, v = _cpu_model(data)
            return pi, v
    
    def test_sequence_exec_cpu_model(self, n=6):
        _cpu_model = CChessModel(self.game, self.args).to('cpu')
        _cpu_model.load_state_dict(self.model_weights)
        _cpu_model.eval()
        data = self._prepare_input().to('cpu')
        results = []
        with torch.no_grad():
            pi, v = _cpu_model(data)
            results.append((pi, v))
        print(f"cpu results({len(results)})={results}")
    
    def test_sequence_exec_gpu_model(self, n=6):
        _gpu_model = CChessModel(self.game, self.args).to('cuda:0')
        _gpu_model.load_state_dict(self.model_weights)
        _gpu_model.eval()
        data = self._prepare_input().to('cuda:0')
        results = []
        with torch.no_grad():
            pi, v = _gpu_model(data)
            results.append((pi, v))
        print(f"gpu results({len(results)})={results}")

    def test_mixed_concurrent(self, gpu_processes=2, cpu_processes=6, num_tasks=100):
        mp.set_start_method('spawn', force=True)
        
        # 准备共享输入数据
        base_data = self._prepare_input()
        task_data = [base_data.clone() for _ in range(num_tasks)]

        results = []
        with tqdm(total=num_tasks, desc="混合并发测试") as pbar:
            # GPU进程池处理
            if gpu_processes > 0:
                with mp.Pool(
                    processes=gpu_processes,
                    initializer=self._gpu_worker_init,
                    initargs=(self.game, self.args, self.model_weights)
                ) as gpu_pool:
                    # 分配GPU任务量：当CPU进程数为0时使用全部任务
                    gpu_task_count = num_tasks if cpu_processes <= 0 else num_tasks//2
                    gpu_tasks = task_data[:gpu_task_count]
                    
                    # 提交异步任务
                    gpu_results = gpu_pool.imap_unordered(self._gpu_task, gpu_tasks, chunksize=10)
                    for result in gpu_results:
                        results.append(result)
                        pbar.update(1)

            # CPU进程池处理
            if cpu_processes > 0:
                with mp.Pool(
                    processes=cpu_processes,
                    initializer=self._cpu_worker_init,
                    initargs=(self.game, self.args, self.model_weights)
                ) as cpu_pool:
                    # 分配CPU任务量：当GPU进程数为0时使用全部任务
                    cpu_start = 0 if gpu_processes <= 0 else num_tasks//2
                    cpu_tasks = task_data[cpu_start:]
                    
                    # 提交异步任务
                    cpu_results = cpu_pool.imap_unordered(self._cpu_task, cpu_tasks, chunksize=10)
                    for result in cpu_results:
                        results.append(result)
                        pbar.update(1)
        print(f"results({len(results)})={results}")
        return results

if __name__ == "__main__":
    
    args = dotdict({
        'num_channels': 512,
        'dropout': 0.3,
    })
    tester = ModelTester(ChineseChessGame(), args)
    tester.test_sequence_exec_gpu_model()
    tester.test_sequence_exec_cpu_model()
    # 测试示例
    print("=== 混合并发测试 ===")
    results = tester.test_mixed_concurrent(
        gpu_processes=1,
        cpu_processes=0,
        num_tasks=100
    )