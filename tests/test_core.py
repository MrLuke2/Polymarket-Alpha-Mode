"""
POLYMARKET ALPHA MODE - Test Suite
================================
"""

import pytest
import asyncio
from datetime import datetime

# Add project root to path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import (
    Market, AgentVote, AgentType, TradeDirection, TradeOutcome,
    AgentAnalysis, CouncilDecision, WhaleActivity, LogLevel
)
from core.state import StateManager
from agents.swarm import (
    CouncilOfAgents, FundamentalistAgent, SentimentAgent, RiskManagerAgent
)
from strategies.whale_watcher import WhaleWatcher, WhaleProfile
from config.settings import Settings


# ============================================
# MODEL TESTS
# ============================================

class TestModels:
    """Test Pydantic models."""
    
    def test_market_creation(self):
        """Test Market model creation."""
        market = Market(
            id="test_001",
            question="Will it rain tomorrow?",
            yes_price=0.65,
            no_price=0.35,
            volume_24h=50000,
            liquidity=100000
        )
        
        assert market.id == "test_001"
        assert market.yes_price == 0.65
        assert market.spread == pytest.approx(0.0, abs=0.01)
    
    def test_market_spread_calculation(self):
        """Test spread calculation with imperfect prices."""
        market = Market(
            id="test_002",
            question="Test market",
            yes_price=0.60,
            no_price=0.35,  # Doesn't sum to 1
            volume_24h=10000,
            liquidity=50000
        )
        
        assert market.spread == pytest.approx(0.05, abs=0.001)
    
    def test_agent_analysis_creation(self):
        """Test AgentAnalysis model."""
        analysis = AgentAnalysis(
            agent_type=AgentType.FUNDAMENTALIST,
            agent_name="Test Agent",
            vote=AgentVote.YES,
            confidence=0.75,
            reasoning="Test reasoning",
            data_sources=["source1", "source2"]
        )
        
        assert analysis.vote == AgentVote.YES
        assert analysis.confidence == 0.75
        assert len(analysis.data_sources) == 2


# ============================================
# STATE MANAGER TESTS
# ============================================

class TestStateManager:
    """Test state management."""
    
    def test_singleton_pattern(self):
        """Test StateManager singleton."""
        sm1 = StateManager()
        sm2 = StateManager()
        assert sm1 is sm2
    
    def test_add_and_get_logs(self):
        """Test log entry management."""
        sm = StateManager()
        
        entry = sm.add_log(
            message="Test log message",
            level=LogLevel.INFO,
            source="test"
        )
        
        logs = sm.get_logs(limit=10)
        assert len(logs) > 0
        assert any(log.message == "Test log message" for log in logs)
    
    def test_portfolio_update(self):
        """Test portfolio state updates."""
        from core.models import Portfolio
        
        sm = StateManager()
        portfolio = Portfolio(
            total_value=15000,
            cash_balance=5000,
            positions=[],
            daily_pnl=500
        )
        
        sm.update_portfolio(portfolio)
        retrieved = sm.get_portfolio()
        
        assert retrieved.total_value == 15000
        assert retrieved.daily_pnl == 500


# ============================================
# AGENT TESTS
# ============================================

class TestAgents:
    """Test individual agents."""
    
    @pytest.fixture
    def sample_market(self):
        return Market(
            id="agent_test_001",
            question="Will BTC exceed $50,000?",
            yes_price=0.55,
            no_price=0.45,
            volume_24h=75000,
            liquidity=120000
        )
    
    @pytest.mark.asyncio
    async def test_fundamentalist_agent(self, sample_market):
        """Test Fundamentalist agent analysis."""
        agent = FundamentalistAgent()
        
        analysis = await agent.analyze(
            sample_market,
            context={"news": ["BTC ETF approved", "Institutional buying increasing"]}
        )
        
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_type == AgentType.FUNDAMENTALIST
        assert analysis.vote in [AgentVote.YES, AgentVote.NO, AgentVote.ABSTAIN]
        assert 0 <= analysis.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_sentiment_agent(self, sample_market):
        """Test Sentiment agent analysis."""
        agent = SentimentAgent()
        
        analysis = await agent.analyze(
            sample_market,
            context={"social": {"twitter_sentiment": 0.7}}
        )
        
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_type == AgentType.SENTIMENT
    
    @pytest.mark.asyncio
    async def test_risk_manager_agent(self, sample_market):
        """Test Risk Manager agent analysis."""
        agent = RiskManagerAgent()
        
        analysis = await agent.analyze(
            sample_market,
            context={}
        )
        
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_type == AgentType.RISK_MANAGER


