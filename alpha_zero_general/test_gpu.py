# -*- coding: utf-8 -*-

import torch
print(torch.__version__)
print(torch.version.cuda)  # PyTorch 对应的 CUDA 版本

# 检查 CUDA 是否可用
cuda_available = torch.cuda.is_available()
print(f"CUDA 是否可用: {cuda_available}")

if cuda_available:
    # 检查 CuDNN 是否可用
    cudnn_available = torch.backends.cudnn.is_available()
    print(f"CuDNN 是否可用: {cudnn_available}")

    if cudnn_available:
        # 查看当前 CuDNN 是否启用
        cudnn_enabled = torch.backends.cudnn.enabled
        print(f"当前 CuDNN 是否启用: {cudnn_enabled}")

        # 启用 CuDNN
        torch.backends.cudnn.enabled = True

        # 设置 CuDNN 为确定性模式（可复现结果）
        torch.backends.cudnn.deterministic = True

        # 禁用 CuDNN 的自动调优功能
        torch.backends.cudnn.benchmark = False

        print("已启用 CuDNN，并设置为确定性模式。")

        # 创建一个简单的模型并在 GPU 上运行
        model = torch.nn.Conv2d(3, 64, kernel_size=3, padding=1).cuda()
        input_tensor = torch.randn(1, 3, 224, 224).cuda()
        output = model(input_tensor)
        print("简单卷积模型在 GPU 上运行成功，输出形状:", output.shape)
    else:
        print("虽然 CUDA 可用，但 CuDNN 不可用。")
else:
    print("CUDA 不可用，无法使用 CuDNN。")