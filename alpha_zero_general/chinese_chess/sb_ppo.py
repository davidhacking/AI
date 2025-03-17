# sb_ppo.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.policies import ActorCriticCnnPolicy
from ChineseChessGame import ChineseChessEnv, ChineseChessBoard
from stable_baselines3.common.vec_env import DummyVecEnv
import os
import numpy as np
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.callbacks import EvalCallback
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import concurrent

def mask_fn(env):
    return env.get_action_mask()

class CustomFeatureExtractor(BaseFeaturesExtractor):
    """自定义特征提取器处理(14,10,9)的棋盘平面"""
    def __init__(self, observation_space, features_dim=512, 
                 res_layers=10, filters=256):
        super().__init__(observation_space, features_dim)
        
        # 输入形状适配：假设observation_space.shape = (14,10,9)
        self.alpha_zero_net = nn.Sequential(
            # 初始卷积层
            nn.Conv2d(14, filters, 3, padding=1, bias=False),
            nn.BatchNorm2d(filters),
            nn.ReLU(inplace=True),
            
            # 残差块
            *[ResidualBlock(filters) for _ in range(res_layers)],
            
            # 全局特征提取
            nn.AdaptiveAvgPool2d((1,1)),
            nn.Flatten(),
            nn.Linear(filters, features_dim)
        )

    def forward(self, obs):
        # 输入形状转换：假设obs原始形状为[batch, 14*10*9]
        obs = obs.view(-1, 14, 10, 9)  # 转换为CNN需要的形状
        return self.alpha_zero_net(obs)

class ResidualBlock(nn.Module):
    """残差块模块"""
    def __init__(self, filters):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(filters, filters, 3, padding=1, bias=False),
            nn.BatchNorm2d(filters),
            nn.ReLU(inplace=True),
            nn.Conv2d(filters, filters, 3, padding=1, bias=False),
            nn.BatchNorm2d(filters)
        )
        
    def forward(self, x):
        return F.relu(x + self.block(x))

def check_file_update(file_path, last_modified_time):
    try:
        current_modified_time = os.path.getmtime(file_path)
        if current_modified_time > last_modified_time:
            return True, current_modified_time
        else:
            return False, last_modified_time
    except FileNotFoundError:
        return False, last_modified_time

