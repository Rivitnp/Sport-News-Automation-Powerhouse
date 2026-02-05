# Sports News Automation Bot

Automated sports news bot that publishes articles to WordPress with AI-generated content and images.

## Features

- Full article extraction from RSS feeds
- AI content generation with fact-checking
- Automated image generation
- SEO optimization
- WordPress integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your API keys.

### 3. Run

```bash
python3 src/news_bot.py
```

## Configuration

Edit `src/config.py` to customize:
- RSS feeds
- Priority scoring
- Processing limits
- Article length requirements

## GitHub Actions

The bot runs automatically via GitHub Actions. Configure secrets in repository settings.

## License

MIT License
