
"""
Utility functions for GitHub integration and repo awareness.
"""

import subprocess
import os
from typing import Optional, Dict
from config.settings import settings

def get_repo_info() -> Dict[str, str]:
    """
    Attempts to retrieve current repository information.
    Prioritizes settings, then environment, then local git config.
    """
    info = {
        "url": settings.github_repo_url,
        "name": "Polymarket-Alpha-Mode",
        "author": "MrLuke2"
    }
    
    # Try to extract from URL
    if settings.github_repo_url:
        parts = settings.github_repo_url.rstrip("/").split("/")
        if len(parts) >= 2:
            info["name"] = parts[-1]
            info["author"] = parts[-2]
            
    # Fallback to local git if available
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        if remote_url:
            info["url"] = remote_url
            # Update name/author from real remote
            remote_parts = remote_url.rstrip(".git").rstrip("/").split("/")
            if len(remote_parts) >= 2:
                info["name"] = remote_parts[-1]
                info["author"] = remote_parts[-2]
    except:
        pass
        
    return info
