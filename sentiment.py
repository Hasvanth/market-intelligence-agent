from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from news_fetcher import get_news

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> dict:

    
    scores = analyzer.polarity_scores(text)

    compound = scores['compound']

    if compound >= 0.05:
        signal = "BULLISH"
    elif compound <= -0.05:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    return {
        "text":    text,
        "score":   compound,
        "signal":  signal,
        "details": scores
    }

def analyze_company_sentiment(company_name: str) -> dict:


    articles = get_news(company_name, num_articles=10)

    results = []
    total_score = 0

    for article in articles:
        text = f"{article['title']}. {article['description']}"

        # Skip empty articles
        if not text or text == 'None. None':
            continue

        # Analyze this article
        sentiment = analyze_sentiment(text)
        sentiment['title']  = article['title']
        sentiment['source'] = article['source']
        sentiment['date']   = article['date']

        results.append(sentiment)
        total_score += sentiment['score']

    # Calculate average score across all articles
    avg_score = total_score / len(results) if results else 0

    # Overall company signal
    if avg_score >= 0.05:
        overall_signal = "BULLISH 📈"
    elif avg_score <= -0.05:
        overall_signal = "BEARISH 📉"
    else:
        overall_signal = "NEUTRAL ➡️"

    return {
        "company":        company_name,
        "overall_score":  round(avg_score, 4),
        "overall_signal": overall_signal,
        "total_articles": len(results),
        "articles":       results
    }


#TEST BLOCK

if __name__ == "__main__":

    # Test 1 — single sentence
    print("=== TEST 1: Single Sentence ===")
    test1 = analyze_sentiment("Apple reports record breaking revenue and profits")
    print(f"Text:   {test1['text']}")
    print(f"Score:  {test1['score']}")
    print(f"Signal: {test1['signal']}")
    print()

    test2 = analyze_sentiment("Apple CEO resigns amid fraud investigation")
    print(f"Text:   {test2['text']}")
    print(f"Score:  {test2['score']}")
    print(f"Signal: {test2['signal']}")
    print()

    # Test 2 — full company analysis
    print("=== TEST 2: Full Company Analysis ===")
    result = analyze_company_sentiment("Apple")
    print(f"Company:           {result['company']}")
    print(f"Overall Score:     {result['overall_score']}")
    print(f"Overall Signal:    {result['overall_signal']}")
    print(f"Articles Analyzed: {result['total_articles']}")
    print()
    print('Individual Article Scores:')
    for article in result['articles'][:5]:
        print(f"  {article['signal']:8} | {article['score']:6.3f} | {article['title'][:60]}")


