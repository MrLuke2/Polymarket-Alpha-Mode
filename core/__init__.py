"""Core package - models, state management, API clients, and LLM integration."""
from .models import (
    TradeDirection, TradeOutcome, AgentVote, AgentType, MarketStatus, LogLevel,
    Market, WatchedMarket, TradeSignal, Trade, AgentAnalysis, CouncilDecision,
    WhaleActivity, CopyTradeSignal, Position, Portfolio, LogEntry, SystemState
)
from .state import state_manager, StateManager
from .llm import llm_manager, LLMManager
from .polymarket_client import polymarket_client, trade_executor, PolymarketClient, TradeExecutor

__all__ = [
    # Enums
    "TradeDirection", "TradeOutcome", "AgentVote", "AgentType", "MarketStatus", "LogLevel",
    # Models
    "Market", "WatchedMarket", "TradeSignal", "Trade", "AgentAnalysis", "CouncilDecision",
    "WhaleActivity", "CopyTradeSignal", "Position", "Portfolio", "LogEntry", "SystemState",
    # State
    "state_manager", "StateManager",
    # LLM
    "llm_manager", "LLMManager",
    # Polymarket Client
    "polymarket_client", "trade_executor", "PolymarketClient", "TradeExecutor"
]
