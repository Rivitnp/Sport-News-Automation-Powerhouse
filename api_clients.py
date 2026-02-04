import requests, io, base64
from tenacity import retry, stop_after_attempt, wait_exponential
from utils import logger, validate_env
from PIL import Image
import pillow_avif

class SerperClient:
    def __init__(self):
        self.key_main = validate_env('SERPER_KEY_MAIN')
        self.key_backup = validate_env('SERPER_KEY_BACKUP', False)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'})
        self.calls = 0

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_trends(self, query, location="Nepal India"):
        """Get trending news with keyword extraction (Nepal/India focus)"""
        self.calls += 1
        if self.calls > 2 and self.key_backup:
            self.key_main, self.key_backup = self.key_backup, self.key_main
            logger.info("Rotated to backup Serper key")
        
        params = {
            "q": f"{query} {location}",
            "tbm": "nws",
            "num": 10,  # Get more for better filtering
            "api_key": self.key_main,
            "gl": "np",  # Nepal geo-location
            "hl": "en"   # English language
        }
        resp = self.session.post("https://google.serper.dev/search", json=params, timeout=10)
        resp.raise_for_status()
        news = resp.json().get('news', [])
        
        # Filter for cricket/football priority
        priority_news = []
        for r in news:
            title_lower = r['title'].lower()
            if any(sport in title_lower for sport in ['cricket', 'football', 'soccer', 'ipl', 'ucl']):
                priority_news.append(r)
        
        # Use all news if no priority matches
        final_news = priority_news if priority_news else news
        
        logger.info(f"Serper returned {len(final_news)} priority articles from {len(news)} total")
        return [{'title': r['title'], 'link': r.get('link', ''), 'source': r.get('source', '')} for r in final_news[:5]]

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=8))
    def search_news(self, query):
        """Search for specific news articles"""
        params = {"q": query, "tbm": "nws", "num": 10, "api_key": self.key_main}
        resp = self.session.post("https://google.serper.dev/search", json=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get('news', [])

class OpenRouterClient:
    def __init__(self):
        self.api_key = validate_env('OPENROUTER_API_KEY')
        self.model = validate_env('OPENROUTER_MODEL', False) or 'deepseek/deepseek-v3:free'
        self.session = requests.Session()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def generate(self, prompt, max_tokens=4000):
        """Generate content using OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
            "X-Title": "Nepal Sports News Bot"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        resp = self.session.post("https://openrouter.ai/api/v1/chat/completions", 
                                headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
        logger.info(f"Generated {len(content)} chars with {self.model}")
        return content

class CloudflareClient:
    def __init__(self):
        self.account_id = validate_env('CLOUDFLARE_ACCOUNT_ID', False)
        self.token = validate_env('CLOUDFLARE_TOKEN', False)
        self.enabled = bool(self.account_id and self.token)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=8))
    def generate_image(self, prompt, width=1200, height=675):
        """Generate copyright-free image using Cloudflare Flux for sports news"""
        if not self.enabled:
            logger.warning("Cloudflare not configured, skipping image generation")
            return None
        
        # Enhance prompt for sports news context
        sport_keywords = ['cricket', 'football', 'soccer', 'ipl', 'ucl', 'premier league']
        enhanced_prompt = prompt.lower()
        
        # Detect sport type and create better prompt
        if any(kw in enhanced_prompt for kw in ['cricket', 'ipl']):
            image_prompt = f"Professional cricket match action photo, stadium atmosphere, dynamic sports photography, high quality, realistic, {prompt[:80]}"
        elif any(kw in enhanced_prompt for kw in ['football', 'soccer', 'ucl', 'premier league']):
            image_prompt = f"Professional football match action photo, stadium atmosphere, dynamic sports photography, high quality, realistic, {prompt[:80]}"
        else:
            image_prompt = f"Professional sports news photo, stadium atmosphere, dynamic action, high quality, realistic, {prompt[:80]}"
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "prompt": image_prompt,
            "width": width,
            "height": height,
            "num_steps": 4
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            
            # Handle binary response
            if resp.headers.get('content-type', '').startswith('image/'):
                logger.info(f"Generated copyright-free image ({len(resp.content)/1024:.1f}KB)")
                return resp.content
            
            # Handle JSON response with base64
            result = resp.json()
            if 'result' in result and 'image' in result['result']:
                b64_data = result['result']['image']
                image_bytes = base64.b64decode(b64_data)
                logger.info(f"Generated copyright-free image ({len(image_bytes)/1024:.1f}KB)")
                return image_bytes
            
            logger.warning("Unexpected Cloudflare response format")
            return None
        except Exception as e:
            logger.error(f"Cloudflare image generation failed: {e}")
            return None

class WordPressClient:
    def __init__(self):
        self.url = validate_env('WP_URL').rstrip('/')
        self.username = validate_env('WP_USERNAME')
        self.password = validate_env('WP_APP_PASSWORD')
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({'Content-Type': 'application/json'})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def upload_media(self, image_data, filename='image.avif'):
        """Upload image to WordPress media library"""
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'image/avif'
        }
        resp = self.session.post(
            f"{self.url}/wp-json/wp/v2/media",
            headers=headers,
            data=image_data,
            timeout=30
        )
        resp.raise_for_status()
        media_id = resp.json()['id']
        logger.info(f"Uploaded media ID: {media_id}")
        return media_id

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def create_post(self, title, content, featured_media=None, categories=None, tags=None):
        """Create WordPress post"""
        data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'categories': categories or [],
            'tags': tags or []
        }
        if featured_media:
            data['featured_media'] = featured_media
        
        resp = self.session.post(f"{self.url}/wp-json/wp/v2/posts", json=data, timeout=30)
        resp.raise_for_status()
        post_id = resp.json()['id']
        post_url = resp.json()['link']
        logger.info(f"Created post ID: {post_id} at {post_url}")
        return post_id, post_url

def optimize_image(image_data, max_size_mb=2):
    """Optimize image to AVIF format with size limit"""
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Resize if too large
        max_dimension = 1200
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save as AVIF
        output = io.BytesIO()
        img.save(output, 'AVIF', quality=85)
        result = output.getvalue()
        
        # Check size
        if len(result) > max_size_mb * 1024 * 1024:
            logger.warning(f"Image too large ({len(result)/1024/1024:.1f}MB), reducing quality")
            output = io.BytesIO()
            img.save(output, 'AVIF', quality=70)
            result = output.getvalue()
        
        logger.info(f"Optimized image to {len(result)/1024:.1f}KB")
        return result
    except Exception as e:
        logger.error(f"Image optimization failed: {e}")
        return None
