import logging
from typing import List
from apify_client import ApifyClient
from utils.config import APIFY_API_KEY, TWEET_SEARCH_LIMIT

logger = logging.getLogger(__name__)


class TwitterScraper:
    """Handles Twitter scraping using Apify API."""
    
    def __init__(self, api_key: str = APIFY_API_KEY):
        """
        Initialize Twitter scraper.
        
        Args:
            api_key (str): Apify API key (optional - will use demo mode if missing)
            
        Raises:
            ValueError: If API key is not provided
        """
        if not api_key:
            logger.warning("Apify API key not provided - using demo mode for Twitter scraping")
            self.client = None
            self.demo_mode = True
        else:
            self.client = ApifyClient(api_key)
            self.demo_mode = False
        
        if self.demo_mode:
            logger.info("TwitterScraper initialized in DEMO MODE")
        else:
            logger.info("TwitterScraper initialized with Apify")
    
    def get_tweets(self, search_terms: List[str], max_tweets: int = TWEET_SEARCH_LIMIT) -> List[dict]:
        """
        Fetch tweets for given search terms.
        
        Args:
            search_terms (List[str]): List of tickers to search (e.g., ["AAPL", "MSFT"])
            max_tweets (int): Maximum tweets to fetch per term
            
        Returns:
            List[dict]: List of tweets with text and metadata
            
        Raises:
            Exception: If scraping fails
        """
        try:
            if not search_terms:
                logger.warning("No search terms provided")
                return []
            
            # If in demo mode, return synthetic tweets
            if self.demo_mode:
                return self._generate_demo_tweets(search_terms, max_tweets)
            
            logger.info(f"Scraping tweets for: {search_terms}")
            
            tweets = []
            
            for term in search_terms:
                try:
                    run_input = {
                        "searchTerms": [term],
                        "maxTweets": max_tweets,
                        "sort": "Latest"
                    }
                    
                    logger.info(f"Starting Apify run for term: {term}")
                    run = self.client.actor("apify/twitter-scraper").call(
                        run_input=run_input,
                        timeout_secs=600
                    )
                    
                    dataset_id = run.get("defaultDatasetId")
                    if not dataset_id:
                        logger.warning(f"No dataset returned for term: {term}")
                        continue
                    
                    # Retrieve tweets from dataset
                    for item in self.client.dataset(dataset_id).iterate_items():
                        tweet_data = {
                            "text": item.get("text", ""),
                            "author": item.get("author", ""),
                            "likes": item.get("likeCount", 0),
                            "retweets": item.get("retweetCount", 0),
                            "created_at": item.get("createdAt", ""),
                            "search_term": term
                        }
                        tweets.append(tweet_data)
                    
                    logger.info(f"Successfully fetched {len(tweets)} tweets for {term}")
                    
                except Exception as e:
                    logger.error(f"Failed to fetch tweets for term {term}: {str(e)}")
                    continue
            
            logger.info(f"Total tweets fetched: {len(tweets)}")
            
            # If no tweets were fetched, use demo mode as fallback
            if not tweets:
                logger.warning("No tweets fetched from API - falling back to demo tweets")
                return self._generate_demo_tweets(search_terms, max_tweets)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Twitter scraping failed: {str(e)}")
            logger.warning("Falling back to demo tweets")
            return self._generate_demo_tweets(search_terms, max_tweets)
    
    def _generate_demo_tweets(self, search_terms: List[str], max_tweets: int) -> List[dict]:
        """Generate synthetic demo tweets for testing."""
        demo_tweets = {
            "AAPL": [
                "Apple reports strong Q4 earnings with record iPhone sales",
                "AAPL stock surges on positive analyst recommendations",
                "Apple's new AI features driving bullish sentiment",
                "Institutional investors increase AAPL position",
            ],
            "MSFT": [
                "Microsoft Cloud revenue continues to grow impressively",
                "MSFT announces major AI partnership expansion",
                "Positive outlook for Microsoft enterprise segment",
                "Azure services demand exceeds expectations",
            ],
            "GOOGL": [
                "Google's search business remains strong",
                "GOOGL advances in AI and machine learning",
                "Alphabet reports solid quarterly results",
                "YouTube advertising revenue shows growth",
            ],
            "AMZN": [
                "Amazon Web Services expanding market share",
                "AMZN logistics network efficiency improves",
                "AWS profitability increases substantially",
                "Amazon announces new retail initiatives",
            ],
            "TSLA": [
                "Tesla production targets on track",
                "TSLA stock momentum continues",
                "Electric vehicle market expansion positive",
                "Tesla energy business accelerating",
            ],
        }
        
        tweets = []
        for term in search_terms:
            term_tweets = demo_tweets.get(term, [
                f"{term} stock showing positive momentum",
                f"Investors bullish on {term}",
                f"{term} reports strong fundamentals",
            ])
            
            for i, text in enumerate(term_tweets[:max_tweets]):
                tweets.append({
                    "text": text,
                    "author": f"demo_user_{i}",
                    "likes": 100 + (i * 10),
                    "retweets": 50 + (i * 5),
                    "created_at": "2024-04-05T12:00:00",
                    "search_term": term
                })
        
        logger.info(f"Generated {len(tweets)} demo tweets")
        return tweets


# Singleton instance
_scraper = None


def get_tweets(tickers: List[str], max_tweets: int = TWEET_SEARCH_LIMIT) -> List[dict]:
    """
    Convenience function to get tweets.
    
    Args:
        tickers (List[str]): List of stock tickers
        max_tweets (int): Maximum tweets per ticker
        
    Returns:
        List[dict]: List of tweet objects
    """
    global _scraper
    if _scraper is None:
        _scraper = TwitterScraper()
    
    return _scraper.get_tweets(tickers, max_tweets)