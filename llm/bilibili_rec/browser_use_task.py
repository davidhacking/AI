import asyncio

from langchain_ollama import ChatOllama

from browser_use import Agent, Browser, BrowserConfig
from browser_use.agent.views import AgentHistoryList

browser = Browser(config=BrowserConfig(
    cdp_url='http://localhost:9222',
))

async def run_search() -> AgentHistoryList:
	agent = Agent(
		task="打开 https://www.bilibili.com/ 给出目前比较热门的视频列表(记住是视频不是游戏或其他) 标题+链接 的形式给我",
		llm=ChatOllama(
            base_url="http://192.168.1.2:11434",
			# model='qwen2.5:32b-instruct-q4_K_M',
			model='deepseek-r1:8b',
			num_ctx=32000,
		),
        browser=browser,
	)

	result = await agent.run()
	return result


async def main():
	result = await run_search()
	print('\n\n', result)


if __name__ == '__main__':
	asyncio.run(main())