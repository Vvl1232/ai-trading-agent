# System Architecture

## High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRADING AI AGENT PIPELINE                        │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: DATA ACQUISITION
    ├── SEC API → Insider Trading Data
    │   ├── Query: "transactionDate:[NOW-7DAYS TO NOW]"
    │   ├── Parse: CSV → DataFrame
    │   └── Output: ~100-200 trades
    │
    └── Apify Actor → Twitter Scraping
        ├── Actor: "apify/twitter-scraper"
        ├── Query: Stock tickers (AAPL, MSFT, etc.)
        └── Output: 100+ tweets per ticker

STEP 2: DATA PROCESSING
    ├── SEC Processing
    │   ├── Validate columns
    │   ├── Parse dates
    │   ├── Sort by transaction date
    │   └── Extract top 5 tickers
    │
    └── Tweet Processing
        ├── Extract text content
        ├── Clean/normalize text
        └── Group by ticker

STEP 3: TEXT PREPARATION FOR RAG
    ├── Raw Data → RecursiveCharacterTextSplitter
    │   ├── Chunk size: 500 tokens
    │   ├── Overlap: 50 tokens
    │   └── Output: 15-20 chunks per ticker
    │
    └── Chunks → HuggingFace Embeddings
        ├── Model: sentence-transformers/all-MiniLM-L6-v2
        ├── Dimension: 384-D vectors
        └── Output: Embedding vectors

STEP 4: VECTOR INDEXING
    └── Embeddings → FAISS Index
        ├── Index Type: IndexFlatL2
        ├── Metric: L2 distance
        ├── Search: Similarity matching
        └── Retrieval: Top-K documents

STEP 5: SENTIMENT ANALYSIS
    ├── For each ticker:
    │   ├── Get ticker text (tweets, news)
    │   ├── Call OpenRouter API
    │   ├── Model: Mistral-7B-Instruct
    │   ├── Prompt: Sentiment classification
    │   └── Output: {sentiment, confidence, summary}
    │
    └── Results: Sentiment distribution

STEP 6: CONTEXT RETRIEVAL (RAG)
    ├── Query: "Best stocks based on sentiment"
    ├── Search: FAISS similarity search
    ├── Retrieve: Top-3 relevant documents
    ├── Score: Similarity confidence (0-1)
    └── Output: Augmented context

STEP 7: SIGNAL GENERATION
    ├── Combine: Sentiment + Context + Confidence
    ├── Agent Logic:
    │   ├── If confidence > 0.8:
    │   │   └── "STRONG BUY/SELL"
    │   ├── Elif confidence > 0.5:
    │   │   └── "BUY/SELL"
    │   └── Else:
    │       └── "HOLD"
    │
    └── Output: Trading signals with recommendations

STEP 8: AGENT LEARNING
    ├── Record: Query → Response → Feedback
    ├── Store: In-memory learning memory
    ├── Update: Agent statistics
    └── Learn: From correct/incorrect decisions

STEP 9: VISUALIZATION
    ├── Plot 1: Sentiment distribution (bar chart)
    │   ├── X-axis: Positive, Negative, Neutral
    │   ├── Y-axis: Count
    │   └── Format: High-DPI PNG
    │
    └── Plot 2: Signal timeline (line chart)
        ├── X-axis: Time
        ├── Y-axis: Sentiment score
        └── Format: High-DPI PNG

STEP 10: REPORTING
    └── Generate JSON Report:
        ├── Timestamps
        ├── Tickers analyzed
        ├── Tweet counts
        ├── Sentiment distribution
        ├── Trading signals
        ├── Agent memory summary
        └── Confidence scores
```

---

## Class Hierarchy & Responsibilities

```
┌──────────────────────────────────────────────────────────────┐
│                   Main Pipeline                              │
│ (main.py - 10 steps)                                        │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬──────────────┐
        │           │           │              │
        ▼           ▼           ▼              ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
    │SEC Fetch│ │TwitterSc│ │Sentiment │ │Vector    │
    │         │ │raper    │ │Analyzer  │ │Store     │
    └────┬────┘ └────┬────┘ └──────┬───┘ └──────┬───┘
         │           │             │              │
         │ Tickers   │ Tweets      │ Signals    │ Context
         │           │             │              │
         └───────────┼─────────────┴──────────────┘
                     │
                     ▼
            ┌─────────────────────┐
            │  TradingAgent       │
            │  - Analyze Signal   │
            │  - Learn            │
            │  - Generate Rec.    │
            └────────┬────────────┘
                     │ Recommendations
                     ▼
            ┌─────────────────────┐
            │     Charts          │
            │  - Plot Sentiment   │
            │  - Plot Timeline    │
            │  - Create Report    │
            └─────────────────────┘
```

---

## Data Flow Diagram

### SEC Pipeline
```
SEC API
  ↓ (JSON: 100+ trades)
sec_fetch.get_sec_data()
  ↓