def check_file_exists(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False

class ModelLoader:
    def __init__(self, env, model_path):
        self.env = env
        self.model_path = model_path
        self.model_file_name = model_path + "/best/best_model.zip"
        self.last_modified_time = 0
        if check_file_exists(self.model_file_name):
            self.model = create_model(self.env, self.model_path, resume=True)
            self.last_modified_time = os.path.getmtime(self.model_file_name)
        else:
            self.model = create_model(self.env, self.model_path, resume=False)
    def load_model(self):
        updated, ts = check_file_update(self.model_file_name, self.last_modified_time)
        if updated:
            self.model = create_model(self.env, self.model_path, resume=True)
            self.last_modified_time = ts
            print(f"{self.model_file_name}模型更新成功")
        return self.model
def create_model(env, model_path="./ppo_chess_red_model/ppo_chess", resume=False):
    """创建或加载模型的工厂函数"""
    policy_kwargs = {
        "features_extractor_class": CustomFeatureExtractor,
        "features_extractor_kwargs": {
            "features_dim": 512,
            "res_layers": 10,
            "filters": 256
        },
        "net_arch": dict(pi=[512, 512], vf=[512, 512]),
        "activation_fn": nn.ReLU,
        "ortho_init": True,
    }

    if resume:
        model_path = model_path
        model = MaskablePPO.load(
            model_path,
            env=env,
            device="cuda",
            custom_objects={
                "learning_rate": 3e-4,
                "policy_kwargs": policy_kwargs
            }
        )
        return model
    else:
        return MaskablePPO(
            MaskableActorCriticPolicy,
            env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=4096,
            batch_size=512,
            n_epochs=15,
            gamma=0.99,
            gae_lambda=0.92,
            clip_range=0.2,
            ent_coef=0.02,
            vf_coef=0.5,
            max_grad_norm=0.5,
            policy_kwargs=policy_kwargs,
        )

class MaskableEvalCallback(EvalCallback):
    
    def _on_step(self) -> bool:
        if self.eval_freq > 0 and self.n_calls % self.eval_freq == 0:
            episode_rewards = []
            episode_lengths = []
            for _ in range(self.n_eval_episodes):
                obs, _ = self.realEvalEnv.reset()
                done = False
                episode_reward = 0.0
                episode_len = 0
                while not done:
                    # 获取当前动作掩码
                    action_mask = self.realEvalEnv.get_action_mask()
                    
                    # 带掩码预测
                    action, _ = self.model.predict(
                        obs, 
                        action_masks=action_mask,
                        deterministic=self.deterministic
                    )
                    action = int(action)
                    # 渲染当前棋盘
                    self.realEvalEnv.render()
                    # 执行动作
                    obs, reward, done, _, _ = self.realEvalEnv.step(action)
                    episode_reward += reward
                    episode_len += 1
                    
                episode_rewards.append(episode_reward)
                episode_lengths.append(episode_len)
            
            mean_reward, std_reward = np.mean(episode_rewards), np.std(episode_rewards)
            mean_ep_length, std_ep_length = np.mean(episode_lengths), np.std(episode_lengths)
            self.last_mean_reward = float(mean_reward)
            if mean_reward > self.best_mean_reward:
                if self.verbose >= 1:
                    print("New best mean reward!")
                if self.best_model_save_path is not None:
                    self.model.save(os.path.join(self.best_model_save_path, "best_model"))
                self.best_mean_reward = float(mean_reward)
        return True

def train(resume=False):
    realEnvRed = ChineseChessEnv()
    realEnvRed.env_player = ChineseChessBoard.RED
    realEnvBlack = ChineseChessEnv()
    realEnvBlack.env_player = ChineseChessBoard.BLACK
    envRed = DummyVecEnv([lambda: ActionMasker(realEnvRed, mask_fn)])
    envBlack = DummyVecEnv([lambda: ActionMasker(realEnvBlack, mask_fn)])
    
    realEnvRed.get_model_func = ModelLoader(envRed, "./ppo_chess_black_model/ppo_chess").load_model
    realEnvBlack.get_model_func = ModelLoader(envBlack, "./ppo_chess_red_model/ppo_chess").load_model

    red_checkpoint_dir = "./ppo_chess_red_model/checkpoints/"
    black_checkpoint_dir = "./ppo_chess_black_model/checkpoints/"
    os.makedirs(red_checkpoint_dir, exist_ok=True)
    os.makedirs(black_checkpoint_dir, exist_ok=True)
    
    # 自动保存检查点（每50万步）
    red_checkpoint_callback = CheckpointCallback(
        save_freq=500_000,
        save_path=red_checkpoint_dir,
        name_prefix="ppo_chess_red",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )
    black_checkpoint_callback = CheckpointCallback(
        save_freq=500_000,
        save_path=black_checkpoint_dir,
        name_prefix="ppo_chess_black",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )
    
    # 最佳模型保存（需要eval_env）
    realEvalEnvRed = ChineseChessEnv()
    realEvalEnvRed.env_player = ChineseChessBoard.RED
    realEvalEnvBlack = ChineseChessEnv()
    realEvalEnvBlack.env_player = ChineseChessBoard.BLACK
    eval_env_red = DummyVecEnv([lambda: ActionMasker(realEvalEnvRed, mask_fn)])
    eval_env_black = DummyVecEnv([lambda: ActionMasker(realEvalEnvBlack, mask_fn)])
    realEvalEnvRed.get_model_func = ModelLoader(eval_env_red, "./ppo_chess_black_model/ppo_chess").load_model
    realEvalEnvBlack.get_model_func = ModelLoader(eval_env_black, "./ppo_chess_red_model/ppo_chess").load_model

    eval_red_callback = MaskableEvalCallback(
        eval_env_red,
        best_model_save_path="./ppo_chess_red_model/best/",
        log_path="./ppo_chess_red_model/logs/",
        eval_freq=200_000,  # 每20万步评估一次
        deterministic=True,
        render=True,
        n_eval_episodes=5
    )
    eval_red_callback.realEvalEnv = realEvalEnvRed

    eval_black_callback = MaskableEvalCallback(
        eval_env_black,
        best_model_save_path="./ppo_chess_black_model/best/",
        log_path="./ppo_chess_black_model/logs/",
        eval_freq=200_000,  # 每20万步评估一次
        deterministic=True,
        render=True,
        n_eval_episodes=5
    )
    eval_black_callback.realEvalEnv = realEvalEnvBlack
    
    def worker_red(name):
        try:
            # 每个worker独立创建模型
            local_model = create_model(envRed, "./ppo_chess_red_model/ppo_chess", resume)
            local_model.learn(
                total_timesteps=5_000_000,
                callback=[red_checkpoint_callback, eval_red_callback],
                reset_num_timesteps=True,
                use_masking=True
            )
            local_model.save("./ppo_chess_red_model/ppo_chess")
            print(f"[Red] 训练完成，模型已保存")
        except Exception as e:
            print(f"[Red] 训练出错: {str(e)}")

    def worker_black(name):
        try:
            # 每个worker独立创建模型
            local_model = create_model(envBlack, "./ppo_chess_black_model/ppo_chess", resume)
            local_model.learn(
                total_timesteps=5_000_000,
                callback=[black_checkpoint_callback, eval_black_callback],
                reset_num_timesteps=True,
                use_masking=True
            )
            local_model.save("./ppo_chess_black_model/ppo_chess")
            print(f"[Black] 训练完成，模型已保存")
        except Exception as e:
            print(f"[Black] 训练出错: {str(e)}")

    # 修改线程启动方式
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 显式获取future对象
        future_red = executor.submit(worker_red, "Red")
        future_black = executor.submit(worker_black, "Black")
        
        # 等待所有任务完成
        concurrent.futures.wait([future_red, future_black])
        # concurrent.futures.wait([future_black])
        
        # 检查异常
        for future in [future_red, future_black]:
            if future.exception():
                print(f"训练出现异常: {future.exception()}")
        
        # for future in [future_black]:
        #     if future.exception():
        #         print(f"训练出现异常: {future.exception()}")

    print("主线程等待所有训练任务完成")  # 添加进度提示

def test(model_path=None):
    """
    测试训练好的模型并渲染过程
    """
    # 创建带掩码的环境
    realEnv = ChineseChessEnv()
    env = ActionMasker(realEnv, mask_fn)
    
    # 加载模型
    if model_path is None:
        model_path = "./ppo_chess_model/ppo_chess"
    model = MaskablePPO.load(model_path, env=env)
    realEnv.model = model

    obs, _ = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        # 获取当前掩码
        action_mask = mask_fn(realEnv)
        
        # 渲染当前棋盘
        env.render()
        
        # 模型预测动作（带掩码）
        action, _ = model.predict(
            obs, 
            action_masks=action_mask,  # 添加动作掩码
            deterministic=True
        )
        action = int(action)
        
        # 执行动作
        obs, reward, done, _, _ = env.step(action)
        total_reward += reward
        
        # 打印信息
        print(f"执行动作: {action}")
        print(f"当前奖励: {reward:.1f}，累计奖励: {total_reward:.1f}")
        print("-"*50)
    
    env.render()
    print(f"游戏结束，总奖励: {total_reward:.1f}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="训练模式")
    parser.add_argument("--test", action="store_true", help="测试模式")
    parser.add_argument("--model", type=str, help="测试使用的模型路径")
    parser.add_argument("--resume", action="store_true")  # 新增resume参数
    args = parser.parse_args()

    if args.train:
        train(resume=args.resume)
    elif args.test:
        test(args.model)
    else:
        print("请指定模式：--train 或 --test")