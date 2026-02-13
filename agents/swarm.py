"""
POLYMARKET ALPHA MODE - Council of Agents (Swarm Intelligence)
============================================================
Multi-agent voting system for trade decisions.
Three specialized agents must reach 2/3 consensus to execute.

Agent A (The Fundamentalist): News/facts analysis
Agent B (The Sentiment Analyst): Social sentiment & trends  
Agent C (The Risk Manager): Volatility & portfolio risk
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from loguru import logger

from core.models import (
    Market, AgentAnalysis, AgentVote, AgentType, CouncilDecision,
    TradeDirection, TradeOutcome, LogLevel
)
from core.state import state_manager
from core.llm import llm_manager
from config.settings import settings


# ============================================
# BASE AGENT
# ============================================

class BaseAgent(ABC):
    """Abstract base class for all council agents."""
    
    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self._llm_client = None
    
    @abstractmethod
    async def analyze(self, market: Market, context: Dict[str, Any]) -> AgentAnalysis:
        """Analyze a market and return vote with reasoning."""
        pass
    
    def _create_analysis(
        self,
        vote: AgentVote,
        confidence: float,
        reasoning: str,
        data_sources: List[str],
        analysis_time_ms: int
    ) -> AgentAnalysis:
        """Helper to create standardized analysis response."""
        return AgentAnalysis(
            agent_type=self.agent_type,
            agent_name=self.name,
            vote=vote,
            confidence=confidence,
            reasoning=reasoning,
            data_sources=data_sources,
            analysis_time_ms=analysis_time_ms
        )


# ============================================
# THE FUNDAMENTALIST (Agent A)
# ============================================

class FundamentalistAgent(BaseAgent):
    """
    Analyzes news, facts, and fundamental data.
    Focuses on: official announcements, verified news, historical patterns.
    """
    
    def __init__(self):
        super().__init__(AgentType.FUNDAMENTALIST, "The Fundamentalist")
        self.system_prompt = """You are The Fundamentalist - a rigorous, fact-based analyst.
        
Your role: Analyze prediction markets based on HARD DATA and VERIFIED FACTS only.

Analysis Framework:
1. What are the KNOWN FACTS relevant to this market?
2. What historical precedents exist?
3. What official sources/announcements are relevant?
4. What is the base rate for similar events?

You IGNORE: Social media hype, speculation, "vibes"
You TRUST: Official sources, historical data, verified reporting

Output your analysis as JSON:
{
    "vote": "yes" | "no" | "abstain",
    "confidence": 0.0-1.0,
    "key_facts": ["fact1", "fact2"],
    "historical_precedent": "description",
    "reasoning": "your analysis"
}"""

    async def analyze(self, market: Market, context: Dict[str, Any]) -> AgentAnalysis:
        """Analyze market based on fundamentals."""
        start_time = datetime.utcnow()
        
        try:
            # Build analysis prompt
            news_context = context.get("news", [])
            news_summary = "\n".join([f"- {n}" for n in news_context[:5]]) if news_context else "No recent news available."
            
            analysis_prompt = f"""Analyze this prediction market:

MARKET: {market.question}
CURRENT YES PRICE: {market.yes_price:.2%}
CURRENT NO PRICE: {market.no_price:.2%}
24H VOLUME: ${market.volume_24h:,.0f}
LIQUIDITY: ${market.liquidity:,.0f}

RECENT NEWS:
{news_summary}

