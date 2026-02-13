"""
POLYMARKET ALPHA MODE - State Manager
===================================
Centralized state management for the trading platform.
Thread-safe operations for multi-component access.
"""

import threading
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import deque
from loguru import logger

from .models import (
    LogEntry, LogLevel, Trade, TradeSignal, WatchedMarket,
    Portfolio, Position, SystemState, CouncilDecision, WhaleActivity
)


class StateManager:
    """
    Thread-safe centralized state manager.
    All components read/write state through this interface.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global state access."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._state_lock = threading.RLock()
        
        # === AI Monologue Log ===
        self._log_entries: deque = deque(maxlen=100)
        
        # === Trading State ===
        self._trade_history: List[Trade] = []
        self._pending_signals: List[TradeSignal] = []
        self._council_decisions: List[CouncilDecision] = []
        
        # === Watched Markets (Sniper Scope) ===
        self._watched_markets: Dict[str, WatchedMarket] = {}
        
        # === Whale Activity ===
        self._whale_activities: deque = deque(maxlen=50)
        
        # === Portfolio ===
        self._portfolio = Portfolio(
            total_value=10000.0,  # Demo starting value
            cash_balance=10000.0,
            positions=[],
            daily_pnl=0.0,
            total_pnl=0.0
        )
        
        # === Historical Data for Charts ===
        self._portfolio_history: List[Dict[str, Any]] = []
        self._btc_history: List[Dict[str, Any]] = []
        
        # === System State ===
        self._system_state = SystemState()
        self._start_time = datetime.utcnow()
        
        logger.info("StateManager initialized")
    
    # ============================================
    # LOGGING / AI MONOLOGUE
    # ============================================
    
    def add_log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> LogEntry:
        """Add entry to the AI monologue log."""
        entry = LogEntry(
            level=level,
            message=message,
            source=source,
            metadata=metadata or {}
        )
        with self._state_lock:
            self._log_entries.appendleft(entry)
        return entry
    
    def get_logs(self, limit: int = 50) -> List[LogEntry]:
        """Get recent log entries."""
        with self._state_lock:
            return list(self._log_entries)[:limit]
    
    # ============================================
    # TRADING STATE
    # ============================================
    
    def add_trade(self, trade: Trade) -> None:
        """Record an executed trade."""
        with self._state_lock:
            self._trade_history.append(trade)
            self._system_state.last_trade_time = trade.timestamp
            self.add_log(
                f"EXECUTED: {trade.direction.value.upper()} {trade.outcome.value.upper()} "
                f"on '{trade.market_question[:40]}...' @ ${trade.size:.2f}",
                level=LogLevel.TRADE,
                source="executor",
                metadata={"trade_id": trade.id}
            )
    
    def get_trade_history(self, limit: int = 50) -> List[Trade]:
        """Get recent trade history."""
        with self._state_lock:
            return self._trade_history[-limit:]
    
    def add_signal(self, signal: TradeSignal) -> None:
        """Add a pending trade signal."""
        with self._state_lock:
            self._pending_signals.append(signal)
            self._system_state.pending_signals = len(self._pending_signals)
    
    def get_pending_signals(self) -> List[TradeSignal]:
        """Get all pending signals."""
        with self._state_lock:
            return list(self._pending_signals)
    
    def clear_signal(self, signal_id: str) -> None:
        """Remove a processed signal."""
        with self._state_lock:
            self._pending_signals = [s for s in self._pending_signals if s.id != signal_id]
            self._system_state.pending_signals = len(self._pending_signals)
    
    def add_council_decision(self, decision: CouncilDecision) -> None:
        """Record a council decision."""
        with self._state_lock:
            self._council_decisions.append(decision)
            self.add_log(
                f"COUNCIL: {decision.final_decision.value.upper()} on '{decision.market_question[:40]}...' "
                f"({decision.votes_for}/{len(decision.analyses)} votes)",
                level=LogLevel.INFO,
                source="council",
                metadata={"decision_id": decision.id}
            )
    
    # ============================================
    # SNIPER SCOPE (WATCHED MARKETS)
    # ============================================
    
    def watch_market(self, watched: WatchedMarket) -> None:
        """Add a market to the Sniper Scope."""
        with self._state_lock:
            self._watched_markets[watched.market.id] = watched
            self._system_state.markets_watched = len(self._watched_markets)
            self.add_log(
                f"SCOPE: Watching '{watched.market.question[:50]}...'",
                level=LogLevel.INFO,
                source="sniper"
            )
    
    def unwatch_market(self, market_id: str) -> None:
        """Remove a market from the Sniper Scope."""
        with self._state_lock:
            if market_id in self._watched_markets:
                del self._watched_markets[market_id]
                self._system_state.markets_watched = len(self._watched_markets)
    
    def get_watched_markets(self) -> List[WatchedMarket]:
        """Get all watched markets."""
        with self._state_lock:
            return list(self._watched_markets.values())
    
    # ============================================
    # WHALE WATCHER
    # ============================================
    
    def add_whale_activity(self, activity: WhaleActivity) -> None:
        """Record detected whale activity."""
        with self._state_lock:
            self._whale_activities.appendleft(activity)
            self.add_log(
                f"WHALE DETECTED: {activity.wallet_address[:10]}... "
                f"{activity.direction.value.upper()} ${activity.size:,.0f} "
                f"on '{activity.market_question[:30]}...'",
                level=LogLevel.WARNING,
                source="whale_watcher",
                metadata={"tx_hash": activity.tx_hash}
            )
    
    def get_whale_activities(self, limit: int = 20) -> List[WhaleActivity]:
        """Get recent whale activities."""
        with self._state_lock:
            return list(self._whale_activities)[:limit]
    
    # ============================================
    # PORTFOLIO
    # ============================================
    
    def update_portfolio(self, portfolio: Portfolio) -> None:
        """Update portfolio state."""
        with self._state_lock:
            self._portfolio = portfolio
            self._system_state.active_positions = len(portfolio.positions)
            # Record for historical chart
            self._portfolio_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "value": portfolio.total_value
            })
            # Keep last 1000 data points
            if len(self._portfolio_history) > 1000:
                self._portfolio_history = self._portfolio_history[-1000:]
    
    def get_portfolio(self) -> Portfolio:
        """Get current portfolio state."""
        with self._state_lock:
            return self._portfolio
    
    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """Get portfolio value history for charting."""
        with self._state_lock:
            return list(self._portfolio_history)
    
    def add_btc_price(self, price: float) -> None:
        """Record BTC price for comparison chart."""
        with self._state_lock:
            self._btc_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "price": price
            })
            if len(self._btc_history) > 1000:
                self._btc_history = self._btc_history[-1000:]
    
    def get_btc_history(self) -> List[Dict[str, Any]]:
        """Get BTC price history."""
        with self._state_lock:
            return list(self._btc_history)
    
    # ============================================
    # SYSTEM STATE
    # ============================================
    
    def get_system_state(self) -> SystemState:
        """Get current system state."""
        with self._state_lock:
            self._system_state.uptime_seconds = int(
                (datetime.utcnow() - self._start_time).total_seconds()
            )
            return self._system_state
    
    def set_running(self, is_running: bool) -> None:
        """Set system running state."""
        with self._state_lock:
            self._system_state.is_running = is_running
    
    def set_agents_active(self, count: int) -> None:
        """Set number of active agents."""
        with self._state_lock:
            self._system_state.agents_active = count
    
    def increment_errors(self) -> None:
        """Increment 24h error count."""
        with self._state_lock:
            self._system_state.errors_24h += 1


# Global instance
state_manager = StateManager()
