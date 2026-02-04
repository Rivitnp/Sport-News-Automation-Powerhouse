# Source Code

This folder contains the main application code for the Nepal Sports News Bot.

## Files

### Core Application
- **`news_bot.py`** - Main bot script that orchestrates the entire workflow
  - Fetches RSS feeds
  - Filters articles by priority (cricket/football focus)
  - Scrapes article content
  - Generates SEO-optimized content with betting sections
  - Publishes to WordPress

### API Clients
- **`api_clients.py`** - API client classes for external services
  - `SerperClient` - Google Search API for trending keywords
  - `OpenRouterClient` - AI content generation (DeepSeek v3)
  - `CloudflareClient` - AI image generation (Flux)
  - `WordPressClient` - WordPress REST API for publishing
  - `optimize_image()` - Image optimization to AVIF format

### Configuration
- **`config.py`** - All configuration settings
  - RSS feed URLs (cricket/football sources)
  - Priority scoring for sports
  - Betting triggers and branding (1xbet.com)
  - Processing limits and delays
  - Image and SEO settings

### Utilities
- **`utils.py`** - Helper functions
  - Logging setup
  - Environment variable validation
  - Database operations (duplicate detection)
  - HTML sanitization

## Running the Bot

### Locally
```bash
# Set environment variables in .env file
python src/news_bot.py
```

### In GitHub Actions
The bot runs automatically every 3 hours via `.github/workflows/news-automation.yml`

## Environment Variables Required

```bash
SERPER_KEY_MAIN=your_serper_key
SERPER_KEY_BACKUP=your_backup_key
OPENROUTER_API_KEY=your_openrouter_key
WP_URL=https://yoursite.com
WP_USERNAME=your_wp_username
WP_APP_PASSWORD=your_wp_app_password
CLOUDFLARE_ACCOUNT_ID=your_cf_account_id
CLOUDFLARE_TOKEN=your_cf_token
GA_MEASUREMENT_ID=your_ga_id
```

## Workflow

1. **Fetch** - Get articles from RSS feeds
2. **Filter** - Prioritize cricket/football, skip American sports
3. **Scrape** - Extract full article content (fallback to RSS summary)
4. **Generate** - Create SEO-optimized content with betting tips
5. **Image** - Generate copyright-free AI image with Cloudflare
6. **Publish** - Post to WordPress with featured image
7. **Track** - Mark as processed to avoid duplicates

## Key Features

- ✅ Cricket & Football priority (Nepal/India audience)
- ✅ Automatic betting tips sections with 1xbet.com mentions
- ✅ 18+ disclaimers on all betting content
- ✅ Copyright-free AI-generated images
- ✅ SEO optimization with Google Analytics
- ✅ Duplicate detection
- ✅ Rate limiting and retry logic
- ✅ Comprehensive error logging
