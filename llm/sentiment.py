import logging
import requests
import json
from typing import Optional, List
from utils.config import OPENROUTER_API_KEY, LLM_MODEL, LLM_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Handles sentiment analysis using OpenRouter API."""
    
    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        """
        Initialize sentiment analyzer.
        
        Args:
            api_key (str): OpenRouter API key (optional - will use demo mode if missing)
            
        Raises:
            ValueError: If API key is not provided
        """
        if not api_key:
            logger.warning("OpenRouter API key not provided - using demo mode for sentiment analysis")
            self.api_key = None
            self.demo_mode = True
        else:
            self.api_key = api_key
            self.demo_mode = False
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = LLM_MODEL
        if self.demo_mode:
            logger.info("SentimentAnalyzer initialized in DEMO MODE")
        else:
            logger.info(f"SentimentAnalyzer initialized with model: {self.model}")
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of given text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Contains 'sentiment' (positive/negative/neutral), 'confidence' (0-1), 'summary'
            
        Raises:
            Exception: If API call fails
        """
        if not text or not isinstance(text, str):
            logger.error("Invalid text input for sentiment analysis")
            raise ValueError("Text must be a non-empty string")
        
        # If in demo mode, return synthetic sentiment
        if self.demo_mode:
            return self._generate_demo_sentiment(text)
        
        # Truncate to reasonable length
        text = text[:2000]
        
        prompt = f"""Analyze the sentiment of this text and respond with ONLY a JSON object:
{{
    "sentiment": "positive" or "negative" or "neutral",
    "confidence": 0.0 to 1.0,
    "summary": "brief summary of why"
}}

Text: {text}"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Sentiment analysis attempt {attempt + 1} for text: {text[:50]}...")
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=LLM_TIMEOUT
                )
                
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" not in result or not result["choices"]:
                    logger.error("No choices in API response")
                    raise ValueError("Invalid API response format")
                
                content = result["choices"][0]["message"]["content"].strip()
                
                # Parse JSON response
                try:
                    sentiment_data = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON response: {content}")
                    # Fallback parsing
                    sentiment_data = self._parse_sentiment_fallback(content)
                
                logger.info(f"Sentiment analysis result: {sentiment_data}")
                return sentiment_data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < MAX_RETRIES - 1:
                    continue
                logger.warning("Falling back to demo sentiment after timeout")
                return self._generate_demo_sentiment(text)
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    continue
                logger.warning("Falling back to demo sentiment after request error")
                return self._generate_demo_sentiment(text)
            except Exception as e:
                logger.error(f"Sentiment analysis failed on attempt {attempt + 1}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    continue
                logger.warning("Falling back to demo sentiment after error")
                return self._generate_demo_sentiment(text)
        
        logger.warning("Max retries exceeded, using demo sentiment")
        return self._generate_demo_sentiment(text)
    
    def _parse_sentiment_fallback(self, content: str) -> dict:
        """
        Fallback parser if JSON parsing fails.
        
        Args:
            content (str): Response content
            
        Returns:
            dict: Parsed sentiment data
        """
        content_lower = content.lower()
        
        if "positive" in content_lower:
            sentiment = "positive"
        elif "negative" in content_lower:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "confidence": 0.5,
            "summary": content[:100]
        }
    
    def _generate_demo_sentiment(self, text: str) -> dict:
        """
        Generate synthetic sentiment for demo mode.
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Demo sentiment data
        """
        # Simple keyword-based demo sentiment
        text_lower = text.lower()
        positive_words = ["strong", "good", "bullish", "up", "gain", "growth", "positive"]
        negative_words = ["weak", "bad", "bearish", "down", "loss", "decline", "negative"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (pos_count * 0.1))
        elif neg_count > pos_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (neg_count * 0.1))
        else:
            sentiment = "neutral"
            confidence = 0.6
        
        return {
            "sentiment": sentiment,
            "confidence": min(0.95, confidence),
            "summary": f"Demo analysis: {text[:80]}"
        }
    
    def analyze_batch(self, texts: list) -> list:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts (list): List of texts to analyze
            
        Returns:
            list: List of sentiment results
        """
        results = []
        for text in texts:
            try:
                result = self.analyze_sentiment(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze text: {str(e)}")
                results.append({
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "summary": "Error during analysis"
                })
        
        return results


# Singleton instance
_analyzer = None


def analyze_sentiment(text: str) -> dict:
    """
    Convenience function to analyze sentiment.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Sentiment analysis result
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    
    return _analyzer.analyze_sentiment(text)


def analyze_batch(texts: list) -> list:
    """
    Convenience function to analyze multiple texts.
    
    Args:
        texts (list): List of texts
        
    Returns:
        list: List of results
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    
    return _analyzer.analyze_batch(texts)