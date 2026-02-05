#!/usr/bin/env python3
"""Debug Flux API to understand the exact error"""

import os
import sys
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
TOKEN = os.getenv('CLOUDFLARE_TOKEN')

print("=" * 60)
print("FLUX API DEBUGGING")
print("=" * 60)

# Test different Flux configurations
test_configs = [
    {
        "name": "Original (1200x672, 4 steps)",
        "data": {
            "prompt": "professional cricket stadium with players in action",
            "width": 1200,
            "height": 672,
            "num_steps": 4
        }
    },
    {
        "name": "Standard (1024x768, 4 steps)",
        "data": {
            "prompt": "professional cricket stadium with players in action",
            "width": 1024,
            "height": 768,
            "num_steps": 4
        }
    },
    {
        "name": "Without dimensions",
        "data": {
            "prompt": "professional cricket stadium with players in action",
            "num_steps": 4
        }
    },
    {
        "name": "Minimal (prompt only)",
        "data": {
            "prompt": "professional cricket stadium with players in action"
        }
    }
]

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
headers = {"Authorization": f"Bearer {TOKEN}"}

for config in test_configs:
    print(f"\n{'=' * 60}")
    print(f"TEST: {config['name']}")
    print(f"{'=' * 60}")
    print(f"Data: {json.dumps(config['data'], indent=2)}")
    
    try:
        resp = requests.post(url, headers=headers, json=config['data'], timeout=30)
        print(f"\nStatus: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type', 'Unknown')}")
        
        if resp.status_code == 200:
            if resp.headers.get('content-type', '').startswith('image/'):
                print(f"✅ SUCCESS - Binary image: {len(resp.content)/1024:.1f}KB")
            else:
                result = resp.json()
                if 'result' in result and 'image' in result['result']:
                    print(f"✅ SUCCESS - Base64 image in JSON")
                else:
                    print(f"Response: {json.dumps(result, indent=2)[:500]}")
        else:
            print(f"❌ FAILED")
            print(f"Response: {resp.text[:500]}")
            
            # Try to parse error
            try:
                error = resp.json()
                print(f"\nError details:")
                print(json.dumps(error, indent=2))
            except:
                pass
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "=" * 60)
print("DEBUGGING COMPLETE")
print("=" * 60)
