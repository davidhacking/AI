from huggingface_hub import snapshot_download

model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

local_path = snapshot_download(
    repo_id=model_name,
    revision="main",
    local_dir="./llm_downloads/DeepSeek-R1-Distill-Qwen-7B",
    local_dir_use_symlinks=False,
    resume_download=True,
    token=True
)

print(f"模型已保存到：{local_path}")