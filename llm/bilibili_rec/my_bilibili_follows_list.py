import asyncio

from langchain_ollama import ChatOllama

from browser_use import Agent, Browser, BrowserConfig
from browser_use.agent.views import AgentHistoryList

browser = Browser(config=BrowserConfig(
    cdp_url='http://localhost:9222',
))

async def run_search() -> AgentHistoryList:
	task_def = """
	1.这个是我的关注页面 https://space.bilibili.com/97754294/relation/follow 找到“全部关注”，
	2.里面每个item是我关注的up主（up主就是视频作者，在这个页面上就是一个一个的头像，头像右边就是up主的名字）
	3.我关注的up主名字列表返回给我，因为关注的内容比较多有500多个，你需要不断地点击下一页，把每页的up主都返回给我
	"""
	agent = Agent(
		task=task_def,
		llm=ChatOllama(
            base_url="http://192.168.1.2:11434",
			# model='qwen2.5:32b-instruct-q4_K_M',
			# model='qwen2.5:14b-instruct-q4_K_M',
			# model='deepseek-r1:8b',
			model='deepseek-r1:14b-qwen-distill-q4_K_M',
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