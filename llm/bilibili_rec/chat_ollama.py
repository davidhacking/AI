from langchain_ollama import ChatOllama

chat_model = ChatOllama(
    base_url="http://192.168.1.2:11434",
    # model="qwen2.5:32b-instruct-q4_K_M",
    model="qwen2.5:14b-instruct-q4_K_M",
    # model="deepseek-r1:8b",
    num_ctx=32000,
)

response = chat_model.invoke("你好！")
print(response.content)