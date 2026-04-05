# Quick Start Guide - Trading AI Agent

## 60-Second Setup

```bash
# 1. Install dependencies (1-2 minutes)
pip install -r requirements.txt

# 2. Create config file
copy .env.example .env

# 3. Add your API keys to .env (get from links below)
# SEC_API_KEY=your_key_here
# APIFY_API_KEY=your_key_here  
# OPENROUTER_API_KEY=your_key_here

# 4. Run the pipeline (3-5 minutes)
python main.py

# 5. Check outputs
ls outputs/
```

## Get Free API Keys (Takes ~5 minutes total)

### SEC API (FREE)
1. Go to: https://sec-api.com/
2. Click "Sign Up"
3. Email verification
4. Copy your API key
5. Add to .env: `SEC_API_KEY=your_key`

### Apify (FREE $25 credit)
1. Go to: https://apify.com/
2. GitHub/Google sign-up
3. Go to Settings → Integrations → API tokens
4. Copy token
5. Add to .env: `APIFY_API_KEY=your_key`

### OpenRouter (PAY-AS-YOU-GO, ~$0.20 per run)
1. Go to: https://openrouter.ai/
2. Google/GitHub sign-up
3. Settings → API Keys
4. Create key
5. Add to .env: `OPENROUTER_API_KEY=your_key`

## Test Without Real APIs

The pipeline automatically falls back to demo data if APIs fail:

```bash
# Just run - it will work with synthetic data
python main.py

# Expected: Complete in ~30 seconds without API calls
```

## What You Get

After running `python main.py`:

```
trading_agent.log           # Detailed execution log
outputs/sentiment.png       # Chart of sentiment distribution
outputs/report_*.json       # Full trading analysis report
```

## Understanding Output

### Logs (trading_agent.log)
```
✓ SEC data: 157 insider trades
✓ Top tickers: AAPL, MSFT, NVDA, TSLA, GOOGL
✓ Tweets fetched: 234 total
✓ Signals generated: 5 recommendations
```

### Chart (sentiment.png)
Visual bar chart showing:
- How many positive signals
- How many negative signals
- How many neutral signals

### Report (JSON)
```json
{
  "tickers_analyzed": ["AAPL", "MSFT", ...],
  "trading_signals": [
    {
      "ticker": "AAPL",
      "recommendation": "BUY - Strong positive sentiment",
      "confidence": 0.87
    },
    ...
  ]
}
```

## Troubleshooting

### Issue: "API key not found"
**Fix:**
1. Make sure .env file exists
2. Check formatting: `KEY=value` (no spaces)
3. Verify API keys are valid

### Issue: Python error on import
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Out of memory" during first run
- This is normal! HuggingFace model is ~500MB
- Subsequent runs will be faster

### Issue: "No tweets found"
- Twitter API might have rate limits
- Pipeline continues with synthetic data
- All signals still generated

## Run on Schedule

### Windows (Task Scheduler)
```powershell
# Create scheduled task to run daily at 9 AM
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$action = New-ScheduledTaskAction -Execute "python" -Argument "c:\path\to\main.py"
Register-ScheduledTask -TaskName "TradingAgent" -Trigger $trigger -Action $action
```

### Linux (Cron)
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/trading-ai-agent && python main.py
```

## Next Steps

1. **Read Full Docs**: See `README.md` for complete guide
2. **Understand Pipeline**: See `FIXES_SUMMARY.md` for what was fixed
3. **Testing Guide**: See `TESTING_INSTRUCTIONS.md` for deep dive
4. **Review Code**: Start with `main.py` to understand flow

## Key Commands

```bash
# Run full pipeline
python main.py

# View logs in real-time (Windows PowerShell)
Get-Content trading_agent.log -Tail 10 -Wait

# View logs (Linux/Mac)
tail -f trading_agent.log

# Check module imports
python -c "from agents.trading_agent import agent; print('✓ OK')"

# Remove output files
rm -r outputs/

# Run specific module test
python -c "from data.sec_fetch import get_sec_data; print('SEC module OK')"
```

## Project Structure

```
trading-ai-agent/
├── main.py                    ← Start here
├── .env                       ← Your API keys go here
├── agents/trading_agent.py    ← Trading logic
├── data/sec_fetch.py          ← SEC data
├── apify/twitter_scraper.py   ← Twitter data
├── llm/sentiment.py           ← AI sentiment
├── rag/vector_store.py        ← Search/context
├── utils/charts.py            ← Visualizations
└── outputs/                   ← Generated files
```

## API Costs (Estimated)

| Service | Per Run | Monthly |
|---------|---------|---------|
| SEC API | FREE | FREE |
| Apify | ~$0.01 | ~$0.30 |
| OpenRouter | ~$0.15 | ~$4.50 |
| **TOTAL** | **~$0.16** | **~$4.80** |

(Costs vary by API usage - see official pricing)

## Support

- 🔍 Check logs first: `tail trading_agent.log`
- 📖 Read: `README.md`
- 🧪 Run tests: See `TESTING_INSTRUCTIONS.md`
- 💡 Understand fixes: See `FIXES_SUMMARY.md`

---

**Ready?** Just run: `python main.py`

Good luck! 🚀
