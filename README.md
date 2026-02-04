# Sports News Automation Bot

Automated sports news aggregation and publishing system for GitHub Actions.

## Features

- RSS feed aggregation from major sports sources
- AI content generation with SEO optimization
- AI-generated images (copyright-free)
- WordPress publishing automation
- Duplicate detection
- Runs automatically on GitHub Actions

## Setup

### 1. Fork Repository

### 2. Add GitHub Secrets

Settings → Secrets and variables → Actions:

**Required:**
- `SERPER_KEY_MAIN` - Serper API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `WP_URL` - WordPress site URL
- `WP_USERNAME` - WordPress username
- `WP_APP_PASSWORD` - WordPress application password

**Optional:**
- `SERPER_KEY_BACKUP` - Backup Serper key
- `CLOUDFLARE_ACCOUNT_ID` - For AI image generation
- `CLOUDFLARE_TOKEN` - Cloudflare API token
- `GA_MEASUREMENT_ID` - Google Analytics ID

### 3. Enable GitHub Actions

Actions tab → Enable workflows

### 4. Run

Workflow runs automatically every 6 hours, or trigger manually.

## Configuration

Edit `config.py` to customize:
- RSS feeds
- Sport priorities
- Keywords
- Processing limits

## Security

✅ All secrets stored in GitHub Secrets (encrypted)
✅ No credentials in code
✅ WordPress app passwords (not main password)
✅ Safe for public repositories

## Cost

$0/month - Runs on free tiers:
- GitHub Actions: 2,000 min/month
- Serper: 2,500 searches/month
- OpenRouter: Free tier available
- Cloudflare: 10,000 requests/day

## License

MIT
