"""
POLYMARKET GOD MODE - Configuration
===================================
Central configuration management using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Main application settings loaded from environment variables."""
    
    # === APPLICATION ===
    app_name: str = "Polymarket Alpha Mode"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # === API KEYS ===
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    polymarket_api_key: Optional[str] = Field(default=None, alias="POLYMARKET_API_KEY")
    polymarket_api_secret: Optional[str] = Field(default=None, alias="POLYMARKET_API_SECRET")
    
    # === POLYMARKET ===
    polymarket_host: str = "https://clob.polymarket.com"
    polymarket_ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    chain_id: int = 137  # Polygon Mainnet
    
    # === WALLET ===
    wallet_private_key: Optional[str] = Field(default=None, alias="WALLET_PRIVATE_KEY")
    wallet_address: Optional[str] = Field(default=None, alias="WALLET_ADDRESS")
    
    # === GITHUB ===
    github_repo_url: str = Field(default="https://github.com/MrLuke2/Polymarket-Alpha-Mode", alias="GITHUB_REPO_URL")
    
    # === WHALE WATCHER ===
    whale_addresses: List[str] = Field(default_factory=lambda: [
        "0x9d84ce0306f8551e02efef1680475fc0f1dc1344",  # ImJustKen (Domer)
        "0xc6587b11a2209e46dfe3928b31c5514a8e33b784",  # Erasmus
        "0x492442EaB586F242B53bDa933fD5dE859c8A3782",  # Anon Sports Whale
        "0xd5ccdf772f795547e299de57f47966e24de8dea4",  # Tsybka
        "0x006cc834Cc092684F1B56626E23BEdB3835c16ea",  # Top 15 Anon
    ])
    whale_min_trade_size: float = 1000.0  # Minimum trade size in USDC to trigger copy
    whale_copy_percentage: float = 0.10   # Copy 10% of whale's position
    
    # === COUNCIL OF AGENTS ===
    council_voting_threshold: float = 0.67  # 2/3 majority required
    agent_timeout_seconds: int = 30
    max_position_size: float = 500.0  # Maximum position size in USDC
    
    # === RISK MANAGEMENT ===
    max_daily_loss: float = 1000.0
    max_single_trade: float = 500.0
    volatility_threshold: float = 0.15  # 15% daily volatility threshold
    
    # === DATA FEEDS ===
    binance_ws_url: str = "wss://stream.binance.com:9443/ws"
    coingecko_api_url: str = "https://api.coingecko.com/api/v3"
    
    # === CACHING ===
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    cache_ttl_seconds: int = 300
    
    # === DASHBOARD ===
    dashboard_refresh_interval: int = 5  # seconds
    max_log_entries: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Global settings instance
settings = Settings()
