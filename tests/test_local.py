#!/usr/bin/env python3
"""
Local testing script to verify all APIs work before pushing to GitHub
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=" * 60)
print("LOCAL TESTING - Sports News Bot")
print("=" * 60)
print()

# Test 1: Environment Variables
print("✓ Testing Environment Variables...")
required_vars = [
    'SERPER_KEY_MAIN',
    'OPENROUTER_API_KEY',
    'WP_URL',
    'WP_USERNAME',
    'WP_APP_PASSWORD'
]

missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if not value:
        missing_vars.append(var)
        print(f"  ❌ {var}: NOT SET")
    else:
        # Show first 10 chars only for security
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"  ✅ {var}: {masked}")

if missing_vars:
    print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
    print("Please update .env file with your actual values")
    sys.exit(1)

print("\n✅ All required environment variables are set!")
print()

# Test 2: Import Modules
print("✓ Testing Module Imports...")
try:
    from utils import logger, validate_env, init_database
    print("  ✅ utils module imported")
except Exception as e:
    print(f"  ❌ Failed to import utils: {e}")
    sys.exit(1)

try:
    from api_clients import SerperClient, OpenRouterClient, CloudflareClient, WordPressClient
    print("  ✅ api_clients module imported")
except Exception as e:
    print(f"  ❌ Failed to import api_clients: {e}")
    sys.exit(1)

print("\n✅ All modules imported successfully!")
print()

# Test 3: WordPress Connection
print("✓ Testing WordPress Connection...")
try:
    import requests
    wp_url = os.getenv('WP_URL')
    wp_username = os.getenv('WP_USERNAME')
    wp_password = os.getenv('WP_APP_PASSWORD')
    
    # Test REST API availability
    print(f"  Testing: {wp_url}/wp-json/wp/v2/posts")
    resp = requests.get(f"{wp_url}/wp-json/wp/v2/posts", timeout=10)
    if resp.status_code == 200:
        print(f"  ✅ WordPress REST API is accessible")
    else:
        print(f"  ⚠️  WordPress REST API returned: {resp.status_code}")
    
    # Test authentication
    print(f"  Testing authentication...")
    auth_resp = requests.get(
        f"{wp_url}/wp-json/wp/v2/users/me",
        auth=(wp_username, wp_password),
        timeout=10
    )
    if auth_resp.status_code == 200:
        user_data = auth_resp.json()
        print(f"  ✅ Authentication successful! Logged in as: {user_data.get('name', 'Unknown')}")
    else:
        print(f"  ❌ Authentication failed: {auth_resp.status_code}")
        print(f"     Response: {auth_resp.text[:200]}")
        print("\n  Possible issues:")
        print("  - Wrong username or app password")
        print("  - App password not generated correctly")
        print("  - WordPress REST API disabled")
        
except Exception as e:
    print(f"  ❌ WordPress connection failed: {e}")
    print("\n  Please check:")
    print("  - WP_URL is correct (no trailing slash)")
    print("  - WordPress site is accessible")
    print("  - REST API is enabled")

print()

# Test 4: Serper API
print("✓ Testing Serper API...")
try:
    serper = SerperClient()
    trends = serper.get_trends("cricket", location="Nepal")
    if trends:
        print(f"  ✅ Serper API working! Found {len(trends)} trends")
        print(f"     Sample: {trends[0]['title'][:50]}...")
    else:
        print(f"  ⚠️  Serper returned no results (might be normal)")
except Exception as e:
    print(f"  ❌ Serper API failed: {e}")
    print("  Check your SERPER_KEY_MAIN")

print()

# Test 5: OpenRouter API
print("✓ Testing OpenRouter API...")
try:
    or_client = OpenRouterClient()
    test_prompt = "Write a short 50-word summary about cricket."
    result = or_client.generate(test_prompt, max_tokens=100)
    if result:
        print(f"  ✅ OpenRouter API working!")
        print(f"     Generated {len(result)} characters")
        print(f"     Sample: {result[:80]}...")
    else:
        print(f"  ❌ OpenRouter returned empty result")
except Exception as e:
    print(f"  ❌ OpenRouter API failed: {e}")
    print("  Check your OPENROUTER_API_KEY")

print()

# Test 6: Cloudflare (Optional)
print("✓ Testing Cloudflare API (optional)...")
try:
    cf_client = CloudflareClient()
    if cf_client.enabled:
        print(f"  ✅ Cloudflare configured")
        # Don't actually generate image in test (costs quota)
        print(f"     Skipping actual image generation to save quota")
    else:
        print(f"  ⚠️  Cloudflare not configured (optional)")
except Exception as e:
    print(f"  ⚠️  Cloudflare test skipped: {e}")

print()

# Test 7: Create Test Post
print("✓ Testing WordPress Post Creation...")
try:
    wp_client = WordPressClient()
    
    test_title = "TEST POST - Please Delete"
    test_content = "<p>This is a test post created by the news bot. You can safely delete this.</p>"
    
    print(f"  Creating draft post...")
    # Create as draft first
    data = {
        'title': test_title,
        'content': test_content,
        'status': 'draft'  # Draft so it doesn't publish
    }
    
    resp = wp_client.session.post(
        f"{wp_client.url}/wp-json/wp/v2/posts",
        json=data,
        timeout=30
    )
    
    if resp.status_code == 201:
        post_data = resp.json()
        print(f"  ✅ Test post created successfully!")
        print(f"     Post ID: {post_data['id']}")
        print(f"     URL: {post_data['link']}")
        print(f"     Status: {post_data['status']}")
        print(f"\n  You can delete this test post from WordPress admin")
    else:
        print(f"  ❌ Failed to create post: {resp.status_code}")
        print(f"     Response: {resp.text[:300]}")
        
except Exception as e:
    print(f"  ❌ Post creation failed: {e}")
    print("\n  This is the main issue! Check:")
    print("  - WordPress user has 'publish_posts' permission")
    print("  - App password is correct")
    print("  - REST API is enabled")

print()
print("=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
print()
print("Next steps:")
print("1. Fix any ❌ errors shown above")
print("2. Once all tests pass, update GitHub Secrets")
print("3. Run the workflow on GitHub")
print()
