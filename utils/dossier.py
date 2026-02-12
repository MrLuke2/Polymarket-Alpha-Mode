
import re
from typing import Dict, Optional

def parse_whale_dossier(markdown_content: str) -> Dict[str, str]:
    """
    Parses the whale dossier markdown content to extract detailed biographies 
    for known whales based on header sections.
    
    Returns a dictionary mapping whale aliases (or key terms) to their bio text.
    """
    profiles = {}
    
    # Regex to find level 3 headers and their content until the next header
    # Matches: ### [Header Text] \n [Content]
    pattern = r"### (.*?)\n(.*?)(?=\n### |\n## |\Z)"
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    
    for header, content in matches:
        # Clean up header to get the key name
        # e.g. "Théo — \"The French Whale\" (~$85M profit)" -> "Théo"
        # e.g. "Domer / ImJustKen — The volume king" -> "Domer"
        
        # We'll use a simplified key for matching, but keep the full header in the content if needed
        key_name = header.split("—")[0].strip().split(" ")[0].lower()
        
        # specific manual mapping for complex headers
        if "domer" in header.lower():
            key_name = "domer"
        elif "théo" in header.lower():
            key_name = "theo"
        elif "kch123" in header.lower():
            key_name = "kch123"
        elif "gcottrell" in header.lower() or "george cottrell" in header.lower():
            key_name = "gcottrell"
            
        profiles[key_name] = content.strip()
        
    return profiles

def get_whale_bio(profiles: Dict[str, str], alias: str) -> Optional[str]:
    """
    Retrieves the bio for a given whale alias from the parsed profiles.
    """
    alias_lower = alias.lower()
    
    # Direct match
    if alias_lower in profiles:
        return profiles[alias_lower]
        
    # Partial match
    for key, bio in profiles.items():
        if key in alias_lower:
            return bio
            
    return None
