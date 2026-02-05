# Nepal Sports News Automation Bot

Automated sports news bot that publishes cricket and football articles to WordPress with AI-generated content and images.

## Features

- **Full Article Extraction** - Extracts 2,000-6,000 char articles from BBC, Guardian, Yahoo (vs 65-150 from RSS)
- **AI Content Generation** - Claude 3.5 Sonnet rewrites with Nepal/India angle + betting insights
- **Context-Aware Images** - APIFree.ai generates relevant images matching article type
- **Fact-Checking** - Verifies tournament names, quotes, dates, and statistics
- **SEO Optimized** - Meta descriptions, categories, tags, and Google Discover eligible
- **Quality Control** - Minimum 300 char source content, no placeholder text, proper citations

## Quality Score

- **Before**: 62/100 (wrong facts, misleading titles, fabricated quotes)
- **After**: 85-90/100 (factual accuracy, proper citations, verified details)

## Architecture

```
src/
├── news_bot.py          # Main bot orchestration
├── article_extractor.py # Multi-strategy article extraction
├── apifree_client.py    # APIFree.ai image generation
├── api_clients.py       # OpenRouter, Serper, Cloudflare, WordPress
├── config.py            # Configuration and priorities
└── utils.py             # Database, logging, sanitization

tests/                   # Test scripts
docs/                    # Documentation
.github/workflows/       # GitHub Actions automation
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required:
- `SERPER_KEY_MAIN` - Google Search API
- `OPENROUTER_API_KEY` - Claude 3.5 Sonnet
- `APIFREE_API_KEY` - Image generation
- `WP_URL` - WordPress site URL
- `WP_USERNAME` - WordPress username
- `WP_APP_PASSWORD` - WordPress app password

Optional:
- `CLOUDFLARE_ACCOUNT_ID` - Fallback image generation
- `CLOUDFLARE_TOKEN` - Fallback image generation
- `GA_MEASUREMENT_ID` - Google Analytics

### 3. Run Locally

```bash
# Test single article
python3 test_single_article.py

# Run full bot (1 article)
python3 src/news_bot.py
```

## GitHub Actions

The bot runs automatically every hour via GitHub Actions:

- **Schedule**: Every hour (24 articles/day)
- **Manual**: Can be triggered manually from Actions tab
- **Secrets**: Configure in Settings → Secrets and variables → Actions

### Required Secrets

1. `SERPER_KEY_MAIN`
2. `OPENROUTER_API_KEY`
3. `APIFREE_API_KEY`
4. `WP_URL`
5. `WP_USERNAME`
6. `WP_APP_PASSWORD`

See `GITHUB_SECRETS_CHECKLIST.md` for complete list.

## Configuration

### Priority Scoring (src/config.py)

- Cricket: +5 points
- Football/Leagues: +3 points
- Other sports: +2 points
- Nepal/India mentions: +5 bonus

### RSS Feeds

Prioritized for extraction success:
1. BBC Sport Football (excellent)
2. The Guardian Sport (excellent)
3. Yahoo Sports (good)
4. Sky Sports Football (good)
5. ESPN Cricinfo (blocks scraping - fallback)

### Article Processing

- **Extraction**: newspaper3k, trafilatura, BeautifulSoup
- **Minimum content**: 300 chars (prevents AI hallucination)
- **Target length**: 800-1200 words
- **Processing time**: ~53 seconds/article
- **Cost**: ~$0.019/article

## Quality Features

### Fact-Checking
- ✅ Tournament names verified (T20 World Cup 2026, not just "World Cup")
- ✅ Quote context verified (no memes/political quotes without context)
- ✅ Host countries included (India and Sri Lanka)
- ✅ Precise dates (start to final, not just "begins on X")
- ✅ Statistics sourced or softened

### Content Quality
- ✅ Visible publish date
- ✅ Source citations
- ✅ Background sections for complex stories
- ✅ Proper quote attribution
- ✅ No placeholder text
- ✅ Minimum 800 words

### SEO & WordPress
- ✅ Featured images (context-aware)
- ✅ Categories (Cricket, Football, Sports Betting)
- ✅ Tags (teams, tournaments, players)
- ✅ Meta descriptions
- ✅ Google Discover eligible

## Cost Breakdown

### Per Article
- APIFree.ai image: $0.004
- Claude 3.5 Sonnet: ~$0.015
- **Total**: ~$0.019/article

### Daily (24 articles)
- **Cost**: ~$0.46/day
- **Monthly**: ~$13.80/month

## Recent Improvements

### v2.0 (February 2026)
- ✅ Full article extraction (2,000-6,000 chars vs 65-150)
- ✅ Priority scoring updated (Cricket +5, Football +3, Other +2)
- ✅ Quote context verification (no memes without context)
- ✅ Tournament details required (hosts, dates, venues)
- ✅ Category accuracy (2+ keyword matches required)
- ✅ Enhanced fact-checking in prompt

### v1.0 (Initial)
- Basic RSS scraping
- AI content generation
- Cloudflare image generation
- WordPress publishing

## Test Articles

- **Italy T20 World Cup**: https://1xbatnepal.com/italys-historic-t20-world-cup-qualification-stuns-cricket-world/
- **India T20 World Cup**: https://1xbatnepal.com/t20-world-cup-2026-india-emerges-as-clear-favorite-amid-record-breaking-era/

## Documentation

- `GITHUB_SECRETS_CHECKLIST.md` - Complete secrets setup guide
- `FINAL_CRITICAL_FIXES_IMPLEMENTED.md` - All improvements documented
- `FIXES_SUMMARY.md` - Quick reference for fixes
- `docs/` - Additional documentation

## Troubleshooting

### ESPN Cricinfo Blocking
- **Problem**: ESPN returns 403 errors
- **Solution**: RSS feeds reordered to prioritize BBC/Guardian/Yahoo

### Insufficient Content
- **Problem**: Articles skipped due to short content
- **Solution**: Quality control working correctly - prevents AI hallucination

### Image Generation Fails
- **Primary**: APIFree.ai ($0.004/image)
- **Fallback**: Cloudflare Flux (free)
- **Last resort**: Skip image (article still publishes)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review `GITHUB_SECRETS_CHECKLIST.md`
3. Open an issue on GitHub

---

**Built with**: Python 3.11+ | Claude 3.5 Sonnet | APIFree.ai | WordPress
