import os
from typing import Literal

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

load_dotenv(override=True)

tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# System prompt to steer the agent to be an expert resaercher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included."""


def main():
    from pydantic import SecretStr

    api_key = os.getenv("OPENAI_API_KEY", None)
    base_url = os.getenv("OPENAI_BASE_URL", None)
    model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4o")
    if model_id.startswith("openai:"):
        model_id = model_id[len("openai:") :]  # 去掉 "openai:" 前缀

    model = ChatOpenAI(
        model_name=model_id,
        openai_api_key=SecretStr(api_key) if api_key else None,
        openai_api_base=base_url,
    )
    agent = create_deep_agent(
        model=model, tools=[internet_search], system_prompt=research_instructions
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is langgraph?"}]}
    )

    # Print the agent's response
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
