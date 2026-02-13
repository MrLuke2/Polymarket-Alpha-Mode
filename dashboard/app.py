"""
POLYMARKET ALPHA MODE - War Room Dashboard
========================================
Cyberpunk Bloomberg Terminal aesthetic.
Real-time monitoring and control interface.

Run: streamlit run dashboard/app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os

# Auto-refresh for real-time updates
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import state_manager
from core.models import LogLevel, Market, WatchedMarket
from agents.swarm import council
from strategies.whale_watcher import whale_watcher
from config.settings import settings
from utils.dossier import parse_whale_dossier, get_whale_bio
from utils.github import get_repo_info
from strategies.correlation_alpha import alpha_engine
from agents.marketing.press_secretary import press_secretary, PNL_CARD_PATH, TWEET_DRAFT_PATH

# Load Dossier Data
@st.cache_data
def load_whale_dossier():
    try:
        dossier_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "polymarket_whale.md")
        if os.path.exists(dossier_path):
            with open(dossier_path, "r", encoding="utf-8") as f:
                content = f.read()
            return parse_whale_dossier(content)
    except Exception as e:
        print(f"Error loading dossier: {e}")
    return {}

whale_bios = load_whale_dossier()


# ============================================
# PAGE CONFIG & STYLING
# ============================================

st.set_page_config(
    page_title="POLYMARKET ALPHA MODE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 5 seconds when system is running
if HAS_AUTOREFRESH:
    refresh_interval = settings.dashboard_refresh_interval * 1000  # Convert to ms
    st_autorefresh(interval=refresh_interval, limit=None, key="dashboard_refresh")

# Cyberpunk / Bloomberg Terminal CSS
CYBERPUNK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@400;700;900&display=swap');
    
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-tertiary: #1a1a2e;
        --accent-cyan: #00f5ff;
        --accent-magenta: #ff00ff;
        --accent-green: #00ff88;
        --accent-red: #ff3366;
        --accent-yellow: #ffcc00;
        --accent-orange: #ff6600;
        --text-primary: #e0e0e0;
        --text-secondary: #888;
        --border-color: #2a2a3e;
        --glow-cyan: 0 0 20px rgba(0, 245, 255, 0.3);
        --glow-magenta: 0 0 20px rgba(255, 0, 255, 0.3);
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-primary) 100%);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main title styling */
    .alpha-mode-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta), var(--accent-cyan));
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 3s ease infinite;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: var(--glow-cyan);
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }
    
    .subtitle {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-secondary);
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    
    /* Panel styling */
    .panel {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--glow-cyan);
    }
    
    .panel-title {
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        color: var(--accent-cyan);
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Log entry styling */
    .log-entry {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 0.4rem 0.6rem;
        margin: 0.2rem 0;
        border-radius: 4px;
        border-left: 3px solid var(--accent-cyan);
        background: rgba(0, 245, 255, 0.05);
    }
    
    .log-entry.success { border-left-color: var(--accent-green); background: rgba(0, 255, 136, 0.05); }
    .log-entry.warning { border-left-color: var(--accent-yellow); background: rgba(255, 204, 0, 0.05); }
    .log-entry.error { border-left-color: var(--accent-red); background: rgba(255, 51, 102, 0.05); }
    .log-entry.trade { border-left-color: var(--accent-magenta); background: rgba(255, 0, 255, 0.08); }
    
    .log-timestamp {
        color: var(--text-secondary);
        font-size: 0.65rem;
    }
    
    .log-source {
        color: var(--accent-cyan);
        font-weight: 500;
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent-cyan);
    }
    
    .metric-value.positive { color: var(--accent-green); }
    .metric-value.negative { color: var(--accent-red); }
    
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }
    
    /* Sniper scope items */
    .scope-item {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .scope-market {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-primary);
    }
    
    .scope-price {
        font-family: 'Orbitron', monospace;
        font-size: 1rem;
        color: var(--accent-green);
    }
    
    /* Whale card */
    .whale-card {
        background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
        border: 1px solid var(--accent-magenta);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .whale-alias {
        font-family: 'Orbitron', monospace;
        font-size: 1rem;
        color: var(--accent-magenta);
    }
    
    .whale-stats {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }
    
    /* Status indicator */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .status-dot.active { background: var(--accent-green); }
    .status-dot.inactive { background: var(--accent-red); animation: none; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Agent cards */
    .agent-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
    }
    
    .agent-name {
        font-family: 'Orbitron', monospace;
        font-size: 0.85rem;
        color: var(--accent-cyan);
    }
    
    .agent-type {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-secondary);
        text-transform: uppercase;
    }
    
    /* Override Streamlit defaults */
    .stMetric {
        background: var(--bg-tertiary);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .stMetric label {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-secondary) !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        color: var(--accent-cyan) !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-cyan);
        border-radius: 3px;
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'Orbitron', monospace;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta));
        color: var(--bg-primary);
        border: none;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, var(--accent-magenta), var(--accent-cyan));
        box-shadow: var(--glow-magenta);
    }
</style>
"""

