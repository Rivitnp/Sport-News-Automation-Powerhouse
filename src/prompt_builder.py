"""
Prompt Builder - Convert ThumbnailSpec JSON to Z-Image Turbo prompts
Follows the 5-step template structure from Image_Guide.md
"""

import json
from typing import Dict
from utils import logger


class PromptBuilder:
    """
    Build production-ready Z-Image Turbo prompts from ThumbnailSpec JSON.
    
    5-Step Structure:
    1. Format & purpose: "16:9 sports news thumbnail poster…"
    2. Subject layout: "Five generic 3D action-figure style adult players…"
    3. Team coding: "Left two blue/white, right two red/white, center gray…"
    4. Text block: exact quoted strings + font + placement
    5. Hard constraints: "No logos, no watermark, no other text…"
    """
    
    @staticmethod
    def build_lineup_5_prompt(spec: Dict) -> str:
        """
        Build lineup_5_figures template prompt.
        Best for: Basketball, football, cricket matchups with two teams
        """
        
        # Step 1: Format & Purpose
        format_section = "16:9 sports news thumbnail poster, dark gray gradient background, studio lighting, clean floor shadow."
        
        # Step 2: Subject Layout
        sport = spec.get("topic", "sports").lower()
        subject_section = f"Five generic 3D action-figure style adult {sport} players standing full body, front-facing, evenly spaced in one row."
        
        # Step 3: Team Coding
        left_color = spec.get("team_left_color", "blue and white")
        right_color = spec.get("team_right_color", "red and white")
        team_section = f"Two players on the left wear plain {left_color} uniforms, two players on the right wear plain {right_color} uniforms, the center figure wears a plain light gray tracksuit."
        
        # Step 4: Text Blocks
        headline = spec.get("headline_text", "TEAM A vs TEAM B")
        subhead = spec.get("sub_text", "")
        
        # Main headline banner
        text_section = f'Add a top banner: red rectangle with white bold all-caps text exactly "{headline}".'
        
        # Add subheading if present
        if subhead:
            text_section += f' Add a subheading below the banner with white bold text exactly "{subhead}".'
        
        # Step 5: Hard Constraints
        constraints = "Uniforms must be completely blank: no team logos, no brand logos, no swoosh, no emblems, no patches. Modern bold sans-serif font, perfectly sharp, perfectly spelled, aligned and centered. Absolutely no other readable text anywhere, no watermark, no random letters, no numbers."
        
        # Combine all sections
        prompt = f"{format_section} {subject_section} {team_section} {text_section} {constraints}"
        
        return prompt
    
    @staticmethod
    def build_symbolic_prompt(spec: Dict) -> str:
        """
        Build symbolic template prompt.
        Best for: Breaking news, boycotts, controversies, rule changes
        """
        
        # Step 1: Format & Purpose
        format_section = "16:9 breaking news poster, cinematic editorial still-life."
        
        # Step 2: Subject Layout
        sport = spec.get("topic", "sports").lower()
        subject_section = f"A {sport} stadium at night under floodlights, empty pitch or court, clean composition with dramatic lighting."
        
        # Step 3: Team Coding (equipment instead of players)
        left_color = spec.get("team_left_color", "blue and white")
        right_color = spec.get("team_right_color", "red and white")
        team_section = f"In the foreground, two plain {sport} equipment items placed apart: one solid {left_color}, one solid {right_color}, both completely blank with no flags, no logos, no emblems."
        
        # Step 4: Text Blocks
        headline = spec.get("headline_text", "BREAKING NEWS")
        subhead = spec.get("sub_text", "")
        
        text_section = f'Add a top banner with bold sans-serif text exactly "{headline}".'
        if subhead:
            text_section += f' Add a smaller subheadline below exactly "{subhead}".'
        
        # Step 5: Hard Constraints
        constraints = "Perfectly sharp, perfectly spelled, high contrast, centered, no distortion. Absolutely no other readable text anywhere, no watermark, no random letters, no numbers."
        
        # Combine all sections
        prompt = f"{format_section} {subject_section} {team_section} {text_section} {constraints}"
        
        return prompt
    
    @staticmethod
    def build_action_moment_prompt(spec: Dict) -> str:
        """
        Build action_moment template prompt.
        Best for: Single-player stories, injury updates, record-breaking performances
        """
        
        # Step 1: Format & Purpose
        format_section = "16:9 sports news thumbnail, cinematic action photography."
        
        # Step 2: Subject Layout
        sport = spec.get("topic", "sports").lower()
        subject_section = f"A generic adult {sport} athlete in a plain uniform performing dynamic action, frozen action moment, dramatic stadium lighting, shallow depth of field, realistic proportions."
        
        # Step 3: Team Coding (single team color)
        team_color = spec.get("team_left_color", "blue and white")
        team_section = f"Uniform must be plain {team_color}, completely blank: no logos, no brand marks, no swoosh. Face is generic and non-identifiable."
        
        # Step 4: Text Blocks
        headline = spec.get("headline_text", "BREAKING MOMENT")
        
        text_section = f'Add bold headline text at the top in modern sans-serif, perfectly spelled: "{headline}". Large empty space on the right side for additional text overlay.'
        
        # Step 5: Hard Constraints
        constraints = "Absolutely no other readable text, no watermark, no extra letters, correct anatomy, sharp focus."
        
        # Combine all sections
        prompt = f"{format_section} {subject_section} {team_section} {text_section} {constraints}"
        
        return prompt
    
    @staticmethod
    def build_prompt(spec: Dict) -> str:
        """
        Main entry point: Convert ThumbnailSpec to Z-Image Turbo prompt.
        
        Args:
            spec: ThumbnailSpec JSON dict from Claude
        
        Returns:
            str: Production-ready Z-Image Turbo prompt
        """
        
        layout = spec.get("layout", "lineup_5_figures")
        
        if layout == "lineup_5_figures":
            prompt = PromptBuilder.build_lineup_5_prompt(spec)
        elif layout == "symbolic":
            prompt = PromptBuilder.build_symbolic_prompt(spec)
        elif layout == "action_moment":
            prompt = PromptBuilder.build_action_moment_prompt(spec)
        else:
            logger.warning(f"Unknown layout: {layout}, defaulting to lineup_5_figures")
            prompt = PromptBuilder.build_lineup_5_prompt(spec)
        
        logger.info(f"Built prompt for {layout} layout ({len(prompt)} chars)")
        return prompt
    
    @staticmethod
    def validate_spec(spec: Dict) -> bool:
        """Validate ThumbnailSpec has required fields"""
        required = [
            "topic", "headline_text", "layout", "aspect_ratio",
            "team_left_color", "team_right_color", "no_real_people", "no_team_logos"
        ]
        
        for field in required:
            if field not in spec:
                logger.error(f"Missing required field in ThumbnailSpec: {field}")
                return False
        
        # Validate headline length
        if len(spec.get("headline_text", "")) > 40:
            logger.warning(f"Headline too long ({len(spec['headline_text'])} chars), should be max 40")
        
        # Validate layout
        valid_layouts = ["lineup_5_figures", "symbolic", "action_moment"]
        if spec.get("layout") not in valid_layouts:
            logger.error(f"Invalid layout: {spec.get('layout')}, must be one of {valid_layouts}")
            return False
        
        return True


