# Testing & Setup Instructions

## Prerequisites

- Python 3.8+
- pip package manager
- Valid API keys for: SEC API, Apify, OpenRouter

## Step 1: Environment Setup

```bash
# Navigate to project directory
cd d:\Internships\TZURONI\trading-ai-agent

# Copy environment template
copy .env.example .env

# Edit .env with your API keys
# Windows: notepad .env
# Or use VS Code: code .env
```

## Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify core dependencies
python -c "import pandas, matplotlib, faiss, langchain, requests; print('✓ Core dependencies OK')"
python -c "from sentence_transformers import SentenceTransformer; print('✓ HuggingFace OK')"
```

## Step 3: Get API Keys

### SEC API
1. Visit: https://sec-api.com/
2. Sign up for free account
3. Get API key from dashboard
4. Add to .env: `SEC_API_KEY=your_key`

### Apify API
1. Visit: https://apify.com/
2. Create account
3. Navigate to integrations → API tokens
4. Copy token
5. Add to .env: `APIFY_API_KEY=your_key`

### OpenRouter API
1. Visit: https://openrouter.ai/
2. Sign up (Google/GitHub OAuth)
3. Go to Settings → API Keys
4. Create new key
5. Add to .env: `OPENROUTER_API_KEY=your_key`

## Step 4: Test Individual Modules

### Test Configuration
```bash
python -c "from utils.config import *; print('✓ Config loaded')"
```

### Test SEC Data Fetch (requires valid API key)
```bash
python -c "
from data.sec_fetch import get_sec_data
try:
    data = get_sec_data()
    print(f'✓ SEC API working - found {len(data.get(\"data\", []))} trades')
except Exception as e:
    print(f'✗ SEC API Error: {e}')
"
```

### Test LLM Sentiment Analysis (requires OpenRouter key)
```bash
python -c "
from llm.sentiment import analyze_sentiment
try:
    result = analyze_sentiment('This stock looks promising')
    print(f'✓ Sentiment API working: {result[\"sentiment\"]}')
except Exception as e:
    print(f'✗ LLM API Error: {e}')
"
```

### Test Vector Store (local, no API needed)
```bash
python -c "
from rag.vector_store import chunk_data, create_vector_store, get_context
texts = [
    'Stock market is booming',
    'Economic data shows growth',
    'Investors are optimistic'
]
try:
    chunks = chunk_data(texts)
    print(f'✓ Chunking works: {len(chunks)} chunks')
except Exception as e:
    print(f'✗ Vector Store Error: {e}')
"
```

### Test Agent
```bash
python -c "
from agents.trading_agent import agent, analyze_sentiment_signal
signal = analyze_sentiment_signal(
    'AAPL',
    {'sentiment': 'positive', 'confidence': 0.85},
    'Context about Apple stock'
)
print(f'✓ Agent working: {signal[\"recommendation\"]}')
"
```

### Test Charts (local, no API needed)
```bash
python -c "
from utils.charts import plot_sentiment
try:
    path = plot_sentiment(5, 2, 3)
    print(f'✓ Charts working: {path}')
except Exception as e:
    print(f'✗ Charts Error: {e}')
"
```

## Step 5: Run Full Pipeline

### Option A: Run with Real APIs (requires all 3 API keys)
```bash
# Full production run
python main.py

# Expected execution time: 3-5 minutes
# Outputs:
#   - trading_agent.log (detailed logs)
#   - outputs/sentiment.png (chart)
#   - outputs/report_YYYYMMDD_HHMMSS.json (JSON report)
```

### Option B: Demo Mode (no API keys needed)
```bash
# The pipeline automatically falls back to demo data if APIs fail
# Good for testing without API keys

# Just run main.py - it will gracefully handle missing APIs
python main.py

# Expected output after ~30 seconds:
# Shows synthetic trading signals for demo tickers
```

## Step 6: Verify Output

### Check Generated Files
```bash
# List outputs
ls -la outputs/

# View report (JSON format)
type outputs\report_*.json

# View chart
# Windows: start outputs\sentiment.png
# Linux/Mac: open outputs/sentiment.png
```

### Check Logs
```bash
# View real-time logs
type trading_agent.log

# Or tail logs (Windows doesn't have tail, use tail replacement):
powershell -Command "Get-Content trading_agent.log -Tail 20 -Wait"
```

## Expected Output Example

### Successful Run
```
================================================================================
TRADING AI AGENT - PIPELINE START
================================================================================
Step 1: Validating API credentials...
✓ API credentials validated