st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)


# ============================================
# HEADER
# ============================================

st.markdown('<h1 class="alpha-mode-title">⚡ POLYMARKET ALPHA MODE ⚡</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">ELITE PREDICTION MARKET INTELLIGENCE SYSTEM</p>', unsafe_allow_html=True)

# System status bar
sys_state = state_manager.get_system_state()
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    status_class = "active" if sys_state.is_running else "inactive"
    status_text = "ONLINE" if sys_state.is_running else "STANDBY"
    st.markdown(f'<span class="status-dot {status_class}"></span> **{status_text}**', unsafe_allow_html=True)

with col2:
    st.markdown(f"🤖 **{sys_state.agents_active}** Agents Active")

with col3:
    st.markdown(f"🎯 **{sys_state.markets_watched}** Markets Tracked")

with col4:
    uptime_hours = sys_state.uptime_seconds // 3600
    uptime_mins = (sys_state.uptime_seconds % 3600) // 60
    st.markdown(f"⏱️ Uptime: **{uptime_hours}h {uptime_mins}m**")

with col5:
    st.markdown(f"⚠️ Errors (24h): **{sys_state.errors_24h}**")

st.markdown("---")


# ============================================
# MAIN DASHBOARD LAYOUT
# ============================================

# Top row: PnL Chart + Metrics
col_chart, col_metrics = st.columns([3, 1])