# Example usage
if __name__ == "__main__":
    # Example 1: Basketball matchup
    spec1 = {
        "topic": "NCAAB matchup",
        "headline_text": "INDIANA STATE vs BRADLEY",
        "sub_text": "BETTING INSIGHTS",
        "layout": "lineup_5_figures",
        "aspect_ratio": "16:9",
        "team_left_color": "royal blue and white",
        "team_right_color": "deep red and white",
        "no_real_people": True,
        "no_team_logos": True,
        "style": "3D action-figure poster",
        "background": "dark gradient studio",
        "negative_space": "top for headline"
    }
    
    print("=" * 80)
    print("EXAMPLE 1: Basketball Matchup (lineup_5_figures)")
    print("=" * 80)
    print("\nThumbnailSpec:")
    print(json.dumps(spec1, indent=2))
    print("\nGenerated Prompt:")
    prompt1 = PromptBuilder.build_prompt(spec1)
    print(prompt1)
    print(f"\nPrompt length: {len(prompt1)} chars")
    
    # Example 2: Cricket breaking news
    spec2 = {
        "topic": "Cricket breaking news",
        "headline_text": "MATCH IN DOUBT",
        "sub_text": "INDIA vs PAKISTAN",
        "layout": "symbolic",
        "aspect_ratio": "16:9",
        "team_left_color": "blue and white",
        "team_right_color": "green and white",
        "no_real_people": True,
        "no_team_logos": True,
        "style": "cinematic editorial still-life",
        "background": "cricket stadium night floodlights",
        "negative_space": "center for equipment"
    }
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Cricket Breaking News (symbolic)")
    print("=" * 80)
    print("\nThumbnailSpec:")
    print(json.dumps(spec2, indent=2))
    print("\nGenerated Prompt:")
    prompt2 = PromptBuilder.build_prompt(spec2)
    print(prompt2)
    print(f"\nPrompt length: {len(prompt2)} chars")
    
    # Example 3: Football performance
    spec3 = {
        "topic": "Football performance",
        "headline_text": "MBAPPE HAT-TRICK",
        "sub_text": "",
        "layout": "action_moment",
        "aspect_ratio": "16:9",
        "team_left_color": "navy blue and red",
        "team_right_color": "",
        "no_real_people": True,
        "no_team_logos": True,
        "style": "action photography",
        "background": "stadium dramatic lighting",
        "negative_space": "right for overlay"
    }
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Football Performance (action_moment)")
    print("=" * 80)
    print("\nThumbnailSpec:")
    print(json.dumps(spec3, indent=2))
    print("\nGenerated Prompt:")
    prompt3 = PromptBuilder.build_prompt(spec3)
    print(prompt3)
    print(f"\nPrompt length: {len(prompt3)} chars")
