# Trading AI Agent

An intelligent, production-grade AI-powered trading agent that analyzes insider trading data, social media sentiment, and financial news to generate actionable trading signals.

## 🎯 Overview

The Trading AI Agent implements a complete end-to-end pipeline:

```
SEC API → Top 5 Trades → Twitter Scraping → Sentiment Analysis → 
RAG Vector Store → Trading Signals → Agent Learning → Reports & Charts
```

**Key Features:**
- ✅ Insider trading data from SEC API
- ✅ Real-time Twitter sentiment analysis
- ✅ LLM-powered sentiment classification (Mistral 7B via OpenRouter)
- ✅ RAG (Retrieval Augmented Generation) with FAISS vector store
- ✅ Intelligent agent with learning loop
- ✅ Comprehensive error handling & logging
- ✅ Automated chart generation and reporting
- ✅ Production-ready code quality

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   TRADING AI AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DATA SOURCES        │  PROCESSING           │  OUTPUT      │
│  ────────────────    │  ────────────────     │  ─────────   │
│                      │                       │              │
│  SEC API             │  Sentiment Analysis   │  Signals     │
│  ↓                   │  ↓                     │  ↓           │
│  Top 5 Trades ────→  │  LLM Processing       │  Reports     │
│                      │  ↓                     │  ↓           │
│  Twitter API         │  RAG Context          │  Charts      │
│  ↓                   │  ↓                     │  ↓           │
│  Tweets ──────────→  │  FAISS Index          │  Memory      │
│                      │  ↓                     │  ↓           │
│  News/Context        │  Similarity Search    │  Actions     │
│                      │  ↓                     │              │
│                      │  Agent Learning       │              │
│                      │                       │              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
trading-ai-agent/
│
├── agents/
│   └── trading_agent.py       # Core agent with learning loop
│
├── data/
│   └── sec_fetch.py           # SEC insider trading data
│
├── apify/
│   └── twitter_scraper.py     # Twitter data collection
│
├── llm/
│   └── sentiment.py           # Sentiment analysis via OpenRouter
│
├── rag/
│   └── vector_store.py        # FAISS embeddings & retrieval
│
├── utils/
│   ├── config.py              # Configuration & constants
│   └── charts.py              # Visualization & reporting
│
├── main.py                    # Pipeline orchestration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── README.md                 # This file
├── TESTING_INSTRUCTIONS.md   # Complete testing guide
└── trading_agent.log         # Runtime logs
```

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd trading-ai-agent
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure API Keys
Edit `.env` with your credentials:
```
SEC_API_KEY=your_sec_key
APIFY_API_KEY=your_apify_key
OPENROUTER_API_KEY=your_openrouter_key
```

### 3. Run Pipeline
```bash
python main.py
```

**Output:**
- `trading_agent.log` - Detailed execution logs
- `outputs/sentiment.png` - Sentiment distribution chart
- `outputs/report_*.json` - Trading analysis report

## 📊 Module Details

### agents/trading_agent.py
Implements the core trading agent with:
- **Signal Generation**: Creates actionable trading recommendations
- **Learning Loop**: Records decisions for continuous improvement  
- **Confidence Scoring**: Validates signal reliability
- **Recommendation Engine**: BUY/SELL/HOLD decisions

### data/sec_fetch.py
Integrates with SEC API:
- Fetches insider trading transactions
- Extracts top 5 trades by activity
- Validates data integrity
- Handles rate limiting gracefully

### apify/twitter_scraper.py
Social media data collection:
- Scrapes tweets for target tickers
- Extracts sentiment signals
- Thread-safe with proper error handling
- Respects API rate limits

### llm/sentiment.py
LLM-based sentiment analysis:
- Uses Mistral-7B via OpenRouter
- Returns: sentiment (pos/neg/neutral) + confidence
- Fallback parsing for robust JSON extraction
- Retry logic with exponential backoff

### rag/vector_store.py
Retrieval-Augmented Generation:
- **Chunking**: 500 token chunks with 50 overlap
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Indexing**: FAISS for fast similarity search
- **Context Retrieval**: Top-K documents for augmentation

### utils/charts.py
Visualization & Reporting:
- **Sentiment Charts**: Bar plots of classification results
- **Timeline Charts**: Sentiment progression over time
- **JSON Reports**: Structured trading analysis data
- **High-DPI Output**: Production-quality 300 DPI images

## 🔑 API Keys Required

| Service | Purpose | Cost | Get Key |
|---------|---------|------|---------|
| SEC API | Insider trading data | Free | [sec-api.com](https://sec-api.com/) |
| Apify | Twitter scraping | Free ($25 credit) | [apify.com](https://apify.com/) |
| OpenRouter | LLM inference | Pay-as-you-go | [openrouter.ai](https://openrouter.ai/) |

## 📝 Configuration

All settings in `utils/config.py`:

```python
# Data ranges
SEC_QUERY_RANGE = "NOW-7DAYS"        # Lookback window
TWEET_SEARCH_LIMIT = 100              # Tweets per ticker

# RAG settings  
CHUNK_SIZE = 500                      # Document chunk size
CHUNK_OVERLAP = 50                    # Overlap between chunks
SIMILARITY_THRESHOLD = 0.5            # Minimum relevance score

