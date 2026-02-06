"""
ThumbnailSpec Builder - Structured image generation specs
Based on Image_Guide.md v2.0 for Z-Image Turbo optimization
"""

import json
from typing import Dict, Optional
from utils import logger


class ThumbnailSpecBuilder:
    """
    Build structured ThumbnailSpec JSON for perfect image generation.
    Follows the Image_Guide.md v2.0 methodology.
    """
    
    # Template definitions
    TEMPLATES = {
        "lineup_5": "lineup_5",
        "symbolic": "symbolic",
        "action_moment": "action_moment"
    }
    
    # Sport-specific color mappings
    TEAM_COLORS = {
        # Cricket
        "india": "blue and white",
        "pakistan": "green and white",
        "australia": "yellow and green",
        "england": "blue and white",
        "south africa": "green and gold",
        "new zealand": "black and white",
        "sri lanka": "blue and gold",
        "west indies": "maroon and gold",
        "bangladesh": "green and red",
        "afghanistan": "blue and red",
        
        # Football
        "liverpool": "red and white",
        "manchester united": "red and white",
        "manchester city": "sky blue and white",
        "chelsea": "blue and white",
        "arsenal": "red and white",
        "barcelona": "blue and red",
        "real madrid": "white and gold",
        "bayern": "red and white",
        "psg": "navy blue and red",
        "juventus": "black and white",
    }
    
    @staticmethod
    def detect_sport(title: str, content: str = "") -> str:
        """Detect sport from title and content"""
        text = f"{title} {content}".lower()
        
        if any(kw in text for kw in ['cricket', 'ipl', 't20', 'test', 'odi', 'wicket', 'batting', 'bowling']):
            return "cricket"
        elif any(kw in text for kw in ['football', 'soccer', 'premier league', 'champions league', 'ucl', 'goal']):
            return "football"
        elif any(kw in text for kw in ['basketball', 'nba', 'ncaa', 'dunk', 'three-pointer']):
            return "basketball"
        elif any(kw in text for kw in ['ufc', 'mma', 'boxing', 'punch', 'knockout']):
            return "ufc"
        elif any(kw in text for kw in ['f1', 'formula', 'racing', 'driver', 'pit stop']):
            return "f1"
        else:
            return "sports"
    
    @staticmethod
    def detect_news_type(title: str, content: str = "") -> str:
        """Detect news type from title and content"""
        text = f"{title} {content}".lower()
        
        if any(kw in text for kw in ['boycott', 'ban', 'suspended', 'controversy', 'protest', 'political', 'diplomatic']):
            return "political"
        elif any(kw in text for kw in ['transfer', 'signs', 'joins', 'deal', 'contract', '£', 'move']):
            return "transfer"
        elif any(kw in text for kw in ['injury', 'injured', 'ruled out', 'sidelined', 'fitness', 'recovery']):
            return "injury"
        elif any(kw in text for kw in ['vs', 'v ', 'beat', 'defeat', 'win', 'loss', 'draw', 'final', 'semi-final', 'match']):
            return "matchup"
        elif any(kw in text for kw in ['record', 'milestone', 'century', 'hat-trick', 'performance', 'score']):
            return "performance"
        else:
            return "news"
    
    @staticmethod
    def extract_teams(title: str) -> tuple:
        """Extract team names from title"""
        text = title.lower()
        
        # Look for "Team A vs Team B" pattern
        import re
        vs_pattern = r'(\w+(?:\s+\w+)?)\s+(?:vs|v\.?|versus)\s+(\w+(?:\s+\w+)?)'
        match = re.search(vs_pattern, text, re.IGNORECASE)
        
        if match:
            team1 = match.group(1).strip().title()
            team2 = match.group(2).strip().title()
            return (team1, team2)
        
        return ("Team A", "Team B")
    
    @staticmethod
    def get_team_color(team_name: str) -> str:
        """Get team color from mapping"""
        team_lower = team_name.lower()
        
        for team_key, color in ThumbnailSpecBuilder.TEAM_COLORS.items():
            if team_key in team_lower:
                return color
        
        # Default colors by sport
        if any(kw in team_lower for kw in ['cricket', 'india', 'pakistan']):
            return "blue and white"
        elif any(kw in team_lower for kw in ['football', 'soccer']):
            return "red and white"
        else:
            return "blue and white"
    
    @staticmethod
    def build_spec(
        title: str,
        content: str = "",
        sport: Optional[str] = None,
        news_type: Optional[str] = None,
        template: Optional[str] = None
    ) -> Dict:
        """
        Build complete ThumbnailSpec JSON from article data.
        
        Args:
            title: Article headline
            content: Article body (optional, for context)
            sport: Override detected sport
            news_type: Override detected news type
            template: Override template selection
        
        Returns:
            Dict: Complete ThumbnailSpec JSON
        """
        
        # Auto-detect if not provided
        detected_sport = sport or ThumbnailSpecBuilder.detect_sport(title, content)
        detected_news_type = news_type or ThumbnailSpecBuilder.detect_news_type(title, content)
        
        # Extract teams
        team1, team2 = ThumbnailSpecBuilder.extract_teams(title)
        
        # Get team colors
        color1 = ThumbnailSpecBuilder.get_team_color(team1)
        color2 = ThumbnailSpecBuilder.get_team_color(team2)
        
        # Select template based on sport and news type
        if template is None:
            if detected_news_type == "political":
                template = "symbolic"
            elif detected_news_type == "performance" or detected_news_type == "injury":
                template = "action_moment"
            elif detected_news_type == "matchup":
                template = "lineup_5"
            else:
                template = "symbolic"
        
        # Build spec
        spec = {
            "sport": detected_sport,
            "news_type": detected_news_type,
            "headline": title[:40].upper(),  # Max 40 chars, uppercase
            "subhead": detected_news_type.upper() if detected_news_type != "matchup" else "",
            "layout_template": template,
            "aspect_ratio": "16:9",
            "dimensions": {
                "width": 1280,
                "height": 720
            },
            "team_left": {
                "name": team1,
                "label": f"{team1.upper()} (HOME)",
                "colors": color1
            },
            "team_right": {
                "name": team2,
                "label": f"{team2.upper()} (AWAY)",
                "colors": color2
            },
            "style": "3D action-figure poster" if template == "lineup_5" else "cinematic editorial still-life",
            "background": "dark gradient studio" if template == "lineup_5" else "stadium night floodlights",
            "must_include": ["headline", "team labels"] if template == "lineup_5" else ["headline"],
            "must_avoid": ["team logos", "brand marks", "real player faces", "extra text", "watermarks"]
        }
        
        logger.info(f"Built ThumbnailSpec: {detected_sport} {detected_news_type} using {template} template")
        
        return spec
    
    @staticmethod
    def to_json(spec: Dict) -> str:
        """Convert spec to JSON string"""
        return json.dumps(spec, indent=2)
    
    @staticmethod
    def validate_spec(spec: Dict) -> bool:
        """Validate ThumbnailSpec structure"""
        required_fields = [
            "sport", "news_type", "headline", "layout_template",
            "dimensions", "team_left", "team_right", "must_avoid"
        ]
        
        for field in required_fields:
            if field not in spec:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate headline length
        if len(spec["headline"]) > 40:
            logger.warning(f"Headline too long ({len(spec['headline'])} chars), truncating to 40")
            spec["headline"] = spec["headline"][:40]
        
        # Validate dimensions
        if spec["dimensions"]["width"] != 1280 or spec["dimensions"]["height"] != 720:
            logger.warning("Non-standard dimensions, resetting to 1280x720")
            spec["dimensions"] = {"width": 1280, "height": 720}
        
        return True


# Example usage
if __name__ == "__main__":
    # Example 1: Cricket matchup
    spec1 = ThumbnailSpecBuilder.build_spec(
        title="India vs Pakistan T20 World Cup Final",
        content="India faces Pakistan in the T20 World Cup final...",
    )
    print("Cricket Matchup Spec:")
    print(ThumbnailSpecBuilder.to_json(spec1))
    print()
    
    # Example 2: Football transfer
    spec2 = ThumbnailSpecBuilder.build_spec(
        title="Mbappe Signs for Real Madrid - £200M Deal",
        content="Kylian Mbappe has completed his transfer to Real Madrid...",
    )
    print("Football Transfer Spec:")
    print(ThumbnailSpecBuilder.to_json(spec2))
    print()
    
    # Example 3: Cricket injury
    spec3 = ThumbnailSpecBuilder.build_spec(
        title="Bumrah Ruled Out of IPL with Injury",
        content="Jasprit Bumrah has been ruled out of the IPL...",
    )
    print("Cricket Injury Spec:")
    print(ThumbnailSpecBuilder.to_json(spec3))
