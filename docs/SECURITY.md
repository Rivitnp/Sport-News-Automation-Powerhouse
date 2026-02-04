# Security

## Secrets Management

All sensitive credentials are stored in **GitHub Secrets** (encrypted), never in code.

### How It Works

```python
# ✅ SAFE - Credentials from encrypted GitHub Secrets
WP_USERNAME = os.getenv('WP_USERNAME')
WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD')
SERPER_KEY_MAIN = os.getenv('SERPER_KEY_MAIN')
```

### GitHub Secrets Are:
- ✅ Encrypted at rest
- ✅ Never exposed in logs
- ✅ Not visible in public repo
- ✅ Only accessible during workflow runs

## What's Safe to Commit

✅ **Safe:**
- Python code (no secrets)
- Configuration files
- Documentation
- `.env.example` (template only)

❌ **NEVER commit:**
- `.env` file (actual secrets)
- API keys
- Passwords
- Database files with sensitive data

## Public Repo Safety

Your repo can be public because:
1. No secrets in code
2. All credentials in GitHub Secrets
3. `.gitignore` blocks sensitive files
4. Logs don't expose secrets

## Best Practices

1. Use GitHub Secrets for all credentials
2. Never hardcode API keys
3. Keep `.env` in `.gitignore`
4. Rotate keys periodically
5. Use WordPress application passwords (not main password)

## If Secrets Are Exposed

1. Immediately revoke/rotate all keys
2. Delete exposed commits from history
3. Update GitHub Secrets with new keys
4. Check for unauthorized access

## Questions?

Your secrets are safe with GitHub Actions + GitHub Secrets encryption.