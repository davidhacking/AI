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

def mask_fn(env):
    return env.get_action_mask()

def train():
    # 创建带掩码的环境
    env = DummyVecEnv([lambda: ActionMasker(ChineseChessEnv(), mask_fn)])
    
    # 创建MaskablePPO模型
    model = MaskablePPO(
        "MlpPolicy",  # 改为使用CNN策略
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
    )
    
    # 开始训练（使用动作掩码）
    model.learn(
        total_timesteps=1_000_000,
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