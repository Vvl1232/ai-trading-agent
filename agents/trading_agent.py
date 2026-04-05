import logging
import json
from typing import Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TradingAgent:
    """
    Main trading agent that orchestrates data collection, analysis, and recommendations.
    Implements learning loop for continuous improvement.
    """
    
    def __init__(self, name: str = "TradingAgent", description: str = "SEC + Twitter Sentiment Analyzer"):
        """
        Initialize trading agent.
        
        Args:
            name (str): Agent name
            description (str): Agent description
        """
        self.name = name
        self.description = description
        self.memory = []  # Learning memory
        logger.info(f"Initialized {name}: {description}")
    
    def analyze_sentiment_signal(self, ticker: str, sentiment_data: dict, context: str) -> dict:
        """
        Analyze trading signal based on sentiment and context.
        
        Args:
            ticker (str): Stock ticker
            sentiment_data (dict): Sentiment analysis result
            context (str): RAG-retrieved context
            
        Returns:
            dict: Trading signal and recommendation
        """
        try:
            sentiment = sentiment_data.get("sentiment", "neutral")
            confidence = sentiment_data.get("confidence", 0.5)
            
            logger.info(f"Analyzing signal for {ticker}: sentiment={sentiment}, confidence={confidence}")
            
            # Generate trading signal
            signal = {
                "ticker": ticker,
                "sentiment": sentiment,
                "confidence": confidence,
                "recommendation": self._generate_recommendation(sentiment, confidence),
                "context": context[:500],  # Truncate context for readability
                "metadata": {
                    "agent": self.name,
                    "model": "hermes-reasoning"
                }
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment signal for {ticker}: {str(e)}")
            raise
    
    def _generate_recommendation(self, sentiment: str, confidence: float) -> str:
        """
        Generate trading recommendation based on sentiment.
        
        Args:
            sentiment (str): Sentiment classification
            confidence (float): Confidence score
            
        Returns:
            str: Trading recommendation
        """
        if confidence < 0.5:
            return "HOLD - Low confidence signal"
        
        if sentiment == "positive":
            if confidence >= 0.8:
                return "BUY - Strong positive sentiment"
            else:
                return "BUY - Positive sentiment"
        elif sentiment == "negative":
            if confidence >= 0.8:
                return "SELL - Strong negative sentiment"
            else:
                return "SELL - Negative sentiment"
        else:
            return "HOLD - Neutral sentiment"
    
    def learn(self, query: str, response: str, feedback: str = None) -> None:
        """
        Learning loop for agent improvement.
        
        Args:
            query (str): Original query/analysis
            response (str): Agent response
            feedback (str): Optional feedback for improvement
        """
        try:
            learning_entry = {
                "query": query,
                "response": response,
                "feedback": feedback,
                "timestamp": self._get_timestamp()
            }
            
            self.memory.append(learning_entry)
            logger.info(f"Agent learned from query: {query[:50]}...")
            
            # Optional: Log memory size
            if len(self.memory) % 10 == 0:
                logger.info(f"Agent memory size: {len(self.memory)} entries")
            
        except Exception as e:
            logger.error(f"Failed to record learning: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().isoformat()
    
    def get_memory_summary(self) -> dict:
        """
        Get summary of agent memory.
        
        Returns:
            dict: Memory statistics
        """
        return {
            "total_entries": len(self.memory),
            "agent_name": self.name,
            "latest_entry": self.memory[-1] if self.memory else None
        }
    
    def reset_memory(self) -> None:
        """Reset agent memory."""
        self.memory = []
        logger.info("Agent memory reset")


# Global agent instance
_agent = None


def get_agent() -> TradingAgent:
    """Get or create global agent instance."""
    global _agent
    if _agent is None:
        _agent = TradingAgent()
    return _agent


# Convenience functions
agent = get_agent()


def analyze_sentiment_signal(ticker: str, sentiment_data: dict, context: str) -> dict:
    """Analyze sentiment signal."""
    return agent.analyze_sentiment_signal(ticker, sentiment_data, context)


def learn(query: str, response: str, feedback: str = None) -> None:
    """Record learning."""
    agent.learn(query, response, feedback)