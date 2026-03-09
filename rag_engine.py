import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from news_fetcher import get_news

load_dotenv()

client = chromadb.PersistentClient (path="./chroma_db")

#embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
#    api_key = os.getenv("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"),
#    model_name = "text-embedding-3-small"
#)

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

embedding_fn = DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name = "market_news",
    embedding_function=embedding_fn
)


def store_news(company_name):

    print(f'Fetching and storing news for {company_name}...')

    articles = get_news(company_name, num_articles=10)

    for i, article in enumerate(articles):
        
        text = f"{article['title']}. {article['description']}"

        if not text or text == 'None. None':
            continue

        doc_id = f"{company_name}_{i}_{article['date']}"

        collection.upsert(
            documents=[text],
            ids=[doc_id],
            metadatas=[{
                'company': company_name,
                'title':   article['title'],
                'source':  article['source'],
                'date':    article['date'],
                'url':     article['url']
            }]
        )
    print(f'Stored {len(articles)} articles for {company_name}')


def search_news(query, company_name = None, num_results=5):

    print(f"Searching memory for: '{query}'")

    where_filter = {'company': company_name} if company_name else None

    results = collection.query(
        query_texts=[query],
        n_results=num_results,
        where=where_filter
    )

    articles = []
    if results['documents'][0]:
        for j in range(len(results['documents'][0])):
            articles.append({
                'text':            results['documents'][0][j],
                'metadata':        results['metadatas'][0][j],
                'relevance_score': results['distances'][0][j]
            })

    return articles

if __name__ == "__main__":

    print("=== TEST 1: Storing News ===")
    store_news("Apple")
    print()

    print("=== TEST 2: Searching Memory ===")
    results = search_news(
        query='What risks is Apple facing?',
        company_name='Apple',
        num_results=3
    )

    for i, result in enumerate(results):
        print(f'\nResult {i+1}:')
        print(f"  Title:  {result['metadata']['title']}")
        print(f"  Source: {result['metadata']['source']}")
        print(f"  Date:   {result['metadata']['date']}")







