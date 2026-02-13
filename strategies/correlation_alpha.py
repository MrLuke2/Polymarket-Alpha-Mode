
"""
POLYMARKET ALPHA MODE - Cross-Exchange Correlation Alpha
======================================================
Predictive alpha engine using Binance Order Book Imbalance.

Logic:
1. Connect to Binance WebSocket for BTC/USDT depth.
2. Calculate Bid-Ask Imbalance Ratio.
3. Signal "Strong Buy" if Bids > 3x Asks & High Volatility.
4. Log signals for manual or automated execution.
"""

import asyncio
import json
import time
import os
import aiohttp
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List
from loguru import logger
from dataclasses import dataclass

from core.models import LogLevel, TradeDirection, TradeOutcome
from core.state import state_manager
from core.polymarket_client import polymarket_client
from core.polymarket_client import trade_executor
from config.settings import settings

# Configuration
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@depth5"
IMBALANCE_THRESHOLD = 3.0  # Bids must be 3x greater than asks
VOLATILITY_WINDOW = 60     # Seconds to measure volatility
COOL_DOWN_PERIOD = 60      # Seconds between signals
STRIKE_PRICE_CEILING = 0.40 # Don't buy if market price is above 40c
LOG_FILE = os.path.join("dashboard", "logs", "alpha_signals.csv")

@dataclass
class AlphaSignal:
    timestamp: str
    symbol: str
    signal_type: str  # STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
    imbalance_ratio: float
    bids_vol: float
    asks_vol: float
    price: float
    confidence: float

class CorrelationAlpha:
    def __init__(self):
        self._running = False
        self._last_signal_time = 0
        self._price_history: List[float] = []
        self._check_logs_dir()
        
    def _check_logs_dir(self):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        if not os.path.exists(LOG_FILE):
            pd.DataFrame(columns=[
                "timestamp", "symbol", "signal_type", "imbalance_ratio", 
                "bids_vol", "asks_vol", "price", "confidence"
            ]).to_csv(LOG_FILE, index=False)

    async def start(self):
        """Start the alpha engine."""
        self._running = True
        logger.info("Starting Correlation Alpha Engine...")
        state_manager.add_log("Alpha Engine: Connecting to Binance...", LogLevel.INFO, "alpha_engine")
        
        while self._running:
            try:
                # Ensure polymarket client is ready
                await polymarket_client._ensure_session()
                
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(BINANCE_WS_URL) as ws:
                        logger.info("Connected to Binance WebSocket")
                        state_manager.add_log("Alpha Engine: Connected to Binance Order Book", LogLevel.SUCCESS, "alpha_engine")
                        
                        async for msg in ws:
                            if not self._running:
                                break
                                
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._process_depth_update(json.loads(msg.data))
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"WebSocket error: {ws.exception()}")
                                break
            except Exception as e:
                logger.error(f"Alpha Engine connection error: {e}")
                state_manager.add_log(f"Alpha Engine Error: {str(e)}", LogLevel.ERROR, "alpha_engine")
                await asyncio.sleep(5)  # Reconnect delay

    def stop(self):
        self._running = False
        logger.info("Stopping Alpha Engine...")

    async def _execute_alpha_trade(self, signal: AlphaSignal):
        """Finds matching Polymarket markets and executes trades."""
        if signal.signal_type != "STRONG_BUY":
            return

        state_manager.add_log(f"Alpha Engine: Searching for BTC markets to exploit signal...", LogLevel.INFO, "alpha_engine")
        
        # 1. Fetch relevant markets
        markets = await polymarket_client.get_markets(limit=50, tag="Crypto")
        
        # 2. Filter for Bitcoin Strike markets
        # Example: "Will Bitcoin exceed $50,000?"
        target_markets = [
            m for m in markets 
            if "Bitcoin" in m.question and "exceed" in m.question.lower()
            and m.yes_price < STRIKE_PRICE_CEILING
        ]
        
        if not target_markets:
            state_manager.add_log("Alpha Engine: No suitable BTC strike markets found < 40c.", LogLevel.INFO, "alpha_engine")
            return

        # 3. Pick the best one (lowest price = highest upside for imbalance move)
        target_markets.sort(key=lambda x: x.yes_price)
        best_market = target_markets[0]
        
        # 4. Request execution
        state_manager.add_log(f"Alpha Engine: Executing trade on '{best_market.question[:30]}...' @ {best_market.yes_price:.2f}", LogLevel.TRADE, "alpha_engine")
        
        trade_size = settings.max_single_trade * signal.confidence
        await trade_executor.execute_decision(
            market=best_market,
            direction=TradeDirection.BUY,
            outcome=TradeOutcome.YES,
            size=trade_size
        )

    async def _process_depth_update(self, data: Dict):
        """Process order book depth update."""
        # Calculate volumes
        bids = data.get('bids', [])
        asks = data.get('asks', [])
        
        if not bids or not asks:
            return

        # Sum top 5 levels
        total_bids_vol = sum(float(b[1]) for b in bids)
        total_asks_vol = sum(float(a[1]) for a in asks)
        mid_price = (float(bids[0][0]) + float(asks[0][0])) / 2
        
        # Track price for simple volatility
        self._price_history.append(mid_price)
        if len(self._price_history) > VOLATILITY_WINDOW:
            self._price_history.pop(0)

        # Ratios
        if total_asks_vol == 0:
            return
            
        imbalance_ratio = total_bids_vol / total_asks_vol
        
        # simple volatility check (std dev equivalent or range)
        volatility_high = False
        if len(self._price_history) > 10:
            price_range = max(self._price_history) - min(self._price_history)
            if price_range / mid_price > 0.001:  # 0.1% move in short window
                volatility_high = True

        # Generation Logic
        current_time = time.time()
        if current_time - self._last_signal_time < COOL_DOWN_PERIOD:
            return

        signal_type = "NEUTRAL"
        confidence = 0.0
        
        if imbalance_ratio > IMBALANCE_THRESHOLD and volatility_high:
            signal_type = "STRONG_BUY"
            confidence = min(0.95, (imbalance_ratio / 5.0)) # Cap at 0.95
        elif imbalance_ratio < (1.0 / IMBALANCE_THRESHOLD) and volatility_high:
            signal_type = "STRONG_SELL"
            confidence = min(0.95, ((1.0 / imbalance_ratio) / 5.0))

        if signal_type != "NEUTRAL":
            await self._emit_signal(AlphaSignal(
                timestamp=datetime.utcnow().isoformat(),
                symbol="BTCUSDT",
                signal_type=signal_type,
                imbalance_ratio=imbalance_ratio,
                bids_vol=total_bids_vol,
                asks_vol=total_asks_vol,
                price=mid_price,
                confidence=confidence
            ))
            self._last_signal_time = current_time

    async def _emit_signal(self, signal: AlphaSignal):
        """Log and broadcast the signal."""
        # Log to file
        df = pd.DataFrame([signal.__dict__])
        df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
        
        # Log to Dashboard
        log_level = LogLevel.SUCCESS if "BUY" in signal.signal_type else LogLevel.WARNING
        state_manager.add_log(
            f"ALPHA SIGNAL: {signal.signal_type} (Ratio: {signal.imbalance_ratio:.2f}) - Conf: {signal.confidence:.0%}",
            log_level,
            "alpha_engine"
        )
        
        # Execute trade in background task
        if signal.confidence > 0.8:
            asyncio.create_task(self._execute_alpha_trade(signal))

# Singleton
alpha_engine = CorrelationAlpha()