validate & parse
  ↓
sec_fetch.get_top5_trades()
  ↓
Top 5 DataFrame [AAPL, MSFT, NVDA, TSLA, GOOGL]
```

### Twitter Pipeline
```
Tickers [AAPL, MSFT, ...]
  ↓
TwitterScraper.get_tweets()
  ↓ (For each ticker)
Apify Actor (twitter-scraper)
  ↓
Raw tweets [100+]
  ↓
Parse & structure
  ↓
Tweet Objects [{text, author, likes, ...}, ...]
```

### RAG Pipeline
```
Tweet Texts ["We love AAPL!", "MSFT is strong", ...]
  ↓
chunk_data() [RecursiveCharacterTextSplitter]
  ↓
Chunks ["We love AAPL", "AAPL stock", ...] (500 tokens)
  ↓
create_vector_store()
  ↓
embeddings.embed_documents() [HuggingFace]
  ↓
Embeddings [384-dim vectors]
  ↓
faiss.IndexFlatL2.add()
  ↓
FAISS Index (L2 distance)
  ↓
similarity_search(query)
  ↓
Top-3 Similar Documents [{text, score}, ...]
  ↓
get_context() [String context]
```

### Sentiment Pipeline
```
Ticker-specific Text
  ↓
analyze_sentiment(text)
  ↓
OpenRouter API (Mistral-7B)
  ↓ Prompt
"Classify sentiment (positive/negative/neutral)"
  ↓ Response
{
  "sentiment": "positive",
  "confidence": 0.87,
  "summary": "Strong bullish signals"
}
  ↓
SentimentAnalyzer Parsing & Validation
  ↓
Validated Sentiment Result
```

### Signal Generation Pipeline
```
Ticker + Sentiment + Confidence + Context
  ↓
analyze_sentiment_signal()
  ↓
Apply Logic:
  → confidence < 0.5? → "HOLD (low confidence)"
  → sentiment == "positive" & conf >= 0.8? → "BUY (strong)"
  → sentiment == "negative" & conf >= 0.8? → "SELL (strong)"
  ↓
Signal = {
  ticker: "AAPL",
  sentiment: "positive",
  confidence: 0.87,
  recommendation: "BUY - Strong positive sentiment",
  context: "...",
  metadata: {...}
}
```

---

## Module Dependencies

```
main.py
├── config.py (load API keys, constants)
├── sec_fetch.py (get insider data)
├── twitter_scraper.py (get tweets)
├── vector_store.py (RAG operations)
│   ├── langchain.text_splitters
│   ├── langchain.embeddings (HuggingFace)
│   └── faiss (indexing)
├── sentiment.py (LLM inference)
│   └── requests (OpenRouter API)
├── trading_agent.py (signals + learning)
└── charts.py (visualization)
    ├── matplotlib
    └── json (reporting)
```

---

## Error Handling Strategy

```
┌─────────────────────────────────────────┐
│          API Call                       │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼──────┐
        │  Try Call   │
        └──────┬──────┘
               ├─ Success → Process & Continue
               │
               └─ Failure → Catch Exception
                    │
                    ├─ Log Error (ERROR level)
                    ├─ Increment Retry Counter
                    │
                    ├─ If Retries < MAX_RETRIES
                    │  └─ Retry with backoff
                    │
                    └─ Else
                       ├─ Log Failure (WARNING level)
                       ├─ Use Fallback Data (Demo)
                       └─ Continue Pipeline
```

---

## Configuration Management

```
config.py
├── API Keys (from .env)
│   ├── SEC_API_KEY
│   ├── APIFY_API_KEY
│   └── OPENROUTER_API_KEY
│
├── Constants
│   ├── SEC_QUERY_RANGE = "NOW-7DAYS"
│   ├── TWEET_SEARCH_LIMIT = 100
│   ├── CHUNK_SIZE = 500
│   ├── CHUNK_OVERLAP = 50
│   ├── SIMILARITY_THRESHOLD = 0.5
│   ├── LLM_MODEL = "mistral-7b-instruct"
│   ├── LLM_TIMEOUT = 30
│   └── MAX_RETRIES = 3
│
└── Logging Setup
    ├── File: trading_agent.log
    └── Console: INFO level
```

---

## Database & State

```
Runtime State (In-Memory)
├── API Responses
│   ├── SEC data (trades)
│   ├── Twitter data (tweets)
│   └── LLM results (sentiments)
│
├── Processing State
│   ├── Chunks (tokenized)
│   ├── Embeddings (vectors)
│   ├── FAISS Index (search)
│   └── Trading Signals
│
└── Agent Memory
    ├── Learning entries
    │   ├── Query
    │   ├── Response
    │   ├── Feedback (optional)
    │   └── Timestamp
    │
    └── Statistics
        ├── Total entries
        ├── Latest entry
        └── Memory summary

