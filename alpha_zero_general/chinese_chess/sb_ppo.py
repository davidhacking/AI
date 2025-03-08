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
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

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

def train():
    # 创建带掩码的环境
    env = DummyVecEnv([lambda: ActionMasker(ChineseChessEnv(), mask_fn)])
    
    model = MaskablePPO(
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
        policy_kwargs={
            "features_extractor_class": CustomFeatureExtractor,
            "features_extractor_kwargs": {
                "features_dim": 512,
                "res_layers": 10,    # 残差层数
                "filters": 256       # 卷积通道数
            },
            "net_arch": dict(pi=[512, 512], vf=[512, 512]),
            "activation_fn": nn.ReLU,
            "ortho_init": True,
        },
    )
    
    # 开始训练（使用动作掩码）
    model.learn(
        total_timesteps=5_000_000,
        callback=None,
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
    args = parser.parse_args()

    if args.train:
        train()
    elif args.test:
        test(args.model)
    else:
        print("请指定模式：--train 或 --test")