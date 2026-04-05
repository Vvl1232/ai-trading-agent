#!/usr/bin/env python3
"""
Trading AI Agent - Main Entry Point

Complete pipeline:
1. Fetch insider trading data from SEC
2. Extract top 5 stock tickers
3. Scrape tweets for sentiment analysis
4. Analyze sentiment using LLM
5. Create vector embeddings and RAG context
6. Generate trading signals
7. Record agent learning
8. Generate visualizations and reports
"""

import logging
import sys
import os
from datetime import datetime
import json

# Create outputs directory
os.makedirs("outputs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main execution pipeline."""
    try:
        logger.info("=" * 80)
        logger.info("TRADING AI AGENT - PIPELINE START")
        logger.info("=" * 80)
        
        # Import modules
        try:
            from data.sec_fetch import get_sec_data, get_top5_trades
            from apify.twitter_scraper import get_tweets
            from rag.vector_store import chunk_data, create_vector_store, get_context
            from llm.sentiment import analyze_sentiment, analyze_batch
            from agents.trading_agent import agent, analyze_sentiment_signal, learn
            from utils.charts import plot_sentiment, create_report
            from utils.config import (
                OPENROUTER_API_KEY, APIFY_API_KEY, SEC_API_KEY,
                TWEET_SEARCH_LIMIT
            )
            logger.info("✓ All modules imported successfully")
        except ImportError as e:
            logger.error(f"✗ Failed to import modules: {str(e)}")
            logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
            return False
        
        # Step 1: Validate API keys
        logger.info("\nStep 1: Validating API credentials...")
        api_status = {
            "SEC_API": bool(SEC_API_KEY),
            "APIFY_API": bool(APIFY_API_KEY),
            "OPENROUTER_API": bool(OPENROUTER_API_KEY)
        }
        
        missing_keys = [k for k, v in api_status.items() if not v]
        if missing_keys:
            logger.warning(f"⚠ Missing API keys: {', '.join(missing_keys)}")
            logger.info("Continuing with demo/fallback mode...")
        else:
            logger.info("✓ All API credentials validated")
        
        # Step 2: Fetch SEC data
        logger.info("\nStep 2: Fetching SEC insider trading data...")
        sec_data = {}
        try:
            sec_data = get_sec_data()
            trade_count = len(sec_data.get('data', []))
            logger.info(f"✓ Retrieved SEC data: {trade_count} trades")
        except Exception as e:
            logger.warning(f"⚠ Failed to fetch SEC data: {str(e)}")
            logger.info("Continuing with demo tickers...")
            sec_data = {}
        
        # Step 3: Extract top 5 trades
        logger.info("\nStep 3: Extracting top 5 trades...")
        tickers = []
        try:
            if sec_data:
                top5_df = get_top5_trades(sec_data)
                if not top5_df.empty:
                    tickers = top5_df["issuerTradingSymbol"].tolist()
                    logger.info(f"✓ Top tickers identified: {tickers}")
            
            if not tickers:
                logger.info("Using demo tickers for testing...")
                tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        except Exception as e:
            logger.warning(f"⚠ Failed to extract top 5: {str(e)}")
            logger.info("Using demo tickers for testing...")
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        
        logger.info(f"✓ Analyzing tickers: {', '.join(tickers)}")
        
        # Step 4: Scrape tweets
        logger.info(f"\nStep 4: Scraping tweets for {len(tickers)} tickers...")
        tweets_data = []
        try:
            tweets_data = get_tweets(tickers, max_tweets=TWEET_SEARCH_LIMIT)
            logger.info(f"✓ Fetched {len(tweets_data)} tweets")
        except Exception as e:
            logger.warning(f"⚠ Twitter scraping encountered error: {str(e)}")
            logger.info("Using demo tweet data...")
            tweets_data = [
                {
                    "text": f"Positive market sentiment for {ticker}",
                    "author": "demo_trading_bot",
                    "search_term": ticker
                }
                for ticker in tickers
            ]
        
        # Verify we have data
        if not tweets_data:
            logger.error("✗ No tweet data available")
            logger.info("Cannot proceed without data")
            return False
        
        logger.info(f"✓ Working with {len(tweets_data)} data points")
        
        # Step 5: Chunk data for RAG
        logger.info(f"\nStep 5: Chunking {len(tweets_data)} items for RAG...")
        try:
            tweet_texts = [t.get("text", "") if isinstance(t, dict) else str(t) for t in tweets_data]
            tweet_texts = [t for t in tweet_texts if t.strip()]
            
            if not tweet_texts:
                raise ValueError("No valid text content to chunk")
            
            chunks = chunk_data(tweet_texts)
            logger.info(f"✓ Created {len(chunks)} chunks (size=500, overlap=50)")
        except Exception as e:
            logger.error(f"✗ Chunking failed: {str(e)}")
            logger.info("Cannot proceed without chunked data")
            return False
        
        # Step 6: Create vector store
        logger.info("\nStep 6: Creating FAISS vector store...")
        vector_store = None
        try:
            vector_store = create_vector_store(chunks)
            logger.info("✓ Vector store initialized with embeddings")
        except Exception as e:
            logger.error(f"✗ Vector store creation failed: {str(e)}")
            logger.info("Proceeding without RAG context...")
        
        # Step 7: Analyze sentiment and generate signals
        logger.info("\nStep 7: Analyzing sentiment and generating signals...")
        
        trading_signals = []
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for idx, ticker in enumerate(tickers, 1):
            try:
                logger.info(f"  [{idx}/{len(tickers)}] Analyzing: {ticker}")
                
                # Get ticker-specific tweets
                ticker_tweets = [t.get("text", "") for t in tweets_data 
                               if isinstance(t, dict) and t.get("search_term") == ticker]
                
                if not ticker_tweets:
                    ticker_tweets = [f"Stock {ticker} market sentiment"]
                
                # Prepare text for analysis
                ticker_text = " ".join(ticker_tweets[:5])  # Use first 5 tweets
                if not ticker_text.strip():
                    ticker_text = f"Analysis of {ticker}"
                
                # Analyze sentiment
                try:
                    sentiment_result = analyze_sentiment(ticker_text)
                except Exception as e:
                    logger.warning(f"    Sentiment analysis failed for {ticker}: {str(e)}")
                    sentiment_result = {
                        "sentiment": "neutral",
                        "confidence": 0.5,
                        "summary": "Analysis unavailable"
                    }
                
                # Get RAG context
                rag_context = "No context available"
                if vector_store:
                    try:
                        rag_context = get_context(f"stock {ticker} performance", k=3)
                    except Exception as e:
                        logger.warning(f"    RAG context retrieval failed: {str(e)}")
                
                # Generate trading signal
                try:
                    signal = analyze_sentiment_signal(ticker, sentiment_result, rag_context)
                    trading_signals.append(signal)
                    
                    # Update sentiment counts
                    sentiment = sentiment_result.get("sentiment", "neutral")
                    if sentiment in sentiment_counts:
                        sentiment_counts[sentiment] += 1
                    
                    confidence = sentiment_result.get("confidence", 0)
                    logger.info(f"    ✓ {ticker}: {sentiment.upper()} (confidence: {confidence:.2f})")
                    logger.info(f"      Recommendation: {signal['recommendation']}")
                except Exception as e:
                    logger.error(f"    ✗ Signal generation failed for {ticker}: {str(e)}")
                    continue
                
            except Exception as e:
                logger.error(f"  ✗ Processing failed for {ticker}: {str(e)}")
                continue
        
        if not trading_signals:
            logger.error("✗ No trading signals generated")
            return False
        
        logger.info(f"\n✓ Generated {len(trading_signals)} trading signals")
        logger.info(f"  Sentiment Distribution: Positive={sentiment_counts['positive']}, "
                   f"Negative={sentiment_counts['negative']}, Neutral={sentiment_counts['neutral']}")
        
        # Step 8: Record learning
        logger.info("\nStep 8: Recording agent learning...")
        try:
            for idx, signal in enumerate(trading_signals, 1):
                try:
                    learn(
                        query=f"Analyze sentiment for {signal['ticker']}",
                        response=json.dumps(signal),
                        feedback=None
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning for signal {idx}: {str(e)}")
            
            memory_summary = agent.get_memory_summary()
            logger.info(f"✓ Agent memory updated: {memory_summary['total_entries']} entries")
        except Exception as e:
            logger.warning(f"⚠ Failed to update agent memory: {str(e)}")
        
        # Step 9: Generate visualizations
        logger.info("\nStep 9: Generating visualizations...")
        chart_path = None
        try:
            chart_path = plot_sentiment(
                sentiment_counts["positive"],
                sentiment_counts["negative"],
                sentiment_counts["neutral"],
                output_dir="outputs"
            )
            logger.info(f"✓ Sentiment chart saved: {chart_path}")
        except Exception as e:
            logger.warning(f"⚠ Chart generation failed: {str(e)}")
        
        # Step 10: Create report
        logger.info("\nStep 10: Creating analysis report...")
        report_path = None
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "tickers_analyzed": tickers,
                "total_items_processed": len(tweets_data),
                "total_chunks": len(chunks) if chunks else 0,
                "sentiment_distribution": sentiment_counts,
                "trading_signals": trading_signals,
                "agent_memory": agent.get_memory_summary(),
                "execution_metadata": {
                    "api_status": api_status,
                    "vector_store_created": vector_store is not None,
                    "chart_generated": chart_path is not None
                }
            }
            
            report_path = create_report(report_data, output_dir="outputs")
            logger.info(f"✓ Report saved: {report_path}")
        except Exception as e:
            logger.warning(f"⚠ Report generation failed: {str(e)}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Tickers Analyzed: {', '.join(tickers)}")
        logger.info(f"Total Items Processed: {len(tweets_data)}")
        logger.info(f"Total Chunks Created: {len(chunks) if chunks else 0}")
        logger.info(f"Trading Signals Generated: {len(trading_signals)}")
        logger.info(f"Sentiment Distribution:")
        logger.info(f"  - Positive: {sentiment_counts['positive']}")
        logger.info(f"  - Negative: {sentiment_counts['negative']}")
        logger.info(f"  - Neutral: {sentiment_counts['neutral']}")
        
        if trading_signals:
            logger.info("\nTop Trading Signals (by confidence):")
            sorted_signals = sorted(trading_signals, 
                                   key=lambda x: x.get('confidence', 0), 
                                   reverse=True)
            for signal in sorted_signals[:3]:
                ticker = signal.get('ticker', 'N/A')
                recommendation = signal.get('recommendation', 'N/A')
                confidence = signal.get('confidence', 0)
                logger.info(f"  {ticker}: {recommendation} (confidence: {confidence:.2f})")
        
        logger.info("\nOutput Files:")
        if chart_path:
            logger.info(f"  - Chart: {chart_path}")
        if report_path:
            logger.info(f"  - Report: {report_path}")
        logger.info(f"  - Log: trading_agent.log")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        return True
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 80)
        logger.info("⚠ Pipeline interrupted by user")
        logger.info("=" * 80)
        return False
    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error("✗ CRITICAL ERROR - PIPELINE FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)