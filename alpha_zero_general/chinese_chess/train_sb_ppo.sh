#!/bin/bash

while true; do
    # 启动训练，并设置两小时超时
    echo "启动训练进程（最多运行2小时）..."
    timeout 7200 python sb_ppo.py --train --resume 2>&1 | tee train_sb_ppo.log

    # 检查退出状态
    if [ $? -eq 124 ]; then
        echo "检测到超时，重启训练..."
    else
        echo "训练正常结束，退出。"
        break  # 如果希望训练完成后不重启，取消下一行的注释
        # break
    fi
done