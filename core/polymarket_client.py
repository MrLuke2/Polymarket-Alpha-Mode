"""
POLYMARKET GOD MODE - Polymarket API Client
============================================
Handles all interactions with Polymarket's CLOB API.
"""

import asyncio
import hmac
import hashlib
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from loguru import logger

from core.models import Market, Trade, TradeDirection, TradeOutcome, LogLevel
from core.state import state_manager
from config.settings import settings


class PolymarketClient:
    """
    Async client for Polymarket CLOB API.
    Handles authentication, market data, and order execution.
    """
    
    def __init__(self):
        self.base_url = settings.polymarket_host
        self.api_key = settings.polymarket_api_key
        self.api_secret = settings.polymarket_api_secret
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate HMAC signature for authenticated requests."""
        if not self.api_secret:
            raise ValueError("API secret not configured")
        
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_auth_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Generate authentication headers."""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, path, body)
        
        return {
            "POLY_API_KEY": self.api_key or "",
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
    
    # ============================================
    # MARKET DATA
    # ============================================
    
    async def get_markets(
        self,
        limit: int = 100,
        active_only: bool = True,
        tag: Optional[str] = None
    ) -> List[Market]:
        """Fetch markets from Polymarket."""
        await self._ensure_session()
        
        params = {"limit": limit, "active": str(active_only).lower()}
        if tag:
            params["tag"] = tag
        
        try:
            async with self._session.get(
                f"{self.base_url}/markets",
                params=params
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch markets: {response.status}")
                    return []
                
                data = await response.json()
                markets = []
                
                for m in data.get("markets", data if isinstance(data, list) else []):
                    try:
                        market = Market(
                            id=m.get("condition_id", m.get("id", "")),
                            question=m.get("question", ""),
                            description=m.get("description"),
                            yes_price=float(m.get("yes_price", m.get("outcomePrices", [0.5, 0.5])[0])),
                            no_price=float(m.get("no_price", m.get("outcomePrices", [0.5, 0.5])[1])),
                            volume_24h=float(m.get("volume_24h", m.get("volume", 0))),
                            liquidity=float(m.get("liquidity", 0)),
                            tags=m.get("tags", [])
                        )
                        markets.append(market)
                    except Exception as e:
                        logger.warning(f"Failed to parse market: {e}")
                        continue
                
                return markets
                
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            state_manager.increment_errors()
            return []
    
    async def get_market(self, market_id: str) -> Optional[Market]:
        """Fetch a single market by ID."""
        await self._ensure_session()
        
        try:
            async with self._session.get(
                f"{self.base_url}/markets/{market_id}"
            ) as response:
                if response.status != 200:
                    return None
                
                m = await response.json()
                return Market(
                    id=m.get("condition_id", market_id),
                    question=m.get("question", ""),
                    description=m.get("description"),
                    yes_price=float(m.get("yes_price", 0.5)),
                    no_price=float(m.get("no_price", 0.5)),
                    volume_24h=float(m.get("volume_24h", 0)),
                    liquidity=float(m.get("liquidity", 0)),
                    tags=m.get("tags", [])
                )
                
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    async def get_orderbook(self, market_id: str) -> Dict[str, Any]:
        """Fetch orderbook for a market."""
        await self._ensure_session()
        
        try:
            async with self._session.get(
                f"{self.base_url}/book",
                params={"token_id": market_id}
            ) as response:
                if response.status != 200:
                    return {"bids": [], "asks": []}
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            return {"bids": [], "asks": []}
    
    # ============================================
    # TRADING
    # ============================================
    
    async def place_order(
        self,
        market_id: str,
        side: TradeDirection,
        outcome: TradeOutcome,
        size: float,
        price: float
    ) -> Optional[Dict[str, Any]]:
        """
        Place a limit order on Polymarket.
        
        Args:
            market_id: The market condition ID
            side: BUY or SELL
            outcome: YES or NO
            size: Amount in USDC
            price: Limit price (0-1)
        
        Returns:
            Order response or None on failure
        """
        if not self.api_key or not self.api_secret:
            logger.error("Cannot place order: API credentials not configured")
            state_manager.add_log(
                "ORDER FAILED: API credentials not configured",
                level=LogLevel.ERROR,
                source="executor"
            )
            return None
        
        await self._ensure_session()
        
        # Determine token ID based on outcome
        # In production, you'd look this up from the market data
        token_id = f"{market_id}_{outcome.value}"
        
        order_payload = {
            "tokenID": token_id,
            "side": side.value.upper(),
            "price": str(price),
            "size": str(size),
            "type": "GTC"  # Good Till Cancelled
        }
        
        path = "/order"
        body = str(order_payload)
        headers = self._get_auth_headers("POST", path, body)
        
        try:
            async with self._session.post(
                f"{self.base_url}{path}",
                json=order_payload,
                headers=headers
            ) as response:
                result = await response.json()
                
                if response.status in (200, 201):
                    state_manager.add_log(
                        f"ORDER PLACED: {side.value.upper()} {outcome.value.upper()} "
                        f"${size:.2f} @ {price:.2%}",
                        level=LogLevel.TRADE,
                        source="executor"
                    )
                    return result
                else:
                    logger.error(f"Order failed: {result}")
                    state_manager.add_log(
                        f"ORDER FAILED: {result.get('error', 'Unknown error')}",
                        level=LogLevel.ERROR,
                        source="executor"
                    )
                    return None
                    
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            state_manager.increment_errors()
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        if not self.api_key:
            return False
        
        await self._ensure_session()
        path = f"/order/{order_id}"
        headers = self._get_auth_headers("DELETE", path)
        
        try:
            async with self._session.delete(
                f"{self.base_url}{path}",
                headers=headers
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch current positions."""
        if not self.api_key:
            return []
        
        await self._ensure_session()
        path = "/positions"
        headers = self._get_auth_headers("GET", path)
        
        try:
            async with self._session.get(
                f"{self.base_url}{path}",
                headers=headers
            ) as response:
                if response.status != 200:
                    return []
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    # ============================================
    # WALLET MONITORING (for Whale Watcher)
    # ============================================
    
    async def get_wallet_trades(
        self,
        wallet_address: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch recent trades for a wallet address."""
        await self._ensure_session()
        
        try:
            # This endpoint may vary - check Polymarket API docs
            async with self._session.get(
                f"{self.base_url}/trades",
                params={"maker": wallet_address, "limit": limit}
            ) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return data.get("trades", data if isinstance(data, list) else [])
                
        except Exception as e:
            logger.error(f"Error fetching wallet trades: {e}")
            return []


# ============================================
# TRADE EXECUTOR
# ============================================

class TradeExecutor:
    """
    Executes trades based on council decisions.
    Handles order management, position tracking, and risk checks.
    """
    
    def __init__(self, client: PolymarketClient):
        self.client = client
        self._pending_orders: Dict[str, Dict] = {}
    
    async def execute_decision(
        self,
        market: Market,
        direction: TradeDirection,
        outcome: TradeOutcome,
        size: float
    ) -> Optional[Trade]:
        """
        Execute a trade based on council decision.
        
        Performs final risk checks before execution.
        """
        # Final risk check
        portfolio = state_manager.get_portfolio()
        
        if size > portfolio.cash_balance:
            state_manager.add_log(
                f"BLOCKED: Insufficient balance. Need ${size:.0f}, have ${portfolio.cash_balance:.0f}",
                level=LogLevel.WARNING,
                source="executor"
            )
            return None
        
        if size > settings.max_single_trade:
            size = settings.max_single_trade
            state_manager.add_log(
                f"SIZE CAPPED: Reduced to max ${settings.max_single_trade:.0f}",
                level=LogLevel.WARNING,
                source="executor"
            )
        
        # Determine price based on outcome
        price = market.yes_price if outcome == TradeOutcome.YES else market.no_price
        
        # Execute order
        result = await self.client.place_order(
            market_id=market.id,
            side=direction,
            outcome=outcome,
            size=size,
            price=price
        )
        
        if result:
            trade = Trade(
                market_id=market.id,
                market_question=market.question,
                direction=direction,
                outcome=outcome,
                size=size,
                price=price,
                tx_hash=result.get("orderID", result.get("id")),
                status="confirmed"
            )
            state_manager.add_trade(trade)
            return trade
        
        return None


# ============================================
# MODULE EXPORTS
# ============================================

# Singleton client instance
polymarket_client = PolymarketClient()
trade_executor = TradeExecutor(polymarket_client)
