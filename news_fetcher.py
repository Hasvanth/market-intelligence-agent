import os
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()

def get_news(company_name, num_articles=10):

    newsapi =  NewsApiClient(api_key = os.getenv("NEWS_API_KEY"))

    response = newsapi.get_everything(

        q=f'"{company_name}" stock OR shares OR earnings OR market',
        language='en',
        sort_by='publishedAt',
        page_size=num_articles

    )

    articles = []

    for article in response['articles']:
        articles.append({

            'title': article['title'],
            'source': article['source']['name'],
            'date': article['publishedAt'],
            'description': article['description'],
            'url': article['url']

        })

    return articles
    
if __name__ == "__main__":
    print("Fetching news for Apple...\n")
    articles = get_news("Apple", num_articles=5)

    for i, article in enumerate(articles):
        print(f"Article {i+1}:")
        print(f"  Title:  {article['title']}")
        print(f"  Source: {article['source']}")
        print(f"  Date:   {article['date']}")
        print(f"  URL:    {article['url']}")
        print()


