# sb_ppo.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.policies import ActorCriticCnnPolicy
from ChineseChessGame import ChineseChessEnv
from stable_baselines3.common.vec_env import DummyVecEnv
import os
import numpy as np
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.callbacks import EvalCallback
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

def create_model(env, resume=False):
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
        model_path = "./ppo_chess_model/ppo_chess"
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
    # 创建带掩码的环境
    realEnv = ChineseChessEnv()
    env = DummyVecEnv([lambda: ActionMasker(realEnv, mask_fn)])
    
    model = create_model(env, resume)
    realEnv.model = model

    checkpoint_dir = "./ppo_chess_model/checkpoints/"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # 自动保存检查点（每50万步）
    checkpoint_callback = CheckpointCallback(
        save_freq=500_000,
        save_path=checkpoint_dir,
        name_prefix="ppo_chess",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )
    
    # 最佳模型保存（需要eval_env）
    realEvalEnv = ChineseChessEnv()
    eval_env = DummyVecEnv([lambda: ActionMasker(realEvalEnv, mask_fn)])
    realEvalEnv.model = model
    eval_callback = MaskableEvalCallback(
        eval_env,
        best_model_save_path="./ppo_chess_model/best/",
        log_path="./ppo_chess_model/logs/",
        eval_freq=200_000,  # 每20万步评估一次
        deterministic=True,
        render=True,
        n_eval_episodes=5
    )
    eval_callback.realEvalEnv = realEvalEnv
    
    # 开始训练（使用动作掩码）
    model.learn(
        total_timesteps=5_000_000,
        callback=[checkpoint_callback, eval_callback],  # 添加回调
        reset_num_timesteps=True,
        use_masking=True  # 启用掩码机制
    )
    
    # 保存模型
    save_path = "./ppo_chess_model"
    os.makedirs(save_path, exist_ok=True)
    model.save(f"{save_path}/ppo_chess")
    print(f"Model saved to {save_path}")

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