Persistent Output (Files)
├── Logs: trading_agent.log
├── Data: outputs/report_*.json
├── Charts: outputs/sentiment.png
└── Config: .env
```

---

## Performance Characteristics

### Time Complexity
- SEC API: O(n) - linear in trade count
- Twitter Scraping: O(m × t) - m tickers, t tweets each
- Chunking: O(n log n) - sorting during split
- Embeddings: O(n × d) - n chunks, d=384 dims
- FAISS Search: O(log n) - binary search equivalent
- LLM Inference: O(t) - linear in token length

### Space Complexity
- Tweets: O(m × t) - m tickers, t tweets
- Embeddings: O(n × 384) - n chunks, 384-dim vectors
- FAISS Index: O(n × 384) - proportional to embeddings
- Agent Memory: O(k) - grows with decisions

### Bottlenecks
1. **Apify Scraping** (30-60 sec) - Network I/O
2. **LLM Inference** (5-10 sec/ticker) - API latency
3. **Model Download** (2-3 min first run) - Network + disk
4. **FAISS Indexing** (5-15 sec) - CPU computation

---

## Deployment Architecture

```
Development
├── Local .env file
├── Direct API calls
└── Local file outputs

Production
├── Docker container
│   ├── config from secrets
│   ├── API calls via VPN/proxy
│   └── outputs to S3/cloud
│
├── Scheduled Execution
│   ├── Cron (Linux)
│   ├── Task Scheduler (Windows)
│   └── Lambda/CloudFunction
│
├── Monitoring
│   ├── Log aggregation (ELK/CloudWatch)
│   ├── Error alerts (PagerDuty)
│   └── Metrics (Prometheus/DataDog)
│
└── Data Pipeline
    ├── Store in database (PostgreSQL/MongoDB)
    ├── Stream to message queue (Kafka/RabbitMQ)
    └── Expose via REST API (Flask/FastAPI)
```

---

## Testing Strategy

```
Unit Tests (test_*.py)
├── test_sec_fetch.py
│   ├── Test get_sec_data()
│   └── Test get_top5_trades()
│
├── test_twitter_scraper.py
│   └── Test get_tweets()
│
├── test_sentiment.py
│   ├── Test analyze_sentiment()
│   └── Test parse_response()
│
├── test_vector_store.py
│   ├── Test chunk_data()
│   ├── Test create_index()
│   └── Test similarity_search()
│
├── test_agent.py
│   ├── Test signal generation
│   └── Test learning loop
│
└── test_charts.py
    ├── Test plot generation
    └── Test report creation

Integration Tests
├── test_pipeline.py
│   └── Test full end-to-end pipeline
│
└── test_api_integration.py
    ├── Mock API responses
    └── Test error handling

Performance Tests
├── test_embeddings.py
│   └── Measure embedding time
│
└── test_faiss.py
    └── Measure search performance
```

---

## Key Design Patterns

### 1. Singleton Pattern
```python
_agent = None
def get_agent():
    global _agent
    if _agent is None:
        _agent = TradingAgent()
    return _agent
```

### 2. Factory Pattern
```python
def create_vector_store(chunks):
    store = VectorStore()
    store.create_index(chunks)
    return store
```

### 3. Strategy Pattern
```python
def _generate_recommendation(sentiment, confidence):
    if sentiment == "positive":
        return "BUY"
    elif sentiment == "negative":
        return "SELL"
    return "HOLD"
```

### 4. Retry Logic Pattern
```python
for attempt in range(MAX_RETRIES):
    try:
        result = api_call()
        return result
    except Exception:
        if attempt < MAX_RETRIES - 1:
            continue
        raise
```

---

## Scalability Considerations

### Current Limits
- Max tweets per run: 500+ (5 tickers × 100 tweets)
- Max FAISS vectors: ~50,000 (limited by RAM)
- Max concurrent LLM calls: 1 (sequential)
- Max agent memory: Unlimited (grows with time)

### Scaling Solutions
- **Batch Processing**: Process multiple tickers in parallel
- **Distributed FAISS**: Split index across nodes
- **Async LLM**: Queue-based inference
- **Database Storage**: Persist memory to database
- **Caching**: Cache FAISS index between runs
- **Microservices**: Separate API, LLM, RAG services

---

## Security & Privacy

### Data Protection
- ✓ API keys in .env (not in code)
- ✓ No hardcoded secrets
- ✓ Request timeouts (prevents hanging)
- ✓ Input validation (prevents injection)

### Privacy
- ✓ No personal data collection
- ✓ Twitter data aggregated (no usernames stored long-term)
- ✓ Predictions are not personally identifiable
- ✓ No data sent to unauthorized services

### Audit Trail
- ✓ All operations logged with timestamps
- ✓ Agent decisions recorded in memory
- ✓ Error conditions logged
- ✓ API calls tracked

---

**Architecture Version**: 1.0  
**Last Updated**: April 5, 2026  
**Status**: Production Ready
