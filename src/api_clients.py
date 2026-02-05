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
        self.model = validate_env('OPENROUTER_MODEL', False) or 'deepseek/deepseek-chat'
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
    def generate_image(self, prompt, width=1200, height=672):
        """Generate copyright-free image using Cloudflare Flux for sports news"""
        if not self.enabled:
            logger.warning("Cloudflare not configured, skipping image generation")
            return None
        
        # Ensure dimensions are divisible by 8 (Flux requirement)
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        # Create highly specific, relevant prompts based on article title
        enhanced_prompt = prompt.lower()
        
        # Extract key terms from title for better image relevance
        title_lower = prompt.lower()
        
        # Cricket-specific scenarios
        if 'ipl' in title_lower or 'indian premier league' in title_lower:
            image_prompt = "vibrant IPL cricket stadium packed with cheering fans, professional cricketers in colorful team jerseys, intense match action, floodlights, energetic atmosphere, photorealistic sports photography, 8k ultra detailed"
        elif 'test cricket' in title_lower or 'test match' in title_lower:
            image_prompt = "traditional test cricket match, players in white uniforms, green cricket field, classic stadium, professional sports photography, bright daylight, photorealistic, 8k quality"
        elif 't20' in title_lower or 'twenty20' in title_lower:
            image_prompt = "exciting T20 cricket match, dynamic batting action, packed stadium with enthusiastic crowd, colorful team jerseys, floodlit evening match, photorealistic sports photography, 8k ultra detailed"
        elif 'world cup' in title_lower and 'cricket' in title_lower:
            image_prompt = "ICC Cricket World Cup match, international cricket stadium filled with fans, players in national team colors, dramatic match moment, professional sports photography, photorealistic, 8k quality"
        elif any(kw in title_lower for kw in ['cricket', 'batting', 'bowling', 'wicket', 'over']):
            image_prompt = "professional cricket match action, batsman hitting ball, bowler in delivery stride, packed stadium atmosphere, bright daylight, photorealistic sports photography, 8k ultra detailed"
        
        # Football-specific scenarios
        elif 'premier league' in title_lower:
            image_prompt = "English Premier League football match, iconic stadium packed with fans, players in team jerseys competing for ball, intense action moment, professional sports photography, photorealistic, 8k quality"
        elif 'champions league' in title_lower or 'ucl' in title_lower:
            image_prompt = "UEFA Champions League football match, massive European stadium, players in club jerseys, dramatic match action, floodlit evening, photorealistic sports photography, 8k ultra detailed"
        elif 'world cup' in title_lower and 'football' in title_lower:
            image_prompt = "FIFA World Cup football match, international stadium filled with passionate fans, players in national team colors, exciting match moment, professional sports photography, photorealistic, 8k quality"
        elif any(kw in title_lower for kw in ['football', 'soccer', 'goal', 'striker', 'midfielder']):
            image_prompt = "professional football match action, players competing for ball, packed stadium with cheering crowd, dynamic sports moment, bright stadium lights, photorealistic sports photography, 8k ultra detailed"
        
        # Generic sports fallback
        else:
            image_prompt = "professional sports stadium filled with enthusiastic fans, athletes in action, dramatic sporting moment, perfect lighting, photorealistic sports photography, 8k ultra detailed quality"
        
        # Use Flux for high-quality images
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "prompt": image_prompt,
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
    def create_post(self, title, content, featured_media=None, categories=None, tags=None, date=None):
        """Create WordPress post with categories, tags, and date"""
        data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'categories': categories or [],
            'tags': tags or []
        }
        if featured_media:
            data['featured_media'] = featured_media
        if date:
            data['date'] = date  # ISO 8601 format: 2026-02-05T12:00:00
        
        try:
            resp = self.session.post(f"{self.url}/wp-json/wp/v2/posts", json=data, timeout=30)
            resp.raise_for_status()
            post_id = resp.json()['id']
            post_url = resp.json()['link']
            logger.info(f"Created post ID: {post_id} at {post_url}")
            return post_id, post_url
        except requests.exceptions.HTTPError as e:
            # Log detailed error information
            logger.error(f"WordPress API Error: {e}")
            logger.error(f"Status Code: {resp.status_code}")
            logger.error(f"Response: {resp.text[:500]}")
            if resp.status_code == 401:
                logger.error("Authentication failed - check WP_USERNAME and WP_APP_PASSWORD")
            elif resp.status_code == 403:
                logger.error("Permission denied - user needs 'publish_posts' capability")
            raise
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=8))
    def get_categories(self):
        """Get all WordPress categories"""
        try:
            resp = self.session.get(f"{self.url}/wp-json/wp/v2/categories?per_page=100", timeout=10)
            resp.raise_for_status()
            categories = resp.json()
            return {cat['name'].lower(): cat['id'] for cat in categories}
        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            return {}
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=8))
    def get_or_create_tag(self, tag_name):
        """Get existing tag ID or create new tag"""
        try:
            # Search for existing tag
            resp = self.session.get(
                f"{self.url}/wp-json/wp/v2/tags?search={tag_name}",
                timeout=10
            )
            resp.raise_for_status()
            tags = resp.json()
            
            # Return existing tag if found
            for tag in tags:
                if tag['name'].lower() == tag_name.lower():
                    return tag['id']
            
            # Create new tag if not found
            resp = self.session.post(
                f"{self.url}/wp-json/wp/v2/tags",
                json={'name': tag_name},
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()['id']
        except Exception as e:
            logger.error(f"Failed to get/create tag '{tag_name}': {e}")
            return None

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
