"""
APIFree.ai Image Generation Client
Z Image Turbo - High-speed SDXL-based image generation
Cost: $0.004 per image
"""

import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from utils import logger

class APIFreeClient:
    def __init__(self, api_key=None):
        """Initialize APIFree.ai client"""
        import os
        self.api_key = api_key or os.getenv('APIFREE_API_KEY')
        self.base_url = "https://api.apifree.ai"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("APIFree.ai not configured (no API key)")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def generate_image(self, prompt, negative_prompt="", width=1280, height=720, num_inference_steps=8):
        """
        Generate image using Z Image Turbo
        
        Args:
            prompt: Text description of the image
            negative_prompt: What to avoid in the image
            width: Image width (64-4096, default 1280 for 16:9)
            height: Image height (64-4096, default 720 for 16:9)
            num_inference_steps: Inference steps (1-200, default 8 for speed)
        
        Returns:
            bytes: Image data (PNG format)
        """
        if not self.enabled:
            logger.error("APIFree.ai not configured")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Submit request
        payload = {
            "model": "tongyi-mai/z-image-turbo",
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_images": 1,
            "num_inference_steps": num_inference_steps
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            # Submit generation request
            logger.info(f"Submitting image generation to APIFree.ai...")
            submit_resp = requests.post(
                f"{self.base_url}/v1/image/submit",
                headers=headers,
                json=payload,
                timeout=30
            )
            submit_resp.raise_for_status()
            
            submit_data = submit_resp.json()
            
            if submit_data.get("code") != 200:
                logger.error(f"APIFree.ai submission failed: {submit_data.get('code_msg')}")
                return None
            
            request_id = submit_data["resp_data"]["request_id"]
            logger.info(f"Request submitted. ID: {request_id}")
            
            # Step 2: Poll for result (max 30 seconds)
            max_attempts = 15  # 15 attempts × 2 seconds = 30 seconds max
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(2)  # Wait 2 seconds between checks
                attempt += 1
                
                # Check status
                result_url = f"{self.base_url}/v1/image/{request_id}/result"
                result_resp = requests.get(result_url, headers=headers, timeout=10)
                result_resp.raise_for_status()
                
                result_data = result_resp.json()
                
                if result_data.get("code") != 200:
                    logger.error(f"APIFree.ai check failed: {result_data.get('code_msg')}")
                    return None
                
                status = result_data["resp_data"]["status"]
                
                if status == "success":
                    # Get image URL
                    image_list = result_data["resp_data"]["image_list"]
                    if not image_list:
                        logger.error("No images in response")
                        return None
                    
                    image_url = image_list[0]
                    cost = result_data["resp_data"]["usage"]["cost"]
                    
                    logger.info(f"Image generated successfully (cost: ${cost})")
                    
                    # Download image
                    img_resp = requests.get(image_url, timeout=30)
                    img_resp.raise_for_status()
                    
                    image_data = img_resp.content
                    logger.info(f"Downloaded image: {len(image_data)/1024:.1f}KB")
                    
                    return image_data
                
                elif status in ["error", "failed"]:
                    error_msg = result_data["resp_data"].get("error", "Unknown error")
                    logger.error(f"Image generation failed: {error_msg}")
                    return None
                
                elif status in ["queuing", "processing"]:
                    logger.info(f"Status: {status}... (attempt {attempt}/{max_attempts})")
                    continue
                
                else:
                    logger.warning(f"Unknown status: {status}")
                    continue
            
            # Timeout
            logger.error(f"Image generation timeout after {max_attempts * 2} seconds")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"APIFree.ai request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"APIFree.ai error: {e}")
            return None
    
    def generate_sports_image(self, title, article_type="match"):
        """
        Generate context-aware sports image based on article title and type
        CUTE VECTOR STYLE with text support - optimized for Z Image Turbo
        16:9 aspect ratio (1280x720) for featured images
        
        Args:
            title: Article title (will be analyzed for teams, players, context)
            article_type: Type of article - "match", "news", "political", "transfer", "injury"
        
        Returns:
            bytes: Image data
        """
        title_lower = title.lower()
        
        # Detect article type from title if not specified
        if article_type == "match":
            if any(kw in title_lower for kw in ['boycott', 'ban', 'suspended', 'controversy', 'protest', 'political']):
                article_type = "political"
            elif any(kw in title_lower for kw in ['transfer', 'signs', 'joins', 'deal', 'contract', '£', '$']):
                article_type = "transfer"
            elif any(kw in title_lower for kw in ['injury', 'injured', 'ruled out', 'sidelined', 'fitness']):
                article_type = "injury"
            elif any(kw in title_lower for kw in ['vs', 'v ', 'beat', 'defeat', 'win', 'loss', 'draw', 'final', 'semi-final']):
                article_type = "match"
            else:
                article_type = "news"
        
        # Extract context from title for better image matching
        
        # FOOTBALL TEAMS - Extract team names and colors
        football_teams = {
            'liverpool': ('red', 'Liverpool'),
            'manchester united': ('red', 'Man United'),
            'manchester city': ('sky blue', 'Man City'),
            'chelsea': ('blue', 'Chelsea'),
            'arsenal': ('red', 'Arsenal'),
            'tottenham': ('white', 'Tottenham'),
            'aston villa': ('claret and blue', 'Aston Villa'),
            'villa': ('claret and blue', 'Aston Villa'),
            'newcastle': ('black and white', 'Newcastle'),
            'barcelona': ('blue and red', 'Barcelona'),
            'real madrid': ('white', 'Real Madrid'),
            'bayern': ('red', 'Bayern'),
            'psg': ('blue', 'PSG'),
        }
        
        # CRICKET TEAMS - Extract team names and colors
        cricket_teams = {
            'india': ('blue', 'India'),
            'pakistan': ('green', 'Pakistan'),
            'australia': ('yellow', 'Australia'),
            'england': ('blue', 'England'),
            'south africa': ('green', 'South Africa'),
            'new zealand': ('black', 'New Zealand'),
            'sri lanka': ('blue', 'Sri Lanka'),
            'west indies': ('maroon', 'West Indies'),
            'bangladesh': ('green', 'Bangladesh'),
            'afghanistan': ('blue', 'Afghanistan'),
            'italy': ('blue', 'Italy'),
        }
        
        # Extract player names for personalization
        player_keywords = ['kohli', 'rohit', 'bumrah', 'dhoni', 'babar', 'miller', 'elliott', 'salah', 'haaland', 'mbappe']
        found_player = None
        for player in player_keywords:
            if player in title_lower:
                found_player = player.title()
                break
        
        # Extract key details from title for text overlay
        key_details = []
        
        # Extract scores/numbers (e.g., "£35M", "3-1", "89 runs")
        import re
        numbers = re.findall(r'[\d]+[-/][\d]+|£[\d]+[MK]?|\d+\s*runs?|\d+\s*wickets?|\d+\s*goals?', title, re.IGNORECASE)
        if numbers:
            key_details.extend(numbers[:2])  # Max 2 numbers
        
        # Extract event type keywords
        event_keywords = ['final', 'semi-final', 'quarter-final', 'debut', 'boost', 'cleared', 'puzzle', 'showdown', 'clash', 'thriller']
        for keyword in event_keywords:
            if keyword in title_lower:
                key_details.append(keyword.title())
                break
        
        # Detect sport and context
        is_cricket = any(kw in title_lower for kw in ['cricket', 'ipl', 't20', 'test', 'odi', 'wicket', 'batting', 'bowling', 'world cup'])
        is_football = any(kw in title_lower for kw in ['football', 'soccer', 'premier league', 'champions league', 'ucl', 'goal', 'villa', 'liverpool'])
        
        # CRICKET IMAGE GENERATION
        if is_cricket:
            # Find teams mentioned
            teams_found = []
            team_colors = []
            for team_key, (color, name) in cricket_teams.items():
                if team_key in title_lower:
                    teams_found.append(name)
                    team_colors.append(color)
            
            # Build context-aware prompt based on article type
            if teams_found:
                teams_text = ' vs '.join(teams_found[:2]) if len(teams_found) >= 2 else teams_found[0]
                colors_text = ', '.join(team_colors[:2]) if team_colors else 'blue, green'
            else:
                teams_text = 'Cricket'
                colors_text = 'blue, green, white'
            
            # Add player context if found
            player_text = f" featuring {found_player}" if found_player else ""
            
            # Tournament context
            if 't20 world cup' in title_lower or 't20 wc' in title_lower:
                tournament = 'T20 World Cup'
            elif 'world cup' in title_lower:
                tournament = 'World Cup'
            elif 'ipl' in title_lower:
                tournament = 'IPL'
            elif 't20' in title_lower:
                tournament = 'T20'
            elif 'test' in title_lower:
                tournament = 'Test Match'
            else:
                tournament = 'Cricket'
            
            # Build detailed text overlay
            text_elements = [teams_text, tournament]
            if key_details:
                text_elements.extend(key_details[:2])
            text_overlay = ' | '.join(text_elements)
            
            # ARTICLE TYPE-SPECIFIC PROMPTS
            if article_type == "political":
                # Political/boycott/controversy - show flags, empty stadium, or diplomatic scene
                prompt = f"News illustration for {tournament} cricket controversy, flat design style, 16:9 widescreen format. Show {teams_text} flags or emblems with diplomatic/political theme. Empty cricket stadium or crossed-out match poster. Serious news graphic aesthetic with {colors_text} team colors. Large bold text overlay at top: '{text_overlay}' in modern sans-serif font. Clean professional news broadcast style, vector art, flat illustration, 2D design, no players, no match action, editorial illustration."
            
            elif article_type == "transfer":
                # Transfer/signing - show player with new team jersey
                prompt = f"Sports news illustration for cricket transfer, flat design style, 16:9 widescreen format. Cartoon cricketer in new team jersey ({colors_text}) holding bat, with team logo/emblem. Contract signing theme with handshake or pen. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Bright team colors ({colors_text}), clean horizontal composition, vector art, flat illustration, 2D design, minimal details."
            
            elif article_type == "injury":
                # Injury news - show medical/fitness theme
                prompt = f"Sports news illustration for cricket injury update, flat design style, 16:9 widescreen format. Cartoon cricketer in team jersey ({colors_text}) with medical/fitness theme (ice pack, physio table, or fitness equipment). Concerned but hopeful aesthetic. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Team colors ({colors_text}), clean composition, vector art, flat illustration, 2D design."
            
            elif article_type == "match":
                # Match report - show action
                prompt = f"Cute vector illustration of {tournament} cricket match{player_text}, flat design style, 16:9 widescreen format. Cartoon cricketers in team jerseys ({colors_text}) with simplified features playing cricket. One batting, one bowling. Simple stadium with geometric shapes and colorful crowd silhouettes. Large bold text overlay at top showing '{text_overlay}' in modern sans-serif font with clear spacing. Bright vibrant colors ({colors_text}), clean horizontal composition optimized for widescreen. Vector art, flat illustration, 2D design, minimal details."
            
            else:  # news
                # General news - show cricket theme with news aesthetic
                prompt = f"Cricket news illustration for {tournament}, flat design style, 16:9 widescreen format. Cricket theme with {teams_text} elements (jerseys, flags, emblems) in {colors_text} colors. News graphic aesthetic with clean professional look. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Bright team colors, clean horizontal composition, vector art, flat illustration, 2D design, editorial style."
        
        # FOOTBALL IMAGE GENERATION
        elif is_football:
            # Find teams mentioned
            teams_found = []
            team_colors = []
            for team_key, (color, name) in football_teams.items():
                if team_key in title_lower:
                    teams_found.append(name)
                    team_colors.append(color)
            
            # Build context-aware prompt
            if teams_found:
                teams_text = ' vs '.join(teams_found[:2]) if len(teams_found) >= 2 else teams_found[0]
                colors_text = ', '.join(team_colors[:2]) if team_colors else 'red, blue'
            else:
                teams_text = 'Football'
                colors_text = 'red, blue, white'
            
            # Add player context if found
            player_text = f" featuring {found_player}" if found_player else ""
            
            # Tournament context
            if 'champions league' in title_lower or 'ucl' in title_lower:
                tournament = 'Champions League'
            elif 'premier league' in title_lower:
                tournament = 'Premier League'
            elif 'world cup' in title_lower:
                tournament = 'World Cup'
            else:
                tournament = 'Football'
            
            # Build detailed text overlay
            text_elements = [teams_text, tournament]
            if key_details:
                text_elements.extend(key_details[:2])
            text_overlay = ' | '.join(text_elements)
            
            # ARTICLE TYPE-SPECIFIC PROMPTS
            if article_type == "political":
                # Political/boycott/controversy
                prompt = f"News illustration for {tournament} football controversy, flat design style, 16:9 widescreen format. Show {teams_text} flags or emblems with diplomatic/political theme. Empty football stadium or crossed-out match poster. Serious news graphic aesthetic with {colors_text} team colors. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Clean professional news broadcast style, vector art, flat illustration, 2D design, no players, editorial illustration."
            
            elif article_type == "transfer":
                # Transfer/signing
                prompt = f"Sports news illustration for football transfer, flat design style, 16:9 widescreen format. Cartoon footballer in new team jersey ({colors_text}) holding ball, with team logo/emblem. Contract signing theme with handshake or pen. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Bright team colors ({colors_text}), clean horizontal composition, vector art, flat illustration, 2D design."
            
            elif article_type == "injury":
                # Injury news
                prompt = f"Sports news illustration for football injury update, flat design style, 16:9 widescreen format. Cartoon footballer in team jersey ({colors_text}) with medical/fitness theme. Concerned but hopeful aesthetic. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Team colors ({colors_text}), vector art, flat illustration, 2D design."
            
            elif article_type == "match":
                # Match report
                prompt = f"Cute vector illustration of {tournament} football match{player_text}, flat design style, 16:9 widescreen format. Cartoon players in team jerseys ({colors_text}) with simplified features kicking oversized ball. Simple stadium with geometric shapes and colorful crowd patterns. Large bold text overlay at top showing '{text_overlay}' in modern sans-serif font with clear spacing. Vibrant team colors ({colors_text}), clean horizontal composition optimized for widescreen. Vector art, flat illustration, 2D design, minimal details."
            
            else:  # news
                # General news
                prompt = f"Football news illustration for {tournament}, flat design style, 16:9 widescreen format. Football theme with {teams_text} elements (jerseys, flags, emblems) in {colors_text} colors. News graphic aesthetic. Large bold text overlay: '{text_overlay}' in modern sans-serif font. Bright team colors, vector art, flat illustration, 2D design, editorial style."
        
        # GENERIC SPORTS FALLBACK
        else:
            text_overlay = 'Sports News'
            if key_details:
                text_overlay += ' | ' + ' | '.join(key_details[:2])
            
            prompt = f"Cute vector illustration of sports event, flat design style, 16:9 widescreen format. Cartoon athletes in team uniforms with simplified features competing. Simple stadium with geometric shapes and colorful crowd patterns. Large bold text overlay at top showing '{text_overlay}' in modern sans-serif font with clear spacing. Bright vibrant colors (blue, red, yellow, green), energetic horizontal composition optimized for widescreen. Vector art, flat illustration, 2D design, clean simple shapes, no photorealism, no 3D effects, no realistic textures."
        
        # NEGATIVE PROMPT - What to avoid (applies to all images)
        negative_prompt = "photorealistic, realistic photo, 3D render, complex details, realistic textures, shadows, gradients, photography, camera, lens, depth of field, bokeh, blurry, noisy, grainy, dark, gloomy, scary, violent, blood, weapons, text errors, spelling mistakes, distorted text, unreadable text, watermark, signature, vertical composition, portrait orientation"
        
        return self.generate_image(prompt, negative_prompt=negative_prompt, width=1280, height=720, num_inference_steps=8)