# ============================================
# COUNCIL TESTS
# ============================================

class TestCouncil:
    """Test Council of Agents."""
    
    @pytest.fixture
    def council(self):
        return CouncilOfAgents()
    
    @pytest.fixture
    def sample_market(self):
        return Market(
            id="council_test_001",
            question="Test council market",
            yes_price=0.60,
            no_price=0.40,
            volume_24h=100000,
            liquidity=150000
        )
    
    def test_council_initialization(self, council):
        """Test council has all agents."""
        assert len(council.agents) == 3
        agent_types = [a.agent_type for a in council.agents]
        assert AgentType.FUNDAMENTALIST in agent_types
        assert AgentType.SENTIMENT in agent_types
        assert AgentType.RISK_MANAGER in agent_types
    
    @pytest.mark.asyncio
    async def test_council_deliberation(self, council, sample_market):
        """Test full council deliberation."""
        decision = await council.deliberate(sample_market)
        
        assert isinstance(decision, CouncilDecision)
        assert len(decision.analyses) == 3
        assert decision.final_decision in [AgentVote.YES, AgentVote.NO, AgentVote.ABSTAIN]
        assert 0 <= decision.consensus_score <= 1


# ============================================
# WHALE WATCHER TESTS
# ============================================

class TestWhaleWatcher:
    """Test Whale Watcher functionality."""
    
    @pytest.fixture
    def watcher(self):
        return WhaleWatcher()
    
    def test_whale_initialization(self, watcher):
        """Test whale profiles loaded."""
        assert len(watcher.whales) > 0
    
    def test_get_leaderboard(self, watcher):
        """Test leaderboard retrieval."""
        leaderboard = watcher.get_whale_leaderboard()
        
        assert len(leaderboard) > 0
        assert "alias" in leaderboard[0]
        assert "win_rate" in leaderboard[0]
    
    def test_add_whale(self, watcher):
        """Test adding new whale."""
        new_whale = WhaleProfile(
            address="0xnewwhale123",
            alias="NewWhale",
            win_rate_30d=0.80,
            pnl_30d=100000,
            avg_trade_size=10000,
            specialty="crypto",
            trust_score=0.9
        )
        
        initial_count = len(watcher.whales)
        watcher.add_whale(new_whale)
        
        assert len(watcher.whales) == initial_count + 1
        assert "0xnewwhale123" in watcher.whales


# ============================================
# CONFIGURATION TESTS
# ============================================

class TestConfiguration:
    """Test configuration management."""
    
    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.app_name == "Polymarket Alpha Mode"
        assert settings.max_single_trade == 500.0
        assert settings.council_voting_threshold == 0.67
    
    def test_whale_addresses_loaded(self):
        """Test whale addresses have defaults."""
        settings = Settings()
        
        assert len(settings.whale_addresses) == 5


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Integration tests for full workflows."""
    
    @pytest.mark.asyncio
    async def test_full_trade_flow(self):
        """Test complete trade evaluation flow."""
        from agents.swarm import council
        
        market = Market(
            id="integration_001",
            question="Integration test market",
            yes_price=0.70,
            no_price=0.30,
            volume_24h=200000,
            liquidity=300000
        )
        
        decision = await council.deliberate(
            market,
            context={
                "news": ["Positive news item"],
                "social": {"sentiment": 0.8}
            }
        )
        
        # Verify decision structure
        assert decision.market_id == "integration_001"
        assert len(decision.analyses) == 3
        assert decision.summary != ""
        
        # If approved, check trade parameters
        if decision.should_execute:
            assert decision.recommended_direction is not None
            assert decision.recommended_outcome is not None
            assert decision.recommended_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
