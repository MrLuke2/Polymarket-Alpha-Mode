
"""
POLYMARKET GOD MODE - The Press Secretary (Viral Engine)
========================================================
Generates marketing content, PnL cards, and tweet drafts.
Human-in-the-loop: Generates the content, user confirms.
"""

import os
import matplotlib.pyplot as plt
from PIL import Image
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from core.models import LogLevel
from core.state import state_manager
from config.settings import settings

# Assets Directory
ASSETS_DIR = os.path.join("dashboard", "assets")
PNL_CARD_PATH = os.path.join(ASSETS_DIR, "latest_win.png")
TWEET_DRAFT_PATH = os.path.join(ASSETS_DIR, "tweet_draft.txt")

class PressSecretary:
    def __init__(self):
        self._check_assets_dir()

    def _check_assets_dir(self):
        os.makedirs(ASSETS_DIR, exist_ok=True)

    def generate_pnl_card(self, profit: float, roi_pct: float, market_question: str):
        """Generates a high-quality PnL image for social sharing."""
        try:
            # Set cyberpunk style
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Colors
            bg_color = "#0a0a0f"
            accent_cyan = "#00f5ff"
            accent_green = "#00ff88"
            text_color = "#e0e0e0"
            
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            
            # Hide axes
            ax.axis('off')
            
            # Add text
            plt.text(0.5, 0.85, "POLYMARKET GOD MODE", color=accent_cyan, fontsize=24, 
                     fontweight='bold', ha='center', fontfamily='monospace')
            plt.text(0.5, 0.75, "ALPHA CAPTURED", color=text_color, fontsize=16, 
                     ha='center', fontfamily='monospace')
            
            # Profit
            color = accent_green if profit >= 0 else "#ff3366"
            sign = "+" if profit >= 0 else ""
            plt.text(0.5, 0.55, f"{sign}${profit:.2f}", color=color, fontsize=48, 
                     fontweight='bold', ha='center', fontfamily='monospace')
            plt.text(0.5, 0.45, f"ROI: {sign}{roi_pct:.1f}%", color=color, fontsize=20, 
                     ha='center', fontfamily='monospace')
            
            # Market
            plt.text(0.5, 0.25, f"Market: {market_question[:40]}...", color="#888", fontsize=12, 
                     ha='center', fontfamily='monospace', style='italic')
            
            # Timestamp
            plt.text(0.5, 0.1, datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"), 
                     color="#444", fontsize=10, ha='center', fontfamily='monospace')
            
            # Border
            rect = plt.Rectangle((0.01, 0.01), 0.98, 0.98, fill=False, color=accent_cyan, linewidth=2, transform=fig.transFigure)
            fig.lines.append(rect)
            
            plt.tight_layout()
            plt.savefig(PNL_CARD_PATH, dpi=150, bbox_inches='tight', facecolor=bg_color)
            plt.close()
            
            logger.info(f"PnL card generated at {PNL_CARD_PATH}")
            state_manager.add_log("Viral Engine: New PnL card generated.", LogLevel.INFO, "press_secretary")
            return PNL_CARD_PATH
        except Exception as e:
            logger.error(f"Failed to generate PnL card: {e}")
            return None

    async def draft_tweets(self, profit: float, roi_pct: float, market_question: str) -> List[str]:
        """Drafts viral tweets using AI logic."""
        # In a real scenario, this would call the LLM Manager
        # Here we provide curated templates that look AI-generated
        
        templates = [
            f"Market logic was clear. Predicted '{market_question[:20]}...' with high confidence. +{roi_pct:.1f}% ROI in the bag. ⚡ #Polymarket #Alpha #GodMode",
            f"Another win for the God Mode Council. Captured ${profit:.2f} on the latest swing. The swarm intelligence is unmatched. 🤖💹 #PredictionMarkets #Trading",
            f"While the crowd was uncertain, the Alpha Engine saw the imbalance. ${profit:.2f} profit secured. Precision trading on @Polymarket. 🎯🔥"
        ]
        
        try:
            with open(TWEET_DRAFT_PATH, "w", encoding="utf-8") as f:
                f.write("\n---\n".join(templates))
            
            state_manager.add_log("Viral Engine: New tweet drafts prepared.", LogLevel.INFO, "press_secretary")
            return templates
        except Exception as e:
            logger.error(f"Failed to save tweet drafts: {e}")
            return templates

# Singleton
press_secretary = PressSecretary()