Step 2: Fetching SEC insider trading data...
✓ Retrieved SEC data: 157 trades

Step 3: Extracting top 5 trades...
✓ Top tickers identified: ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL']

Step 4: Scraping tweets for 5 tickers...
✓ Fetched 234 tweets

Step 5: Chunking 234 tweets for RAG...
✓ Created 18 chunks (size=500, overlap=50)

Step 6: Creating FAISS vector store...
✓ Vector store initialized with embeddings

Step 7: Analyzing sentiment and generating signals...
  Analyzing 1/5: AAPL
    ✓ AAPL: POSITIVE (confidence: 0.87)
    Recommendation: BUY - Strong positive sentiment
  ...

Step 8: Recording agent learning...
✓ Agent memory updated: 5 entries

Step 9: Generating visualizations...
✓ Sentiment chart saved: outputs/sentiment.png

Step 10: Creating analysis report...
✓ Report saved: outputs/report_20240405_143022.json

================================================================================
PIPELINE SUMMARY
================================================================================
Tickers Analyzed: AAPL, MSFT, NVDA, TSLA, GOOGL
Total Tweets Processed: 234
Trading Signals Generated: 5
Sentiment Distribution:
  - Positive: 3
  - Negative: 1
  - Neutral: 1

Top Trading Signals:
  AAPL: BUY - Strong positive sentiment (confidence: 0.87)
  MSFT: BUY - Positive sentiment (confidence: 0.72)
  NVDA: HOLD - Neutral sentiment (confidence: 0.51)

================================================================================
PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

## Troubleshooting

### Issue: "OPENROUTER_API_KEY not found"
**Solution:** 
1. Create .env file from .env.example
2. Add your actual API key
3. Verify no spaces around `=` sign

### Issue: "sec-api import error"
**Solution:**
```bash
pip install sec-api --upgrade
```

### Issue: "FAISS indexing failed"
**Solution:**
```bash
# FAISS CPU version has some platform issues
pip uninstall faiss-cpu
pip install faiss-cpu==1.7.4
```

### Issue: "HuggingFace model download hangs"
**Solution:**
The first run downloads ~500MB of embeddings model. This is normal.
- First run: 2-3 minutes for model download
- Subsequent runs: <30 seconds

### Issue: "Apify rate limited"
**Solution:**
The scraper will gracefully fall back to demo data. No error.

### Issue: "Out of memory during embedding"
**Solution:**
Reduce chunk size in utils/config.py:
```python
CHUNK_SIZE = 250  # Instead of 500
```

## REST API Testing (Optional)

If you plan to wrap this in a Flask/FastAPI:

```python
# test_api_call.py
import requests
import json

# Call your API endpoint
response = requests.post('http://localhost:5000/analyze', 
    json={'tickers': ['AAPL', 'MSFT']})

print(json.dumps(response.json(), indent=2))
```

## Performance Metrics

| Task | Time | Notes |
|------|------|-------|
| SEC API call | 2-3 sec | Single API request |
| Apify scraping | 30-60 sec | Per 5 tickers |
| LLM sentiment | 5-10 sec | Per ticker |
| FAISS indexing | 5-15 sec | One-time per run |
| Full pipeline | 3-5 min | With all APIs |
| Demo mode | 30-45 sec | No API calls |

## CI/CD Integration

To run in GitHub Actions:

```yaml
name: Trading Agent Pipeline

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: |
          echo "SEC_API_KEY=${{ secrets.SEC_API_KEY }}" > .env
          echo "APIFY_API_KEY=${{ secrets.APIFY_API_KEY }}" >> .env
          echo "OPENROUTER_API_KEY=${{ secrets.OPENROUTER_API_KEY }}" >> .env
      - run: python main.py
      - uses: actions/upload-artifact@v2
        with:
          name: trading-reports
          path: outputs/
```

## Manual Testing Checklist

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with API keys
- [ ] Config module imports successfully
- [ ] Individual modules test without error
- [ ] Full pipeline runs to completion
- [ ] Output files generated (PNG chart, JSON report)
- [ ] Logs show no critical errors
- [ ] Trading signals contain valid recommendations

## Getting Help

1. Check logs: `tail -100 trading_agent.log`
2. Run module tests above to isolate issues
3. Verify API keys are correct and not expired
4. Check internet connection for API calls
5. Review error messages in console output

---

**Last Updated:** April 5, 2026
**Python Version:** 3.8+
**Status:** Production Ready
