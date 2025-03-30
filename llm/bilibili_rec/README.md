
## llm
```bash
conda create -n browser-use python=3.11
conda activate browser-use
pip install playwright pydantic psutil requests -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install browser-use -i https://pypi.tuna.tsinghua.edu.cn/simple
playwright install
```

```bash
ollama pull deepseek-r1:8b
ollama pull deepseek-r1:14b
ollama pull deepseek-r1:14b-qwen-distill-q4_K_M
ollama pull qwen2.5:32b-instruct-q4_K_M
ollama pull qwen2.5:14b-instruct-q4_K_M
```

```bash
cd \\host.lan\Data\github\AI\llm\bilibili_rec
C:\Users\windows\AppData\Local\ms-playwright\chromium-1161\chrome-win\chrome.exe --remote-debugging-port=9222
```