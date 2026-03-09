import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from news_fetcher import get_news
from stock_data import get_stock_data
from rag_engine import store_news, search_news

load_dotenv()

@tool
def fetch_latest_news(company_name: str) -> str:
    """
    Fetches the latest news articles for a company.
    Use this when you need current news about a company.
    Input: company name like 'Apple' or 'Tesla'
    """
    articles = get_news(company_name, num_articles=5)
    store_news(company_name)
    result = f'Latest news for {company_name}:\n\n'
    for i, article in enumerate(articles):
        result += f'{i+1}. {article["title"]}\n'
        result += f'   Source: {article["source"]}\n'
        result += f'   Date: {article["date"]}\n'
        result += f'   Summary: {article["description"]}\n\n'
    return result


@tool
def fetch_stock_price(ticker: str) -> str:
    """
    Fetches real-time stock price and company info.
    Use this when you need current stock price data.
    Input: stock ticker like 'AAPL', 'TSLA', 'GOOGL'
    """
    data = get_stock_data(ticker)
    result = f'Stock data for {data["company_name"]} ({data["ticker"]}):\n'
    result += f'Current Price: ${data["current_price"]}\n'
    result += f'Previous Close: ${data["previous_close"]}\n'
    result += f'Sector: {data["sector"]}\n'
    history = data['history'].tail(5)
    result += f'\nLast 5 days price history:\n'
    result += history[['Close']].to_string()
    return result


@tool
def search_memory(query: str) -> str:
    """
    Searches past news articles stored in memory.
    Use this to find relevant past news for context.
    Input: a question or topic to search for
    """
    results = search_news(query, num_results=3)
    if not results:
        return 'No relevant articles found in memory.'
    output = f"Relevant articles from memory for '{query}':\n\n"
    for i, result in enumerate(results):
        output += f'{i+1}. {result["metadata"]["title"]}\n'
        output += f'   Source: {result["metadata"]["source"]}\n'
        output += f'   Date: {result["metadata"]["date"]}\n\n'
    return output


@tool
def generate_market_report(company_name: str) -> str:
    """
    Generates a full market intelligence report for a company.
    Use this as the final step after gathering all data.
    Input: company name
    """
    return f'Generate a comprehensive market intelligence report for {company_name} based on all the data and news you have gathered. Include: 1) Current market position 2) Recent news sentiment 3) Key risks 4) Key opportunities 5) Overall signal: BUY, SELL, or HOLD with reasoning.'


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [
    fetch_latest_news,
    fetch_stock_price,
    search_memory,
    generate_market_report
]

system_prompt = """You are an expert financial market intelligence agent.

Your job is to analyze stocks and companies by:
1. Fetching the latest news
2. Getting current stock prices
3. Searching memory for past context
4. Generating a comprehensive intelligence report

Always use the tools in this order:
- First fetch news
- Then fetch stock price
- Then search memory for context
- Finally generate the market report

Be specific, data-driven, and always end with a clear BUY, SELL, or HOLD signal."""

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt
)


def analyze_company(company_name: str, ticker: str):
    print(f'\n{"="*60}')
    print(f'AGENT ANALYZING: {company_name} ({ticker})')
    print(f'{"="*60}\n')

    result = agent.invoke({
        "messages": [
            ("human", f"Analyze {company_name} with ticker {ticker}. Fetch the latest news, get the current stock price, search memory for any relevant past context, and generate a full market intelligence report with a BUY, SELL, or HOLD signal.")
        ]
    })

    final_answer = result['messages'][-1].content

    print(f'\n{"="*60}')
    print('FINAL REPORT:')
    print(f'{"="*60}')
    print(final_answer)
    return final_answer


if __name__ == "__main__":
    analyze_company("Apple", "AAPL")