Should we take a position? Analyze fundamentals only."""

            # Try LLM analysis first, fall back to rule-based
            if llm_manager.has_llm:
                llm_result = await llm_manager.analyze(
                    system_prompt=self.system_prompt,
                    user_prompt=analysis_prompt,
                    temperature=0.3
                )
                if llm_result:
                    vote_str = llm_result.get("vote", "abstain").lower()
                    vote = AgentVote(vote_str) if vote_str in ["yes", "no", "abstain"] else AgentVote.ABSTAIN
                    analysis = {
                        "vote": vote,
                        "confidence": float(llm_result.get("confidence", 0.5)),
                        "reasoning": llm_result.get("reasoning", "LLM analysis complete.")
                    }
                else:
                    analysis = await self._rule_based_analysis(market, context)
            else:
                analysis = await self._rule_based_analysis(market, context)
            
            analysis_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self._create_analysis(
                vote=analysis["vote"],
                confidence=analysis["confidence"],
                reasoning=analysis["reasoning"],
                data_sources=["news_feed", "market_data", "historical_patterns"],
                analysis_time_ms=analysis_time
            )
            
        except Exception as e:
            logger.error(f"Fundamentalist analysis failed: {e}")
            return self._create_analysis(
                vote=AgentVote.ABSTAIN,
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                data_sources=[],
                analysis_time_ms=0
            )
    
    async def _rule_based_analysis(self, market: Market, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based analysis fallback when LLM unavailable."""
        # High volume + mispricing = opportunity
        mispricing = abs(market.yes_price - 0.5)  # Distance from 50/50
        
        if market.volume_24h > 50000 and mispricing > 0.15:
            # Strong signal when high volume confirms price movement
            vote = AgentVote.YES
            confidence = min(0.8, 0.5 + mispricing)
            reasoning = f"High volume (${market.volume_24h:,.0f}) confirms price direction. Mispricing of {mispricing:.1%} suggests opportunity."
        elif market.volume_24h < 5000:
            vote = AgentVote.ABSTAIN
            confidence = 0.3
            reasoning = f"Insufficient volume (${market.volume_24h:,.0f}) for confident fundamental analysis."
        else:
            vote = AgentVote.NO
            confidence = 0.5
            reasoning = "No clear fundamental edge detected. Price appears fairly valued."
        
        return {"vote": vote, "confidence": confidence, "reasoning": reasoning}


# ============================================
# THE SENTIMENT ANALYST (Agent B)
# ============================================