with col_chart:
    st.markdown('<div class="panel"><div class="panel-title">📈 Portfolio Performance vs BTC</div>', unsafe_allow_html=True)
    
    # Get portfolio and BTC history
    portfolio_history = state_manager.get_portfolio_history()
    btc_history = state_manager.get_btc_history()
    
    # Create demo data if empty
    if not portfolio_history:
        import random
        base_value = 10000
        for i in range(100):
            portfolio_history.append({
                "timestamp": (datetime.utcnow() - timedelta(hours=100-i)).isoformat(),
                "value": base_value + random.uniform(-500, 800) + (i * 15)
            })
            btc_history.append({
                "timestamp": (datetime.utcnow() - timedelta(hours=100-i)).isoformat(),
                "price": 42000 + random.uniform(-2000, 2000) + (i * 50)
            })
    
    # Create dual-axis chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Portfolio line
    if portfolio_history:
        df_portfolio = pd.DataFrame(portfolio_history)
        df_portfolio['timestamp'] = pd.to_datetime(df_portfolio['timestamp'])
        fig.add_trace(
            go.Scatter(
                x=df_portfolio['timestamp'],
                y=df_portfolio['value'],
                name="Portfolio Value",
                line=dict(color="#00f5ff", width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 245, 255, 0.1)'
            ),
            secondary_y=False
        )
    
    # BTC line
    if btc_history:
        df_btc = pd.DataFrame(btc_history)
        df_btc['timestamp'] = pd.to_datetime(df_btc['timestamp'])
        fig.add_trace(
            go.Scatter(
                x=df_btc['timestamp'],
                y=df_btc['price'],
                name="BTC Price",
                line=dict(color="#ff00ff", width=2, dash='dot')
            ),
            secondary_y=True
        )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(18, 18, 26, 0.8)',
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="JetBrains Mono", size=10)
        ),
        xaxis=dict(gridcolor='rgba(42, 42, 62, 0.5)'),
        yaxis=dict(gridcolor='rgba(42, 42, 62, 0.5)')
    )
    
    fig.update_yaxes(title_text="Portfolio ($)", secondary_y=False, color="#00f5ff")
    fig.update_yaxes(title_text="BTC ($)", secondary_y=True, color="#ff00ff")
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_metrics:
    st.markdown('<div class="panel"><div class="panel-title">💰 Metrics</div>', unsafe_allow_html=True)
    
    portfolio = state_manager.get_portfolio()
    
    # Total Value
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">${portfolio.total_value:,.0f}</div>
            <div class="metric-label">Total Value</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Daily PnL
    pnl_class = "positive" if portfolio.daily_pnl >= 0 else "negative"
    pnl_sign = "+" if portfolio.daily_pnl >= 0 else ""
    st.markdown(f'''
        <div class="metric-card" style="margin-top: 0.5rem;">
            <div class="metric-value {pnl_class}">{pnl_sign}${portfolio.daily_pnl:,.0f}</div>
            <div class="metric-label">Daily PnL</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Win Rate
    st.markdown(f'''
        <div class="metric-card" style="margin-top: 0.5rem;">
            <div class="metric-value">{portfolio.win_rate:.0%}</div>
            <div class="metric-label">Win Rate</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Total Trades
    st.markdown(f'''
        <div class="metric-card" style="margin-top: 0.5rem;">
            <div class="metric-value">{portfolio.total_trades}</div>
            <div class="metric-label">Total Trades</div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# Middle row: AI Monologue + Sniper Scope
col_log, col_scope = st.columns([2, 1])

with col_log:
    st.markdown('<div class="panel"><div class="panel-title">🧠 AI Monologue Feed</div>', unsafe_allow_html=True)
    
    # Log container with scrolling
    log_container = st.container()
    
    with log_container:
        logs = state_manager.get_logs(limit=15)
        
        if not logs:
            # Demo logs
            demo_logs = [
                (LogLevel.INFO, "council", "Analyzing 'Will Fed cut rates in March?' market..."),
                (LogLevel.SUCCESS, "fundamentalist", "VOTE: YES (78% confidence) - Historical pattern matches Q1 rate cuts"),
                (LogLevel.WARNING, "sentiment", "VOTE: YES (65% confidence) - Twitter sentiment bullish on rate cuts"),
                (LogLevel.INFO, "risk_manager", "VOTE: YES (71% confidence) - Risk/reward acceptable, good liquidity"),
                (LogLevel.TRADE, "executor", "EXECUTED: BUY YES on 'Fed Rate Cut March' @ $250"),
                (LogLevel.INFO, "whale_watcher", "Scanning whale wallets for activity..."),
                (LogLevel.WARNING, "whale_watcher", "WHALE DETECTED: CryptoKing BUY $5,000 on 'BTC > $50k'"),
            ]
            
            for level, source, message in reversed(demo_logs):
                level_class = level.value.lower()
                timestamp = datetime.utcnow().strftime("%H:%M:%S")
                st.markdown(f'''
                    <div class="log-entry {level_class}">
                        <span class="log-timestamp">{timestamp}</span> 
                        <span class="log-source">[{source.upper()}]</span> 
                        {message}
                    </div>
                ''', unsafe_allow_html=True)
        else:
            for log in logs:
                level_class = log.level.value.lower()
                timestamp = log.timestamp.strftime("%H:%M:%S")
                st.markdown(f'''
                    <div class="log-entry {level_class}">
                        <span class="log-timestamp">{timestamp}</span> 
                        <span class="log-source">[{log.source.upper()}]</span> 
                        {log.message}
                    </div>
                ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_scope:
    st.markdown('<div class="panel"><div class="panel-title">🎯 Sniper Scope</div>', unsafe_allow_html=True)
    
    watched = state_manager.get_watched_markets()
    
    if not watched:
        # Demo watched markets
        demo_markets = [
            ("Will Trump win 2024?", 0.52, "politics"),
            ("BTC > $50k by March", 0.68, "crypto"),
            ("Fed cuts rates Q1", 0.41, "economics"),
            ("Tesla earnings beat", 0.55, "stocks"),
        ]
        
        for market, price, category in demo_markets:
            price_color = "#00ff88" if price > 0.5 else "#ff3366"
            st.markdown(f'''
                <div class="scope-item">
                    <div>
                        <div class="scope-market">{market[:35]}...</div>
                        <span style="font-size: 0.65rem; color: #888;">{category}</span>
                    </div>
                    <div class="scope-price" style="color: {price_color};">{price:.0%}</div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        for w in watched[:5]:
            price = w.market.yes_price
            price_color = "#00ff88" if price > 0.5 else "#ff3366"
            st.markdown(f'''
                <div class="scope-item">
                    <div>
                        <div class="scope-market">{w.market.question[:35]}...</div>
                        <span style="font-size: 0.65rem; color: #888;">{w.notes or "Monitoring"}</span>
                    </div>
                    <div class="scope-price" style="color: {price_color};">{price:.0%}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# Bottom row: Council + Whale Watcher
col_council, col_whales = st.columns(2)

with col_council:
    st.markdown('<div class="panel"><div class="panel-title">👥 Council of Agents</div>', unsafe_allow_html=True)
    
    agents = council.get_agent_status()
    
    for agent in agents:
        status_dot = "active" if agent["active"] else "inactive"
        st.markdown(f'''
            <div class="agent-card">
                <span class="status-dot {status_dot}"></span>
                <span class="agent-name">{agent["name"]}</span>
                <div class="agent-type">{agent["type"]}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Recent council decisions
    st.markdown('<div style="margin-top: 1rem; font-size: 0.8rem; color: #888;">Recent Decisions:</div>', unsafe_allow_html=True)
    
    # Demo decision
    st.markdown('''
        <div style="background: rgba(0, 255, 136, 0.1); border-left: 3px solid #00ff88; padding: 0.5rem; margin: 0.3rem 0; font-size: 0.75rem;">
            <strong style="color: #00ff88;">✓ APPROVED</strong> - "Fed Rate Cut" (3/3 votes)
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_whales:
    st.markdown('<div class="panel"><div class="panel-title">🐋 Whale Watcher</div>', unsafe_allow_html=True)
    
    whales = whale_watcher.get_whale_leaderboard()[:4]
    
    for whale in whales:
        st.markdown(f'''
            <div class="whale-card">
                <div class="whale-alias">🐋 {whale["alias"]}</div>
                <div class="whale-stats">
                    {whale["address"]} • Win: {whale["win_rate"]} • 
                    <span style="color: #00ff88;">{whale["pnl_30d"]}</span> (30d)
                </div>
                <div class="whale-stats">Specialty: {whale["specialty"]} • Trust: {whale["trust_score"]}</div>
            </div>
        ''', unsafe_allow_html=True)

        # Check for dossier bio
        bio = get_whale_bio(whale_bios, whale["alias"])
        if bio:
            with st.expander("🔍 VIEW CLASSIFIED INTEL", expanded=False):
                st.markdown(bio)
    
    # Recent whale activity
    activities = state_manager.get_whale_activities(limit=2)
    if activities:
        st.markdown('<div style="margin-top: 0.5rem; font-size: 0.75rem; color: #ff00ff;">Recent Activity:</div>', unsafe_allow_html=True)
        for act in activities:
            st.markdown(f'''
                <div style="font-size: 0.7rem; color: #888; margin: 0.2rem 0;">
                    {act.wallet_address[:10]}... → ${act.size:,.0f} on {act.market_question[:20]}...
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Link to dossier
    st.info("💡 **PRO TIP:** Enable 'Show Whale Dossier' in the sidebar for a deep-dive report on these traders.", icon="🐋")


# ============================================
# CONTROL PANEL (Sidebar)
# ============================================

with st.sidebar:
    st.markdown('<div class="panel-title">⚙️ Control Panel</div>', unsafe_allow_html=True)
    
    # System controls
    if st.button("🚀 START SYSTEM", use_container_width=True):
        state_manager.set_running(True)
        state_manager.set_agents_active(3)
        state_manager.add_log("System started", LogLevel.SUCCESS, "system")
        st.rerun()
    
    if st.button("⏹️ STOP SYSTEM", use_container_width=True):
        state_manager.set_running(False)
        state_manager.set_agents_active(0)
        state_manager.add_log("System stopped", LogLevel.WARNING, "system")
        st.rerun()
    
    st.markdown("---")
    
    # Risk settings
    st.markdown("**Risk Parameters**")
    max_trade = st.slider("Max Trade Size ($)", 100, 1000, int(settings.max_single_trade))
    max_daily_loss = st.slider("Max Daily Loss ($)", 100, 2000, int(settings.max_daily_loss))
    
    st.markdown("---")
    
    # Manual market add
    st.markdown("**Add to Sniper Scope**")
    market_input = st.text_input("Market ID or Question")
    if st.button("➕ ADD MARKET"):
        if market_input:
            demo_market = Market(
                id=market_input[:8],
                question=market_input,
                yes_price=0.5,
                no_price=0.5,
                volume_24h=10000,
                liquidity=50000
            )
            state_manager.watch_market(WatchedMarket(market=demo_market))
            st.success("Market added to scope")

    st.markdown("---")
    
    # Alpha Engine Status
    st.markdown("**Core Algorithms**")
    alpha_status = "ONLINE" if alpha_engine._running else "OFFLINE"
    st.info(f"📡 Alpha Engine: {alpha_status}")
    
    # Viral Engine Section
    st.markdown("---")
    st.markdown("**Viral Engine (Press Secretary)**")
    
    if st.button("🚀 GENERATE FLEX ASSETS", use_container_width=True):
        # Generate demo assets
        press_secretary.generate_pnl_card(1250.00, 25.0, "Bitcoin > $100k by Dec 2025")
        asyncio.run(press_secretary.draft_tweets(1250.00, 25.0, "Bitcoin > $100k by Dec 2025"))
        st.success("Assets Generated!")
        st.rerun()

    if os.path.exists(PNL_CARD_PATH):
        st.image(PNL_CARD_PATH, caption="Latest Win Card", use_container_width=True)
        
    if os.path.exists(TWEET_DRAFT_PATH):
        with open(TWEET_DRAFT_PATH, "r", encoding="utf-8") as f:
            drafts = f.read().split("\n---\n")
        
        st.markdown("**Tweet Drafts:**")
        for i, draft in enumerate(drafts):
            st.code(draft, language="markdown")
            if st.button(f"📋 Copy Draft {i+1}", key=f"copy_{i}"):
                # Simple JS alert or just visual feedback since we can't easily clipboard from backend
                st.info("Draft ready for copy (Select & Ctrl+C)")
    
    st.markdown("---")
    
    # Whale Dossier
    st.markdown("**Intelligence**")
    show_dossier = st.checkbox("🐋 Show Whale Dossier", value=False)
    
    if show_dossier:
        st.markdown("---")
        try:
            dossier_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "polymarket_whale.md")
            with open(dossier_path, "r", encoding="utf-8") as f:
                dossier_content = f.read()
            
            # Create a scrolling container for the dossier
            with st.container():
                st.markdown("### 📂 CLASSIFIED REPORT")
                st.markdown(dossier_content)
        except Exception as e:
            st.error(f"⚠️ ERR: Could not load dossier. {str(e)}")


# ============================================
# FOOTER / STATUS
# ============================================

# Display LLM provider status and Repo Info in footer
try:
    from core.llm import llm_manager
    llm_status = f"LLM: {llm_manager.provider_name}"
except ImportError:
    llm_status = "LLM: Not configured"

repo_info = get_repo_info()

st.markdown(f"""
<div style="text-align: center; color: #444; font-size: 0.75rem; margin-top: 3rem; padding: 2rem; border-top: 1px solid #1a1a2e;">
    ⚡ <strong>{repo_info['name'].upper()}</strong> v{settings.app_version} | 
    {llm_status} | 
    <a href="{repo_info['url']}" target="_blank" style="color: #00f5ff; text-decoration: none;">GitHub Source</a> |
    {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
</div>
""", unsafe_allow_html=True)
