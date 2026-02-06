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
        Uses EXACT template from Image_Guide.md
        """
        
        # EXACT template from Image_Guide.md
        template = """16:9 sports news thumbnail poster, dark gray gradient background, studio lighting, clean floor shadow. Five generic 3D action-figure style adult {SPORT} players standing full body, front-facing, evenly spaced in one row. Two players on the left wear plain {LEFT_COLORS} uniforms, two players on the right wear plain {RIGHT_COLORS} uniforms, the center figure wears a plain light gray tracksuit. Uniforms must be completely blank: no team logos, no brand logos, no swoosh, no emblems, no patches. Add a top banner: red rectangle with white bold all-caps text exactly "{HEADLINE}". Add two label boxes below the banner: left white rectangle with black bold text exactly "{LEFT_LABEL}", right white rectangle with black bold text exactly "{RIGHT_LABEL}". Modern bold sans-serif font, perfectly sharp, perfectly spelled, aligned and centered. Absolutely no other readable text anywhere, no watermark, no random letters, no numbers."""
        
        # Extract values from spec
        sport = spec.get("topic", "cricket").lower().split()[0]  # Get first word (e.g., "cricket" from "cricket matchup")
        left_color = spec.get("team_left_color", "blue and white")
        right_color = spec.get("team_right_color", "red and white")
        headline = spec.get("headline_text", "TEAM A vs TEAM B").upper()
        left_label = f"{headline.split('vs')[0].strip()} (HOME)" if "vs" in headline else "TEAM A (HOME)"
        right_label = f"{headline.split('vs')[1].strip()} (AWAY)" if "vs" in headline else "TEAM B (AWAY)"
        
        # Fill template
        prompt = template.format(
            SPORT=sport,
            LEFT_COLORS=left_color,
            RIGHT_COLORS=right_color,
            HEADLINE=headline,
            LEFT_LABEL=left_label,
            RIGHT_LABEL=right_label
        )
        
        return prompt
    
    @staticmethod
    def build_symbolic_prompt(spec: Dict) -> str:
        """
        Build symbolic template prompt.
        Uses EXACT template from Image_Guide.md
        """
        
        # EXACT template from Image_Guide.md
        template = """16:9 breaking news poster, cinematic editorial still-life. A {SPORT} stadium at night under floodlights, empty pitch or court, clean composition with dramatic lighting. In the foreground, two plain {SPORT} equipment items placed apart: one solid {LEFT_COLORS}, one solid {RIGHT_COLORS}, both completely blank with no flags, no logos, no emblems. Equipment should be: for cricket use helmets, for basketball use jerseys on hangers, for football use boots. Add a top banner with bold sans-serif text exactly "{HEADLINE}". Add a smaller subheadline below exactly "{SUBHEAD}". Perfectly sharp, perfectly spelled, high contrast, centered, no distortion. Absolutely no other readable text anywhere, no watermark, no random letters, no numbers."""
        
        # Extract values from spec
        sport = spec.get("topic", "cricket").lower().split()[0]
        left_color = spec.get("team_left_color", "blue and white")
        right_color = spec.get("team_right_color", "red and white")
        headline = spec.get("headline_text", "BREAKING NEWS").upper()
        subhead = spec.get("sub_text", "").upper()
        
        # Fill template
        prompt = template.format(
            SPORT=sport,
            LEFT_COLORS=left_color,
            RIGHT_COLORS=right_color,
            HEADLINE=headline,
            SUBHEAD=subhead
        )
        
        return prompt
    
    @staticmethod
    def build_action_moment_prompt(spec: Dict) -> str:
        """
        Build action_moment template prompt.
        Uses EXACT template from Image_Guide.md
        """
        
        # EXACT template from Image_Guide.md
        template = """16:9 sports news thumbnail, cinematic action photography. A generic adult {SPORT} athlete in a plain {TEAM_COLOR} uniform performing {ACTION}, dynamic motion, frozen action, dramatic {VENUE} lighting, shallow depth of field, realistic proportions. Uniform must be completely blank: no logos, no brand marks, no swoosh. Face is generic and non-identifiable. Add bold headline text at the top in modern sans-serif, perfectly spelled: "{HEADLINE}". Large empty space on the right side for additional text overlay. Absolutely no other readable text, no watermark, no extra letters, correct anatomy, sharp focus."""
        
        # Extract values from spec
        sport = spec.get("topic", "cricket").lower().split()[0]
        team_color = spec.get("team_left_color", "blue and white")
        headline = spec.get("headline_text", "BREAKING MOMENT").upper()
        action = "in action"  # Default action
        venue = "stadium"  # Default venue
        
        # Fill template
        prompt = template.format(
            SPORT=sport,
            TEAM_COLOR=team_color,
            ACTION=action,
            VENUE=venue,
            HEADLINE=headline
        )
        
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
        
        # Validate and fix spec first
        PromptBuilder.validate_spec(spec)
        
        layout = spec.get("layout", "lineup_5_figures")
        
        if layout == "lineup_5_figures" or layout == "lineup_5":
            prompt = PromptBuilder.build_lineup_5_prompt(spec)
        elif layout == "symbolic":
            prompt = PromptBuilder.build_symbolic_prompt(spec)
        elif layout == "action_moment":
            prompt = PromptBuilder.build_action_moment_prompt(spec)
        else:
            logger.warning(f"Unknown layout: {layout}, defaulting to lineup_5_figures")
            prompt = PromptBuilder.build_lineup_5_prompt(spec)
        
        logger.info(f"✅ Built prompt for {layout} layout ({len(prompt)} chars)")
        return prompt
    
    @staticmethod
    def validate_spec(spec: Dict) -> bool:
        """Validate ThumbnailSpec has required fields"""
        # Handle both old and new layout names
        layout = spec.get("layout", "")
        if layout == "lineup_5":
            spec["layout"] = "lineup_5_figures"
        
        required = [
            "topic", "headline_text", "layout", "aspect_ratio",
            "team_left_color", "team_right_color"
        ]
        
        for field in required:
            if field not in spec or not spec[field]:
                logger.warning(f"Missing or empty field in ThumbnailSpec: {field}")
                # Don't fail validation, use defaults
                if field == "team_left_color":
                    spec["team_left_color"] = "blue and white"
                elif field == "team_right_color":
                    spec["team_right_color"] = "red and white"
                elif field == "layout":
                    spec["layout"] = "lineup_5_figures"
        
        # Validate headline length
        headline = spec.get("headline_text", "")
        if len(headline) > 40:
            logger.warning(f"Headline too long ({len(headline)} chars), truncating to 40")
            spec["headline_text"] = headline[:40]
        
        # Validate layout
        valid_layouts = ["lineup_5_figures", "symbolic", "action_moment"]
        if spec.get("layout") not in valid_layouts:
            logger.warning(f"Invalid layout: {spec.get('layout')}, defaulting to lineup_5_figures")
            spec["layout"] = "lineup_5_figures"
        
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
