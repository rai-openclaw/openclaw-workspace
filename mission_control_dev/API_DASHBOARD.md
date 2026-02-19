# API Usage Dashboard

Track all APIs used by Mission Control, their limits, costs, and quick recharge links.

## API Inventory

| API | Purpose | Status | Monthly Cost | Limit Status | Quick Link |
|-----|---------|--------|--------------|--------------|------------|
| **Finnhub** | Stock prices | 🟢 Active | Free tier | 60 calls/min | [Dashboard](https://finnhub.io/dashboard) |
| **CoinGecko** | Crypto prices | 🟡 Rate limited | Free | 10-30 calls/min | [Pricing](https://www.coingecko.com/en/api/pricing) |
| **Gemini (Google)** | OCR screenshots | 🟢 Active | Pay-as-you-go | Per 1K requests | [Cloud Console](https://console.cloud.google.com/billing) |
| **Brave Search** | Web search | 🟢 Active | Free tier | 2K queries/month | [Dashboard](https://api.search.brave.com/app/dashboard) |

## Key Details

### Finnhub (Stocks)
- **API Key:** `d68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0`
- **Tier:** Free
- **Limit:** 60 calls/minute
- **Cost:** $0 (free tier)
- **Used for:** Real-time stock prices in portfolio tracker
- **Status:** ✅ Working normally

### CoinGecko (Crypto)
- **API Key:** None (public endpoint)
- **Tier:** Free Demo
- **Limit:** 10-30 calls/minute (varies)
- **Cost:** $0
- **Used for:** ETH price updates
- **Status:** ⚠️ Rate limited today (429 errors seen)
- **Alternative:** Could use Finnhub for ETH too

### Gemini / Google AI (OCR)
- **API Key:** Stored in `.gemini_api_key`
- **Tier:** Pay-as-you-go
- **Limit:** Based on quota
- **Cost:** ~$0.001-0.01 per image (varies by model)
- **Used for:** Screenshot OCR (brokerage statements)
- **Status:** ✅ Working (after rate limit cooldown)
- **Recharge:** [Google Cloud Billing](https://console.cloud.google.com/billing)

### Brave Search
- **API Key:** Yes (via OpenClaw config)
- **Tier:** Free
- **Limit:** 2,000 queries/month
- **Cost:** $0
- **Used for:** Web search in research tasks
- **Status:** ✅ Available

## Cost Estimates

### Current Month (February 2026)
| API | Estimated Calls | Est. Cost |
|-----|----------------|-----------|
| Finnhub | ~1,000 | $0 |
| CoinGecko | ~100 | $0 |
| Gemini OCR | ~50 images | $0.50-1.00 |
| Brave Search | ~50 | $0 |
| **Total** | - | **~$1.00** |

## Rate Limit Alerts

### Current Issues:
- **CoinGecko:** Hit 429 rate limit today (temporary, resolves in ~1 hour)
  - **Workaround:** Cached for 5 min, manual refresh available
  - **Alternative:** Use Finnhub for ETH instead

### Monitoring:
- [ ] Add rate limit tracking to dashboard
- [ ] Set up alerts at 80% usage
- [ ] Add fallback API options

## Quick Actions

### Check API Status:
```bash
# Test Finnhub
curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=d68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0"

# Test CoinGecko
curl "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
```

### Recharge/Add Credits:
1. **Finnhub:** Upgrade at [finnhub.io/pricing](https://finnhub.io/pricing)
2. **Gemini:** Add billing at [Google Cloud Console](https://console.cloud.google.com/billing)
3. **Brave:** Check usage at [api.search.brave.com](https://api.search.brave.com/app/dashboard)

## Future Improvements

- [ ] Real-time usage counters
- [ ] Automated rate limit alerts
- [ ] Cost projection based on usage trends
- [ ] API key rotation reminders
- [ ] Fallback API switching (e.g., CoinGecko → Finnhub for crypto)

---

**Last Updated:** February 15, 2026
