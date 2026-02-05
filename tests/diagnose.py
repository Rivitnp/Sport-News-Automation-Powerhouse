#!/usr/bin/env python3
"""
Diagnostic script to identify why articles aren't being published
Run this locally with: python tests/diagnose.py
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv()

print("=" * 70)
print("DIAGNOSTIC SCRIPT - Finding Why Articles Aren't Publishing")
print("=" * 70)
print()

# Step 1: Test RSS Feeds
print("STEP 1: Testing RSS Feeds")
print("-" * 70)

try:
    import feedparser
    import requests
    from config import RSS_FEEDS, PRIORITY_SPORTS
    
    print(f"Configured RSS feeds: {len(RSS_FEEDS)}")
    
    for feed_url in RSS_FEEDS:
        print(f"\n  Testing: {feed_url}")
        try:
            # Fetch with requests first
            resp = requests.get(feed_url, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            print(f"    ❌ Failed to fetch: {e}")
            continue
        
        if not feed.entries:
            print(f"    ❌ No entries found!")
            continue
        
        print(f"    ✅ Found {len(feed.entries)} entries")
        
        # Check priority filtering
        priority_count = 0
        for entry in feed.entries[:5]:
            title = entry.title.lower()
            summary = entry.get('summary', '').lower()
            text = f"{title} {summary}"
            
            # Calculate priority
            score = 0
            for sport, priority in PRIORITY_SPORTS.items():
                if sport in text:
                    score += priority
                    break
            
            if score >= 3:
                priority_count += 1
                print(f"       ✓ Priority {score}: {entry.title[:60]}")
            else:
                print(f"       ✗ Low priority {score}: {entry.title[:60]}")
        
        print(f"    Priority articles: {priority_count}/{len(feed.entries[:5])}")
        
except Exception as e:
    print(f"  ❌ RSS test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Step 2: Test WordPress Authentication
print("STEP 2: Testing WordPress Authentication")
print("-" * 70)

try:
    import requests
    
    wp_url = os.getenv('WP_URL', '').rstrip('/')
    wp_username = os.getenv('WP_USERNAME')
    wp_password = os.getenv('WP_APP_PASSWORD')
    
    if not all([wp_url, wp_username, wp_password]):
        print("  ❌ WordPress credentials not set in .env")
    else:
        print(f"  Testing: {wp_url}")
        
        # Test 1: REST API availability
        try:
            resp = requests.get(f"{wp_url}/wp-json/wp/v2/posts", timeout=10)
            print(f"    ✅ REST API accessible (status: {resp.status_code})")
        except Exception as e:
            print(f"    ❌ REST API not accessible: {e}")
        
        # Test 2: Authentication
        try:
            auth_resp = requests.get(
                f"{wp_url}/wp-json/wp/v2/users/me",
                auth=(wp_username, wp_password),
                timeout=10
            )
            
            if auth_resp.status_code == 200:
                user = auth_resp.json()
                print(f"    ✅ Authentication successful!")
                print(f"       User: {user.get('name')}")
                print(f"       Roles: {user.get('roles', [])}")
                
                # Check permissions
                capabilities = user.get('capabilities', {})
                if capabilities.get('publish_posts'):
                    print(f"    ✅ User has 'publish_posts' permission")
                else:
                    print(f"    ❌ User MISSING 'publish_posts' permission!")
                    print(f"       This is why posts aren't publishing!")
                    
            elif auth_resp.status_code == 401:
                print(f"    ❌ Authentication FAILED (401 Unauthorized)")
                print(f"       Wrong username or app password!")
                print(f"       Response: {auth_resp.text[:200]}")
            elif auth_resp.status_code == 403:
                print(f"    ❌ Authentication FAILED (403 Forbidden)")
                print(f"       User doesn't have permission!")
            else:
                print(f"    ❌ Unexpected status: {auth_resp.status_code}")
                print(f"       Response: {auth_resp.text[:200]}")
                
        except Exception as e:
            print(f"    ❌ Auth test failed: {e}")
        
        # Test 3: Try creating a draft post
        print(f"\n  Testing post creation...")
        try:
            test_data = {
                'title': 'DIAGNOSTIC TEST - DELETE ME',
                'content': '<p>This is a diagnostic test post. Safe to delete.</p>',
                'status': 'draft'
            }
            
            create_resp = requests.post(
                f"{wp_url}/wp-json/wp/v2/posts",
                auth=(wp_username, wp_password),
                json=test_data,
                timeout=30
            )
            
            if create_resp.status_code == 201:
                post = create_resp.json()
                print(f"    ✅ Post creation WORKS!")
                print(f"       Post ID: {post['id']}")
                print(f"       URL: {post['link']}")
                print(f"\n    THIS MEANS WORDPRESS IS WORKING!")
                print(f"    The issue is likely with RSS content or Serper API")
            else:
                print(f"    ❌ Post creation FAILED: {create_resp.status_code}")
                print(f"       Response: {create_resp.text[:300]}")
                print(f"\n    THIS IS THE PROBLEM!")
                
                if create_resp.status_code == 401:
                    print(f"       → Wrong app password")
                elif create_resp.status_code == 403:
                    print(f"       → User lacks publish_posts permission")
                elif create_resp.status_code == 400:
                    print(f"       → Invalid request format")
                    
        except Exception as e:
            print(f"    ❌ Post creation test failed: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"  ❌ WordPress test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Step 3: Test Serper API
print("STEP 3: Testing Serper API")
print("-" * 70)

try:
    from api_clients import SerperClient
    
    serper = SerperClient()
    
    # Test with cricket query
    print("  Testing query: 'cricket betting Nepal India'")
    trends = serper.get_trends("cricket betting Nepal India")
    
    if trends:
        print(f"    ✅ Serper returned {len(trends)} results")
        for i, trend in enumerate(trends[:3], 1):
            print(f"       {i}. {trend['title'][:70]}")
    else:
        print(f"    ⚠️  Serper returned 0 results")
        print(f"       This might be normal, but could indicate API issues")
        
except Exception as e:
    print(f"  ❌ Serper test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Step 4: Test OpenRouter
print("STEP 4: Testing OpenRouter API")
print("-" * 70)

try:
    from api_clients import OpenRouterClient
    
    or_client = OpenRouterClient()
    print(f"  Using model: {or_client.model}")
    
    result = or_client.generate("Write one sentence about cricket.", max_tokens=50)
    
    if result:
        print(f"    ✅ OpenRouter working!")
        print(f"       Generated: {result[:100]}")
    else:
        print(f"    ❌ OpenRouter returned empty result")
        
except Exception as e:
    print(f"  ❌ OpenRouter test failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
print()
print("SUMMARY:")
print("--------")
print("If WordPress post creation test PASSED:")
print("  → The issue is with RSS content or article filtering")
print("  → Articles are being skipped due to insufficient content")
print()
print("If WordPress post creation test FAILED:")
print("  → Fix the WordPress authentication issue first")
print("  → Check app password and user permissions")
print()
print("Next steps:")
print("1. Fix any ❌ errors shown above")
print("2. Update GitHub Secrets with correct values")
print("3. Re-run the workflow")
print()