class SentimentAgent(BaseAgent):
    """
    Analyzes social sentiment, trends, and market psychology.
    Focuses on: Twitter/X trends, community sentiment, momentum.
    """
    
    def __init__(self):
        super().__init__(AgentType.SENTIMENT, "The Sentiment Analyst")
        self.system_prompt = """You are The Sentiment Analyst - a social dynamics expert.

Your role: Read the CROWD. Understand MOMENTUM. Spot TRENDS before they peak.

Analysis Framework:
1. What is social media saying about this topic?
2. Is sentiment RISING or FALLING?
3. Are there any viral moments or influencer takes?
4. What's the "vibe" - fear, greed, uncertainty?

You VALUE: Trends, momentum, crowd psychology, viral potential
You WATCH: Influencers, trending hashtags, community reactions

Output your analysis as JSON:
{
    "vote": "yes" | "no" | "abstain",
    "confidence": 0.0-1.0,
    "sentiment_score": -1.0 to 1.0,
    "trending_terms": ["term1", "term2"],
    "reasoning": "your analysis"
}"""

    async def analyze(self, market: Market, context: Dict[str, Any]) -> AgentAnalysis:
        """Analyze market based on sentiment."""
        start_time = datetime.utcnow()
        
        try:
            social_data = context.get("social", {})
            
            # Rule-based sentiment analysis
            analysis = await self._rule_based_analysis(market, context)
            
            analysis_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self._create_analysis(
                vote=analysis["vote"],
                confidence=analysis["confidence"],
                reasoning=analysis["reasoning"],
                data_sources=["twitter_trends", "reddit_sentiment", "discord_activity"],
                analysis_time_ms=analysis_time
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._create_analysis(
                vote=AgentVote.ABSTAIN,
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                data_sources=[],
                analysis_time_ms=0
            )
    
    async def _rule_based_analysis(self, market: Market, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based sentiment analysis fallback."""
        # Check for momentum based on price movement and volume
        price_momentum = market.yes_price - 0.5
        volume_signal = min(1.0, market.volume_24h / 100000)  # Normalize volume
        
        sentiment_score = price_momentum * volume_signal
        
        if abs(sentiment_score) > 0.1:
            vote = AgentVote.YES
            direction = "bullish" if sentiment_score > 0 else "bearish"
            confidence = min(0.75, 0.4 + abs(sentiment_score))
            reasoning = f"Strong {direction} sentiment detected. Momentum score: {sentiment_score:.2f}. Volume confirms crowd conviction."
        elif market.spread < 0.02:
            vote = AgentVote.YES
            confidence = 0.6
            reasoning = "Tight spread indicates strong market consensus. Riding the crowd sentiment."
        else:
            vote = AgentVote.ABSTAIN
            confidence = 0.4
            reasoning = "Mixed signals. No clear sentiment trend to capitalize on."
        
        return {"vote": vote, "confidence": confidence, "reasoning": reasoning}


# ============================================
# THE RISK MANAGER (Agent C)
# ============================================

class RiskManagerAgent(BaseAgent):
    """
    Evaluates risk and can VETO trades.
    Focuses on: Volatility, portfolio exposure, drawdown risk.
    """
    
    def __init__(self):
        super().__init__(AgentType.RISK_MANAGER, "The Risk Manager")
        self.system_prompt = """You are The Risk Manager - the voice of caution.

Your role: PROTECT capital. VETO bad risk/reward. ENFORCE discipline.

Analysis Framework:
1. What is the MAXIMUM LOSS scenario?
2. How volatile is this market?
3. Does this fit our portfolio risk limits?
4. Is the risk/reward ratio acceptable (min 2:1)?

You VETO if:
- Daily volatility > 15%
- Position would exceed 10% of portfolio
- Risk/reward ratio < 2:1
- Market has unusual activity suggesting manipulation

Output your analysis as JSON:
{
    "vote": "yes" | "no" | "abstain",
    "confidence": 0.0-1.0,
    "risk_score": 0.0-1.0 (higher = riskier),
    "max_position_size": number,
    "reasoning": "your analysis"
}"""

    async def analyze(self, market: Market, context: Dict[str, Any]) -> AgentAnalysis:
        """Analyze market risk."""
        start_time = datetime.utcnow()
        
        try:
            portfolio = context.get("portfolio")
            
            analysis = await self._rule_based_analysis(market, context)
            
            analysis_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self._create_analysis(
                vote=analysis["vote"],
                confidence=analysis["confidence"],
                reasoning=analysis["reasoning"],
                data_sources=["volatility_calc", "portfolio_analysis", "liquidity_check"],
                analysis_time_ms=analysis_time
            )
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            return self._create_analysis(
                vote=AgentVote.NO,  # Default to NO on risk analysis failure
                confidence=1.0,
                reasoning=f"Risk analysis failed - defaulting to VETO: {str(e)}",
                data_sources=[],
                analysis_time_ms=0
            )
    
    async def _rule_based_analysis(self, market: Market, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based risk analysis."""
        portfolio = context.get("portfolio")
        
        # Calculate risk metrics
        spread_risk = market.spread / 0.1  # Normalize spread (10% = max)
        liquidity_risk = 1.0 - min(1.0, market.liquidity / 50000)  # Lower liquidity = higher risk
        
        # Check portfolio constraints
        max_position = settings.max_single_trade
        if portfolio:
            max_position = min(max_position, portfolio.total_value * 0.1)  # 10% max
        
        # Composite risk score
        risk_score = (spread_risk * 0.3) + (liquidity_risk * 0.4) + (0.3 * (1 - market.volume_24h / 100000))
        risk_score = max(0, min(1, risk_score))
        
        # Decision logic
        if risk_score > settings.volatility_threshold:
            vote = AgentVote.NO
            confidence = 0.9
            reasoning = f"VETO: Risk score {risk_score:.2f} exceeds threshold. Spread: {market.spread:.2%}, Liquidity: ${market.liquidity:,.0f}"
        elif market.liquidity < 10000:
            vote = AgentVote.NO
            confidence = 0.85
            reasoning = f"VETO: Insufficient liquidity (${market.liquidity:,.0f}). Exit risk too high."
        elif risk_score > 0.5:
            vote = AgentVote.ABSTAIN
            confidence = 0.6
            reasoning = f"Elevated risk ({risk_score:.2f}). Proceed with reduced position size: ${max_position * 0.5:.0f}"
        else:
            vote = AgentVote.YES
            confidence = 0.7
            reasoning = f"Risk acceptable ({risk_score:.2f}). Max position: ${max_position:.0f}. Good liquidity and tight spread."
        
        return {"vote": vote, "confidence": confidence, "reasoning": reasoning}


# ============================================
# THE COUNCIL
# ============================================

class CouncilOfAgents:
    """
    Orchestrates the multi-agent voting system.
    Requires 2/3 majority to execute trades.
    """
    
    def __init__(self):
        self.agents: List[BaseAgent] = [
            FundamentalistAgent(),
            SentimentAgent(),
            RiskManagerAgent()
        ]
        self.voting_threshold = settings.council_voting_threshold
        logger.info(f"Council initialized with {len(self.agents)} agents")
    
    async def deliberate(
        self,
        market: Market,
        context: Optional[Dict[str, Any]] = None
    ) -> CouncilDecision:
        """
        All agents analyze the market and vote.
        Returns collective decision with full reasoning.
        """
        context = context or {}
        context["portfolio"] = state_manager.get_portfolio()
        
        state_manager.add_log(
            f"COUNCIL CONVENED: Analyzing '{market.question[:50]}...'",
            level=LogLevel.INFO,
            source="council"
        )
        
        # Run all agents concurrently
        analyses = await asyncio.gather(
            *[agent.analyze(market, context) for agent in self.agents],
            return_exceptions=True
        )
        
        # Filter out exceptions and log them
        valid_analyses: List[AgentAnalysis] = []
        for i, result in enumerate(analyses):
            if isinstance(result, Exception):
                logger.error(f"Agent {self.agents[i].name} failed: {result}")
                state_manager.increment_errors()
            else:
                valid_analyses.append(result)
                # Log each agent's vote
                state_manager.add_log(
                    f"  {result.agent_name}: {result.vote.value.upper()} "
                    f"(conf: {result.confidence:.0%}) - {result.reasoning[:80]}...",
                    level=LogLevel.INFO,
                    source=result.agent_type.value
                )
        
        # Tally votes
        yes_votes = sum(1 for a in valid_analyses if a.vote == AgentVote.YES)
        no_votes = sum(1 for a in valid_analyses if a.vote == AgentVote.NO)
        total_votes = len(valid_analyses)
        
        # Check for Risk Manager veto
        risk_veto = any(
            a.agent_type == AgentType.RISK_MANAGER and a.vote == AgentVote.NO
            for a in valid_analyses
        )
        
        # Determine final decision
        consensus_score = yes_votes / total_votes if total_votes > 0 else 0
        
        if risk_veto:
            final_decision = AgentVote.NO
            should_execute = False
            summary = "VETOED by Risk Manager. Trade rejected for safety."
        elif consensus_score >= self.voting_threshold:
            final_decision = AgentVote.YES
            should_execute = True
            summary = f"APPROVED: {yes_votes}/{total_votes} agents voted YES. Consensus: {consensus_score:.0%}"
        else:
            final_decision = AgentVote.NO
            should_execute = False
            summary = f"REJECTED: Only {yes_votes}/{total_votes} voted YES. Below {self.voting_threshold:.0%} threshold."
        
        # Determine recommended trade parameters if approved
        recommended_direction = None
        recommended_outcome = None
        recommended_size = None
        
        if should_execute:
            # Use highest confidence agent's implicit direction
            avg_confidence = sum(a.confidence for a in valid_analyses if a.vote == AgentVote.YES) / max(1, yes_votes)
            recommended_direction = TradeDirection.BUY
            recommended_outcome = TradeOutcome.YES if market.yes_price < 0.5 else TradeOutcome.NO
            recommended_size = min(
                settings.max_single_trade,
                settings.max_single_trade * avg_confidence
            )
        
        decision = CouncilDecision(
            market_id=market.id,
            market_question=market.question,
            analyses=valid_analyses,
            final_decision=final_decision,
            consensus_score=consensus_score,
            should_execute=should_execute,
            recommended_direction=recommended_direction,
            recommended_outcome=recommended_outcome,
            recommended_size=recommended_size,
            summary=summary
        )
        
        state_manager.add_council_decision(decision)
        
        return decision
    
    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents for dashboard."""
        return [
            {
                "name": agent.name,
                "type": agent.agent_type.value,
                "active": True
            }
            for agent in self.agents
        ]


# ============================================
# MODULE EXPORTS
# ============================================

# Singleton council instance
council = CouncilOfAgents()
