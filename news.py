# Gets recent news headlines for a stock symbol from the Finnhub API
import requests
from datetime import date, timedelta
from finnhub_key import FINNHUB_API_KEY

FINNHUB_URL = "https://finnhub.io/api/v1/company-news"

# function to get a few recent news articles for one stock symbol
def get_news_for_symbol(symbol, days=7, limit=4):
    to_date = date.today()
    from_date = to_date - timedelta(days=days)

    params = {
        "symbol": symbol,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "token": FINNHUB_API_KEY,
    }

    try:
        response = requests.get(FINNHUB_URL, params=params, timeout=5)
        articles = response.json()
    except requests.RequestException:
        return []
     # to fix Finnhub sends back an error message instead of a list 
    if not isinstance(articles, list):
        return [] 

    news = []
    for article in articles[:limit]:
        news.append({
            "headline": article.get("headline"),
            "source": article.get("source"),
            "url": article.get("url"),
        })
    return news
