# Quick Setup Guide

## Get API Keys

### Serper API
1. Go to https://serper.dev/
2. Sign up (2,500 searches/month free)
3. Copy API key
4. Save as `SERPER_KEY_MAIN` in GitHub Secrets

### OpenRouter API
1. Go to https://openrouter.ai/
2. Create account
3. Get API key
4. Save as `OPENROUTER_API_KEY` in GitHub Secrets

### WordPress
1. WordPress admin → Users → Profile → Application Passwords
2. Create new application password
3. Save:
   - `WP_URL`: https://yoursite.com
   - `WP_USERNAME`: your username
   - `WP_APP_PASSWORD`: generated password

### Cloudflare (Optional)
1. Go to https://dash.cloudflare.com/
2. Workers & Pages → AI
3. Get Account ID and API token
4. Save as `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_TOKEN`

## Configure GitHub Secrets

Repository → Settings → Secrets and variables → Actions → New secret

Add each secret listed above.

## Enable Workflow

Actions tab → Enable workflows

## Test

Actions → Run workflow manually

Check your WordPress site for new posts.

## Customize

Edit `config.py`:
- RSS feeds
- Sport priorities  
- Keywords
- Processing limits

## Security

✅ All secrets encrypted in GitHub
✅ Never commit credentials to code
✅ Use WordPress app passwords (not main password)
✅ Safe for public repositories