# LLM settings
LLM_MODEL = "mistralai/mistral-7b-instruct"
LLM_TIMEOUT = 30                      # API timeout (seconds)
MAX_RETRIES = 3                       # Retry attempts
```

## 🔍 Pipeline Execution

### Step-by-Step Flow

1. **Validation**: Verify all API keys exist
2. **SEC Data**: Fetch insider trading transactions
3. **Top 5 Tickers**: Extract most active stocks
4. **Tweet Collection**: Scrape sentiment indicators
5. **Data Chunking**: Prepare text for embeddings
6. **Vector Store**: Create FAISS index
7. **Sentiment Analysis**: LLM classification per ticker
8. **RAG Context**: Retrieve relevant background
9. **Signal Generation**: Create trading recommendations
10. **Agent Learning**: Record decisions in memory
11. **Visualization**: Generate charts and reports

### Error Handling

The pipeline is resilient to API failures:

```
SEC API Down?      → Use demo tickers
Twitter Limited?   → Fallback to synthetic data
LLM Timeout?       → Use neutral sentiment
FAISS Error?       → Skip RAG context
```

All failures are logged but don't crash the pipeline.

## 📈 Performance

| Task | Time | Bottleneck |
|------|------|-----------|
| Initialization | 2-5 sec | Embeddings model load |
| SEC API | 2-3 sec | Network I/O |
| Apify Scraping | 30-60 sec | Actor processing |
| LLM Inference | 5-10 sec/ticker | API latency |
| FAISS Indexing | 5-15 sec | Embedding computation |
| **Total Pipeline** | **3-5 min** | Apify scraping |
| **Demo Mode** | **30-45 sec** | No APIs |

## 🧪 Testing

See `TESTING_INSTRUCTIONS.md` for:
- Module-level unit tests
- API integration tests
- Full pipeline validation
- Troubleshooting guide
- CI/CD integration examples

Quick test:
```bash
python -c "from agents.trading_agent import agent; print('✓ Agent initialized')"
```

## 📊 Output Examples

### Trading Signal
```json
{
  "ticker": "AAPL",
  "sentiment": "positive",
  "confidence": 0.87,
  "recommendation": "BUY - Strong positive sentiment",
  "context": "Apple shows strong market momentum...",
  "metadata": {
    "agent": "TradingAgent",
    "model": "hermes-reasoning"
  }
}
```

### Sentiment Distribution Chart
```
Sentiment Analysis Results

Positive  Negative  Neutral
   ████✓      ██✓      ████✓
    3         1        2

(Saved as: outputs/sentiment.png)
```

### Full Report
```json
{
  "timestamp": "2024-04-05T14:30:22",
  "tickers_analyzed": ["AAPL", "MSFT", "GOOGL"],
  "total_tweets": 234,
  "sentiment_distribution": {
    "positive": 3,
    "negative": 1,
    "neutral": 1
  },
  "trading_signals": [
    {
      "ticker": "AAPL",
      "sentiment": "positive",
      "confidence": 0.87,
      "recommendation": "BUY - Strong positive sentiment"
    },
    ...
  ],
  "agent_memory": {
    "total_entries": 5,
    "agent_name": "TradingAgent"
  }
}
```

## 🔐 Security & Best Practices

✅ **Implemented:**
- NO hardcoded API keys (uses .env)
- Proper secret management
- Input validation & sanitization
- Rate limiting awareness
- Error message safety (no key exposure)
- Comprehensive logging
- Clean separation of secrets

⚠️ **Before Production:**
- Use sealed secret management (AWS Secrets Manager, etc.)
- Implement API key rotation
- Add authentication layer
- Use HTTPS for all API calls
- Implement backoff/retry strategies
- Add monitoring & alerting
- Run security audit
- Load test with realistic data

## 📚 Dependencies

```
pandas               # Data manipulation
numpy                # Numerical computing
matplotlib           # Visualization
faiss-cpu           # Vector indexing
langchain           # LLM framework
langchain-community # Additional components
sentence-transformers # Text embeddings
requests            # HTTP client
apify-client        # Apify SDK
sec-api             # SEC data
python-dotenv       # Environment variables
```

See `requirements.txt` for pinned versions.

## 🐛 Known Limitations

1. **Rate Limiting**: May hit Apify rate limits during scraping
   - *Workaround*: Stagger requests or upgrade plan

2. **LLM Cost**: OpenRouter charging may apply
   - *Workaround*: Monitor API usage, set cost limits

3. **Twitter Data Availability**: Not all tickers have tweets
   - *Workaround*: Pipeline continues with available data

4. **FAISS Memory**: Large datasets may exceed RAM
   - *Workaround*: Implement batch indexing for scale

5. **Cold Start Time**: First run downloads ~500MB
   - *Workaround*: This is one-time; subsequent runs are fast

## 🔄 Continuous Improvement

The agent implements a learning loop:

```python
agent.learn(
    query="Analyze AAPL sentiment",
    response=trading_signal,
    feedback="Signal was correct"
)
```

Over time:
- ✓ Agent learns from correct/incorrect signals
- ✓ Memory grows to improve future decisions
- ✓ Confidence scores become more calibrated
- ✓ Recommendations become more accurate

## 📞 Support & Contribution

For issues, questions, or improvements:

1. Check `TESTING_INSTRUCTIONS.md` for common problems
2. Review `trading_agent.log` for error details
3. Verify API keys are valid and not rate-limited
4. Run module tests to isolate issues
5. Check network connectivity to APIs

## 📄 License

Proprietary - TZURONI Trading Systems

## 📞 Contact

For questions or issues, contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** April 5, 2026  
**Status:** Production Ready ✅  
**Python:** 3.8+  
**Tested On:** Windows 10/11, Linux, macOS

