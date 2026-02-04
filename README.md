# Nepal Sports News Automation Bot

Automated sports news publishing system for Nepal/India audience with betting focus. Publishes 80 cricket and football articles daily to WordPress with SEO optimization and 1xbet.com betting tips.

## 🎯 Project Overview

- **Target Audience:** Nepal and India sports betting enthusiasts
- **Focus Sports:** Cricket & Football (NOT American sports)
- **Publishing:** 80 articles/day (every 3 hours, 10 per run)
- **Traffic Goal:** 10,000+ visitors/month (expecting 48k-72k)
- **Betting Partner:** 1xbet.com with 18+ disclaimers

## 📁 Project Structure

```
Sport-News-Automation-Powerhouse/
├── src/                    # Source code
│   ├── news_bot.py        # Main bot script
│   ├── api_clients.py     # API integrations
│   ├── config.py          # Configuration
│   └── utils.py           # Helper functions
│
├── tests/                  # Testing & diagnostics
│   ├── test_bot.py        # Unit tests
│   ├── diagnose.py        # Diagnostic tool
│   ├── test_local.py      # Local testing
│   └── test_imports.py    # Import verification
│
├── docs/                   # Documentation
│   ├── SETUP_GUIDE.md     # Setup instructions
│   ├── TROUBLESHOOTING.md # Common issues
│   ├── NEXT_STEPS.md      # Post-setup guide
│   └── ...                # More docs
│
├── .github/workflows/      # GitHub Actions
│   ├── news-automation.yml # Main workflow
│   └── test.yml           # Test workflow
│
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Rivitnp/Sport-News-Automation-Powerhouse.git
cd Sport-News-Automation-Powerhouse
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Diagnostic
```bash
python tests/diagnose.py
```

### 5. Test Locally
```bash
PYTHONPATH=src python src/news_bot.py
```

### 6. Deploy to GitHub
```bash
# Set GitHub Secrets (see docs/SETUP_GUIDE.md)
# Workflow runs automatically every 3 hours
```

## 🔑 Required API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Serper** | Trending keywords | [serper.dev](https://serper.dev) |
| **OpenRouter** | AI content generation | [openrouter.ai](https://openrouter.ai) |
| **WordPress** | Publishing platform | Your WordPress site |
| **Cloudflare** | AI image generation | [cloudflare.com](https://cloudflare.com) |
| **Google Analytics** | Traffic tracking | [analytics.google.com](https://analytics.google.com) |

See [`docs/SETUP_GUIDE.md`](docs/SETUP_GUIDE.md) for detailed instructions.

## ✨ Key Features

### Content Generation
- ✅ Fetches from 8 RSS feeds (cricket/football priority)
- ✅ AI-powered content rewriting (DeepSeek v3)
- ✅ SEO optimization with trending keywords
- ✅ 800-1200 word articles

### Betting Integration
- ✅ Automatic betting tips sections
- ✅ 1xbet.com mentions in every article
- ✅ 18+ disclaimers on all betting content
- ✅ Context-aware betting predictions

### Image Handling
- ✅ Copyright-free AI image generation (Cloudflare Flux)
- ✅ AVIF format optimization
- ✅ No source image extraction (safe mode)

### SEO & Analytics
- ✅ Google Analytics 4 integration
- ✅ Schema.org markup
- ✅ Meta descriptions with betting keywords
- ✅ Internal linking opportunities

### Automation
- ✅ Runs every 3 hours via GitHub Actions
- ✅ Duplicate detection
- ✅ Rate limiting
- ✅ Comprehensive error logging
- ✅ Automatic retries

## 📊 Publishing Schedule

| Time (UTC) | Articles | Daily Total |
|------------|----------|-------------|
| 00:00 | 10 | 10 |
| 03:00 | 10 | 20 |
| 06:00 | 10 | 30 |
| 09:00 | 10 | 40 |
| 12:00 | 10 | 50 |
| 15:00 | 10 | 60 |
| 18:00 | 10 | 70 |
| 21:00 | 10 | **80** |

## 🔧 Configuration

### Priority Sports (config.py)
```python
PRIORITY_SPORTS = {
    'cricket': 10,      # Highest
    'football': 9,      # High
    'ipl': 10,          # Indian Premier League
    'ucl': 9,           # Champions League
    'american football': 1,  # Filtered out
}
```

### RSS Feeds
- ESPN Cricinfo
- Cricbuzz
- NDTV Sports
- Goal.com
- BBC Sport
- And more...

See [`src/config.py`](src/config.py) for full configuration.

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Diagnostic
```bash
python tests/diagnose.py
```

### Test Locally
```bash
PYTHONPATH=src python src/news_bot.py
```

See [`tests/README.md`](tests/README.md) for more testing options.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Complete setup instructions |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & solutions |
| [NEXT_STEPS.md](docs/NEXT_STEPS.md) | What to do after setup |
| [WHERE_ARE_LOGS.md](docs/WHERE_ARE_LOGS.md) | Finding GitHub Actions logs |
| [BETTING_FEATURES.md](docs/BETTING_FEATURES.md) | Betting integration details |
| [SECURITY.md](docs/SECURITY.md) | Security best practices |

See [`docs/`](docs/) for all documentation.

## 🐛 Troubleshooting

### Bot runs but publishes 0 articles?
```bash
# Run diagnostic to identify issue
python tests/diagnose.py
```

Common causes:
1. WordPress authentication failed (401/403)
2. Articles filtered as low priority
3. Insufficient content in RSS feeds

See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for solutions.

### Where are the logs?
```
GitHub → Actions → Latest Run → "Run news bot" step
```

See [`docs/WHERE_ARE_LOGS.md`](docs/WHERE_ARE_LOGS.md) for detailed guide.

## 🔒 Security

- ✅ No hardcoded secrets
- ✅ All keys in GitHub Secrets
- ✅ `.env` in `.gitignore`
- ✅ WordPress app passwords (not regular passwords)
- ✅ HTTPS-only API calls

See [`docs/SECURITY.md`](docs/SECURITY.md) for security guidelines.

## 📈 Expected Results

### Traffic
- **Month 1:** 10,000+ visitors
- **Month 2:** 25,000+ visitors
- **Month 3:** 50,000+ visitors

### Content
- **80 articles/day** = 2,400 articles/month
- **Each article:** 800-1200 words
- **All articles:** Betting tips + 1xbet.com mention

### SEO
- Google Analytics tracking
- Schema.org markup
- Trending keywords integration
- Internal linking

## 🛠️ Technology Stack

- **Language:** Python 3.11
- **Automation:** GitHub Actions
- **CMS:** WordPress (REST API)
- **AI Content:** OpenRouter (DeepSeek v3)
- **AI Images:** Cloudflare Flux
- **Keywords:** Serper API
- **Analytics:** Google Analytics 4

## 📝 License

This project is for educational purposes. Ensure compliance with:
- WordPress Terms of Service
- API provider terms
- Gambling advertising regulations in your jurisdiction
- Copyright laws for content and images

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests: `pytest tests/ -v`
5. Submit pull request

## 📞 Support

1. Check [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)
2. Run `python tests/diagnose.py`
3. Review GitHub Actions logs
4. Open an issue with diagnostic output

## 🎯 Roadmap

- [x] Basic RSS fetching
- [x] Priority filtering
- [x] AI content generation
- [x] Betting tips integration
- [x] AI image generation
- [x] WordPress publishing
- [x] GitHub Actions automation
- [x] Comprehensive testing
- [ ] Multi-language support
- [ ] Advanced SEO features
- [ ] Performance analytics dashboard

## ⚠️ Disclaimer

This bot is designed for sports news publishing with betting content. Ensure compliance with:
- Local gambling advertising laws
- Age restrictions (18+)
- Responsible gambling guidelines
- Content licensing requirements

Always include appropriate disclaimers and age warnings on betting content.

---

**Repository:** https://github.com/Rivitnp/Sport-News-Automation-Powerhouse

**Status:** ✅ Production Ready

**Last Updated:** 2024
