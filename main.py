"""
POLYMARKET ALPHA MODE - Main Backend Runner
===========================================
Orchestrates all trading components.

Run: python main.py
"""

import asyncio
import signal
import sys
from typing import Optional
from datetime import datetime

from loguru import logger

from core.state import state_manager
from core.models import LogLevel, Market
from agents.swarm import council
from strategies.whale_watcher import whale_watcher
from strategies.correlation_alpha import alpha_engine
from config.settings import settings


# ============================================
# LOGGING CONFIGURATION
# ============================================

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/alpha_mode_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG"
)


# ============================================
# MAIN ORCHESTRATOR
# ============================================

class AlphaModeOrchestrator:
    """
    Main orchestrator that coordinates all system components.
    """
    
    def __init__(self):
        self._running = False
        self._tasks: list = []
        self._shutdown_event = asyncio.Event()
        
        logger.info("AlphaMode Orchestrator initialized")
    
    async def start(self):
        """Start all system components."""
        self._running = True
        state_manager.set_running(True)
        state_manager.set_agents_active(3)
        
        state_manager.add_log(
            "⚡ ALPHA MODE ACTIVATED ⚡",
            level=LogLevel.SUCCESS,
            source="system"
        )
        
        logger.info("Starting all components...")
        
        # Start component tasks
        self._tasks = [
            asyncio.create_task(self._market_scanner()),
            asyncio.create_task(whale_watcher.start()),
            asyncio.create_task(alpha_engine.start()),
            asyncio.create_task(self._portfolio_updater()),
            asyncio.create_task(self._btc_price_tracker()),
        ]
        
        # Wait for shutdown signal
        await self._shutdown_event.wait()
        
        # Cleanup
        await self.stop()
    
    async def stop(self):
        """Stop all components gracefully."""
        logger.info("Shutting down...")
        
        self._running = False
        state_manager.set_running(False)
        whale_watcher.stop()
        alpha_engine.stop()
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        state_manager.add_log(
            "System shutdown complete",
            level=LogLevel.WARNING,
            source="system"
        )
        
        logger.info("Shutdown complete")
    
    def request_shutdown(self):
        """Request graceful shutdown."""
        self._shutdown_event.set()
    
    # ============================================
    # COMPONENT TASKS
    # ============================================
    
    async def _market_scanner(self):
        """
        Scan markets and evaluate trading opportunities.
        Sends promising markets to the Council for analysis.
        """
        logger.info("Market scanner started")
        
        while self._running:
            try:
                # In production, fetch markets from Polymarket API
                # For demo, we'll create sample markets periodically
                
                state_manager.add_log(
                    "Scanning markets for opportunities...",
                    level=LogLevel.INFO,
                    source="scanner"
                )
                
                # Demo: Analyze a market every 60 seconds
                demo_market = Market(
                    id="demo_001",
                    question="Will Bitcoin exceed $50,000 by end of Q1 2024?",
                    yes_price=0.62,
                    no_price=0.38,
                    volume_24h=125000,
                    liquidity=85000,
                    tags=["crypto", "bitcoin"]
                )
                
                # Send to council for analysis
                decision = await council.deliberate(
                    demo_market,
                    context={
                        "news": [
                            "Bitcoin ETF approval driving institutional interest",
                            "Halving event expected in April 2024",
                            "Major banks announcing crypto custody services"
                        ]
                    }
                )
                
                if decision.should_execute:
                    state_manager.add_log(
                        f"Trade signal generated: {decision.recommended_direction.value.upper()} "
                        f"{decision.recommended_outcome.value.upper()} @ ${decision.recommended_size:.0f}",
                        level=LogLevel.SUCCESS,
                        source="executor"
                    )
                
                await asyncio.sleep(60)  # Scan every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Market scanner error: {e}")
                state_manager.increment_errors()
                await asyncio.sleep(30)
    
    async def _portfolio_updater(self):
        """
        Periodically update portfolio values and positions.
        """
        logger.info("Portfolio updater started")
        
        while self._running:
            try:
                portfolio = state_manager.get_portfolio()
                
                # In production, fetch real positions from Polymarket
                # For demo, simulate small PnL changes
                import random
                portfolio.total_value += random.uniform(-50, 80)
                portfolio.daily_pnl = portfolio.total_value - 10000
                portfolio.updated_at = datetime.utcnow()
                
                state_manager.update_portfolio(portfolio)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Portfolio updater error: {e}")
                await asyncio.sleep(60)
    
    async def _btc_price_tracker(self):
        """
        Track BTC price for comparison chart.
        """
        logger.info("BTC price tracker started")
        
        while self._running:
            try:
                # In production, fetch from Binance/CoinGecko
                # For demo, simulate price movement
                import random
                base_price = 45000
                price = base_price + random.uniform(-2000, 2000)
                
                state_manager.add_btc_price(price)
                
                await asyncio.sleep(60)  # Update every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"BTC tracker error: {e}")
                await asyncio.sleep(120)


# ============================================
# SIGNAL HANDLERS
# ============================================

orchestrator: Optional[AlphaModeOrchestrator] = None


def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    if orchestrator:
        orchestrator.request_shutdown()


# ============================================
# ENTRY POINT
# ============================================

async def main():
    """Main entry point."""
    global orchestrator
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    logger.info("=" * 50)
    logger.info("  POLYMARKET ALPHA MODE - Starting...")
    logger.info(f"  Environment: {settings.environment.value}")
    logger.info(f"  Max Trade Size: ${settings.max_single_trade}")
    logger.info(f"  Council Threshold: {settings.council_voting_threshold:.0%}")
    logger.info("=" * 50)
    
    orchestrator = AlphaModeOrchestrator()
    
    try:
        await orchestrator.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("AlphaMode terminated")


if __name__ == "__main__":
    asyncio.run(main())
