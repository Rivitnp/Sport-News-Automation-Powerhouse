#!/usr/bin/env python3
"""
Test script to publish a single article with all critical fixes
Tests the complete workflow: fetch → generate → image → publish
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from news_bot import (
    validate_startup, 
    fetch_rss_articles, 
    process_article,
    init_database
)
from api_clients import SerperClient, CloudflareClient, WordPressClient
from apifree_client import APIFreeClient
from utils import logger

# Load environment variables
load_dotenv()

def main():
    """Test single article generation with all fixes"""
    print("\n" + "="*80)
    print("TESTING SINGLE ARTICLE WITH CRITICAL FIXES")
    print("="*80 + "\n")
    
    try:
        # Validate environment
        print("Step 1: Validating environment...")
        validate_startup()
        print("✅ Environment validated\n")
        
        # Initialize database
        print("Step 2: Initializing database...")
        init_database()
        print("✅ Database initialized\n")
        
        # Initialize clients
        print("Step 3: Initializing API clients...")
        serper = SerperClient()
        apifree_client = APIFreeClient()
        cf_client = CloudflareClient()
        wp_client = WordPressClient()
        print("✅ API clients initialized\n")
        
        # Fetch articles (prioritize feeds with longer summaries)
        print("Step 4: Fetching articles from RSS feeds...")
        articles = fetch_rss_articles(max_articles=20)  # Fetch more to find one with content
        
        if not articles:
            print("❌ No articles found")
            return 1
        
        print(f"✅ Found {len(articles)} articles\n")
        
        # Show top 5 articles
        print("Top 5 articles by priority:")
        for i, article in enumerate(articles[:5], 1):
            print(f"  {i}. [{article['priority']}] {article['title'][:70]}")
        print()
        
        # Try articles until we find one with sufficient content
        print("Step 5: Finding article with sufficient content...\n")
        
        success = False
        for i, article in enumerate(articles, 1):
            print("="*80)
            print(f"TRYING ARTICLE {i}/{len(articles)} (Priority: {article['priority']})")
            print("="*80)
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Link: {article['link'][:80]}...")
            print("="*80 + "\n")
            
            # Process the article
            print("Processing:")
            print("  - Scraping content...")
            print("  - Checking content length...")
            print("  - Generating SEO article with fact-checking...")
            print("  - Detecting article type...")
            print("  - Generating context-aware image...")
            print("  - Publishing to WordPress...\n")
            
            success = process_article(article, serper, apifree_client, cf_client, wp_client)
            
            if success:
                break
            else:
                print(f"⚠️ Article {i} skipped (insufficient content or error)\n")
                if i < len(articles):
                    print("Trying next article...\n")
        
        if success:
            print("\n" + "="*80)
            print("✅ SUCCESS! Article published with all critical fixes")
            print("="*80)
            print("\nQuality Checklist - Please verify on WordPress:")
            print("  [ ] Title is clear and accurate (no misleading phrasing)")
            print("  [ ] Publish date visible at top of article")
            print("  [ ] Correct tournament name (T20 World Cup 2026, not just 'World Cup')")
            print("  [ ] Background section if story is complex")
            print("  [ ] Quotes have attribution (or no quotes if not in source)")
            print("  [ ] No placeholder text like '[pending review]'")
            print("  [ ] Minimum 800 words")
            print("  [ ] Betting disclaimer present")
            print("  [ ] Image matches article type")
            print("  [ ] Image shows correct teams/entities")
            print("  [ ] Featured image present")
            print("  [ ] Categories and tags assigned")
            print("\nCheck the article on your WordPress site!")
            print("="*80 + "\n")
            return 0
        else:
            print("\n" + "="*80)
            print("❌ FAILED - No articles with sufficient content found")
            print("="*80)
            print("\nAll articles had insufficient source content (< 500 chars)")
            print("This is the new quality control working correctly!")
            print("\nOptions:")
            print("  1. Wait for RSS feeds to update with more detailed articles")
            print("  2. Try different RSS feeds with fuller content")
            print("  3. Lower minimum threshold (not recommended - causes hallucination)")
            print("="*80 + "\n")
            return 1
            
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ FATAL ERROR: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
