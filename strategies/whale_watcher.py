"""
POLYMARKET ALPHA MODE - Whale Watcher (Copy Trading)
==================================================
Monitor top traders and intelligently copy their positions.

Strategy:
1. Track top profitable wallets from leaderboard
2. Detect large trades (>$1,000)
3. Analyze trade reasoning with AI
4. Copy-trade 10% of whale's size if AI agrees
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from loguru import logger

from core.models import (
    WhaleActivity, CopyTradeSignal, TradeDirection, TradeOutcome,
    Market, LogLevel
)
from core.state import state_manager
from config.settings import settings


# ============================================
# WHALE PROFILES
# ============================================

@dataclass
class WhaleProfile:
    """Profile for a tracked whale wallet."""
    address: str
    alias: str
    win_rate_30d: float
    pnl_30d: float
    avg_trade_size: float
    specialty: str  # e.g., "crypto", "politics", "sports"
    trust_score: float  # 0-1, higher = more trustworthy


# Default whale profiles (replace with real addresses)
# Real whale profiles from research dossier
DEFAULT_WHALES = [
    WhaleProfile(
        address="0x9d84ce0306f8551e02efef1680475fc0f1dc1344",
        alias="ImJustKen (Domer)",
        win_rate_30d=0.52,  # Verified ~52% but high EV
        pnl_30d=2930000,    # $2.93M All-time
        avg_trade_size=15000,
        specialty="General/Poker",
        trust_score=0.95
    ),
    WhaleProfile(
        address="0xc6587b11a2209e46dfe3928b31c5514a8e33b784",
        alias="Erasmus",
        win_rate_30d=0.71,
        pnl_30d=1300000,
        avg_trade_size=25000,
        specialty="Politics/Polling",
        trust_score=0.90
    ),
    WhaleProfile(
        address="0x492442EaB586F242B53bDa933fD5dE859c8A3782",
        alias="Anon Sports Whale",
        win_rate_30d=0.65,
        pnl_30d=3150000,
        avg_trade_size=50000,
        specialty="Sports",
        trust_score=0.88
    ),
    WhaleProfile(
        # kch123 (real addr unknown in dossier explicitly but linked to sports)
        address="0x1234567890abcdef1234567890abcdef12345678", 
        alias="kch123",
        win_rate_30d=0.68,
        pnl_30d=10800000, 
        avg_trade_size=50000,
        specialty="Sports/Super Bowl",
        trust_score=0.92
    ),
    WhaleProfile(
        address="0x006cc834Cc092684F1B56626E23BEdB3835c16ea",
        alias="Top 15 Anon",
        win_rate_30d=0.60,
        pnl_30d=5160000,
        avg_trade_size=10000,
        specialty="Unknown",
        trust_score=0.85
    ),
]


# ============================================
# WHALE WATCHER SERVICE
# ============================================

class WhaleWatcher:
    """
    Monitors whale wallets and generates copy-trade signals.
    """
    
    def __init__(self, whale_profiles: Optional[List[WhaleProfile]] = None):
        self.whales = {w.address: w for w in (whale_profiles or DEFAULT_WHALES)}
        self.min_trade_size = settings.whale_min_trade_size
        self.copy_percentage = settings.whale_copy_percentage
        self._running = False
        self._poll_interval = 30  # seconds
        self._recent_txs: set = set()  # Track processed transactions
        
        logger.info(f"WhaleWatcher initialized with {len(self.whales)} tracked wallets")
    
    async def start(self):
        """Start monitoring whale activity."""
        self._running = True
        state_manager.add_log(
            f"WHALE WATCHER ACTIVE: Tracking {len(self.whales)} wallets",
            level=LogLevel.INFO,
            source="whale_watcher"
        )
        
        while self._running:
            try:
                await self._poll_whale_activity()
            except Exception as e:
                logger.error(f"Whale polling error: {e}")
                state_manager.increment_errors()
            
            await asyncio.sleep(self._poll_interval)
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
    
    async def _poll_whale_activity(self):
        """Poll for new whale trades."""
        # In production, this would query:
        # 1. Polymarket API for recent trades by tracked addresses
        # 2. Or scan blockchain events for the CLOB contract
        
        # For demo, we'll simulate whale activity detection
        # Replace this with actual API calls in production
        
        for address, profile in self.whales.items():
            try:
                activity = await self._check_wallet_activity(address, profile)
                if activity:
                    state_manager.add_whale_activity(activity)
                    signal = await self._analyze_and_generate_signal(activity, profile)
                    if signal and signal.ai_agrees:
                        state_manager.add_log(
                            f"COPY SIGNAL: Following {profile.alias} into "
                            f"'{activity.market_question[:30]}...' - ${signal.recommended_size:.0f}",
                            level=LogLevel.SUCCESS,
                            source="whale_watcher"
                        )
            except Exception as e:
                logger.error(f"Error checking wallet {address[:10]}: {e}")
    
    async def _check_wallet_activity(
        self, 
        address: str, 
        profile: WhaleProfile
    ) -> Optional[WhaleActivity]:
        """
        Check for new activity from a whale wallet using Polymarket API.
        """
        try:
            from core.polymarket_client import polymarket_client
            trades = await polymarket_client.get_wallet_trades(address, limit=5)
            
            if not trades:
                return None
                
            # Get latest trade
            latest = trades[0]
            trade_id = latest.get("id") or latest.get("transactionHash")
            
            # Check if already processed
            if not trade_id or trade_id in self._recent_txs:
                return None
            
            self._recent_txs.add(trade_id)
            # Keep history manageable
            if len(self._recent_txs) > 1000:
                self._recent_txs.clear()
            
            # Parse activity
            size = float(latest.get("size", 0))
            if size < self.min_trade_size:
                return None
                
            return WhaleActivity(
                wallet_address=address,
                market_id=latest.get("conditionId", "unknown"),
                market_question=latest.get("question", "Unknown Market"),
                direction=TradeDirection.BUY if latest.get("side", "").upper() == "BUY" else TradeDirection.SELL,
                outcome=TradeOutcome.YES if latest.get("outcome", "").upper() == "YES" else TradeOutcome.NO,
                size=size,
                price=float(latest.get("price", 0.5)),
                tx_hash=latest.get("transactionHash", latest.get("id", "unknown")),
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Failed to check whale {address}: {e}")
            return None
    
    async def _analyze_and_generate_signal(
        self,
        activity: WhaleActivity,
        profile: WhaleProfile
    ) -> Optional[CopyTradeSignal]:
        """
        Analyze whale trade and decide whether to copy.
        Uses AI to understand the reasoning behind the trade.
        """
        # Skip if below minimum size
        if activity.size < self.min_trade_size:
            state_manager.add_log(
                f"Ignoring small whale trade: ${activity.size:.0f} < ${self.min_trade_size:.0f} min",
                level=LogLevel.INFO,
                source="whale_watcher"
            )
            return None
        
        # Calculate recommended copy size
        recommended_size = min(
            activity.size * self.copy_percentage,
            settings.max_single_trade
        )
        
        # Analyze whether we should follow this trade
        analysis = await self._ai_analyze_whale_trade(activity, profile)
        
        signal = CopyTradeSignal(
            whale_activity=activity,
            recommended_size=recommended_size,
            ai_agrees=analysis["agrees"],
            ai_reasoning=analysis["reasoning"],
            confidence=analysis["confidence"]
        )
        
        return signal
    
    async def _ai_analyze_whale_trade(
        self,
        activity: WhaleActivity,
        profile: WhaleProfile
    ) -> Dict[str, Any]:
        """
        AI analysis of whale trade to determine if we should copy.
        
        Considers:
        - Whale's historical accuracy in this category
        - Current market conditions
        - Position sizing relative to their usual trades
        - Timing (are they early or late to a trend?)
        """
        # Rule-based analysis (replace with LLM in production)
        
        # Factor 1: Whale's track record
        track_record_score = profile.win_rate_30d * profile.trust_score
        
        # Factor 2: Trade size relative to their average
        size_ratio = activity.size / profile.avg_trade_size
        conviction_score = min(1.0, size_ratio)  # Higher size = higher conviction
        
        # Factor 3: Is this whale specialized in this market type?
        # (Would need market categorization in production)
        specialty_match = 0.7  # Default moderate match
        
        # Composite score
        composite_score = (
            track_record_score * 0.4 +
            conviction_score * 0.3 +
            specialty_match * 0.3
        )
        
        # Decision threshold
        agrees = composite_score > 0.55
        
        reasoning = (
            f"{profile.alias} ({profile.win_rate_30d:.0%} win rate) placed "
            f"{'large' if size_ratio > 1.2 else 'standard'} bet. "
            f"Trust score: {profile.trust_score:.0%}. "
            f"Composite analysis: {composite_score:.0%}. "
            f"{'FOLLOWING' if agrees else 'PASSING'} - "
            f"{'Strong conviction signal' if agrees else 'Insufficient confidence'}"
        )
        
        return {
            "agrees": agrees,
            "confidence": composite_score,
            "reasoning": reasoning
        }
    
    def get_whale_leaderboard(self) -> List[Dict[str, Any]]:
        """Get whale profiles formatted for dashboard display."""
        return [
            {
                "address": w.address[:10] + "...",
                "alias": w.alias,
                "win_rate": f"{w.win_rate_30d:.0%}",
                "pnl_30d": f"${w.pnl_30d:,.0f}",
                "specialty": w.specialty,
                "trust_score": f"{w.trust_score:.0%}"
            }
            for w in sorted(
                self.whales.values(),
                key=lambda x: x.pnl_30d,
                reverse=True
            )
        ]
    
    def add_whale(self, profile: WhaleProfile) -> None:
        """Add a new whale to track."""
        self.whales[profile.address] = profile
        state_manager.add_log(
            f"Added whale: {profile.alias} ({profile.address[:10]}...)",
            level=LogLevel.INFO,
            source="whale_watcher"
        )
    
    def remove_whale(self, address: str) -> None:
        """Remove a whale from tracking."""
        if address in self.whales:
            alias = self.whales[address].alias
            del self.whales[address]
            state_manager.add_log(
                f"Removed whale: {alias}",
                level=LogLevel.INFO,
                source="whale_watcher"
            )


# ============================================
# LEADERBOARD FETCHER
# ============================================

class LeaderboardFetcher:
    """
    Fetches top traders from Polymarket leaderboard.
    Updates whale profiles with real performance data.
    """
    
    LEADERBOARD_URL = "https://polymarket.com/api/leaderboard"  # Placeholder
    
    async def fetch_top_traders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch top traders from Polymarket leaderboard.
        
        Note: Actual endpoint may differ - check Polymarket API docs.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.LEADERBOARD_URL,
                    params={"limit": limit, "timeframe": "30d"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("traders", [])
                    else:
                        logger.warning(f"Leaderboard fetch failed: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Leaderboard fetch error: {e}")
            return []
    
    async def update_whale_profiles(
        self, 
        watcher: WhaleWatcher
    ) -> List[WhaleProfile]:
        """
        Update whale profiles with latest leaderboard data.
        Returns newly discovered whales.
        """
        traders = await self.fetch_top_traders()
        new_whales = []
        
        for trader in traders:
            address = trader.get("address")
            if not address:
                continue
            
            if address in watcher.whales:
                # Update existing whale
                profile = watcher.whales[address]
                profile.win_rate_30d = trader.get("win_rate", profile.win_rate_30d)
                profile.pnl_30d = trader.get("pnl_30d", profile.pnl_30d)
            else:
                # New whale discovered
                profile = WhaleProfile(
                    address=address,
                    alias=trader.get("username", f"Whale_{address[:6]}"),
                    win_rate_30d=trader.get("win_rate", 0.5),
                    pnl_30d=trader.get("pnl_30d", 0),
                    avg_trade_size=trader.get("avg_trade_size", 1000),
                    specialty="general",
                    trust_score=0.6  # Default for new whales
                )
                new_whales.append(profile)
        
        return new_whales


# ============================================
# MODULE EXPORTS
# ============================================

# Singleton whale watcher instance
whale_watcher = WhaleWatcher()
leaderboard_fetcher = LeaderboardFetcher()
