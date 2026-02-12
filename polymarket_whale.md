# Polymarket's top whales and how to track them

**One trader dominates all others: the anonymous French national known as "Théo" has extracted roughly $85 million from Polymarket across 11 linked accounts, making him the most profitable prediction market trader in history.** Behind him, a concentrated elite of fewer than 700 wallets captures over 70% of the platform's total realized profits, while 92.4% of all Polymarket wallets remain unprofitable. This report identifies the top whale traders by profit, profiles rising stars, and maps the complete technical infrastructure for building a real-time whale-watching copy-trading system.

Polymarket processed **$21.5 billion in trading volume** in 2025 across 95 million on-chain transactions, with 1.7 million total trading addresses. Yet only **0.51% of wallets** have ever earned more than $1,000 in profit. The platform operates on Polygon with USDC collateral, settling trades via a hybrid-decentralized CLOB (Central Limit Order Book) — off-chain matching, on-chain settlement through signed EIP-712 orders. This architecture makes every trade publicly auditable and every whale wallet trackable.

---

## The all-time profit leaderboard reveals extreme concentration

The top 10 most profitable Polymarket accounts by all-time PnL, with wallet information and trading profiles:

| Rank | Username | All-Time PnL | Volume | Specialty | Notes |
|------|----------|-------------|--------|-----------|-------|
| 1 | **Theo4** | +$22,053,934 | $43.3M | Politics | Théo's primary account |
| 2 | **Fredi9999** | +$16,619,507 | $76.6M | Politics | Théo's second account |
| 3 | **kch123** | +$10,865,852 | $230.3M | Sports | Super Bowl / Champions League whale |
| 4 | **Len9311238** | +$8,709,973 | $16.4M | Politics | High ROI, low volume |
| 5 | **zxgngl** | +$7,807,266 | $40.7M | Politics | Spent $7.2M on Trump "Yes" in one session |
| 6 | **RepTrump** | +$7,532,410 | $14.0M | Politics | Another Théo account |
| 7 | **DrPufferfish** | +$6,564,386 | $129.3M | Sports / Diversified | ~51.8% win rate, market-maker style |
| 8 | **PrincessCaro** | +$6,083,643 | $23.5M | Politics | Another Théo account |
| 9 | **walletmobile** | +$5,942,685 | $32.2M | Politics | Bet solely on Trump, profited $6.1M |
| 10 | **BetTom42** | +$5,642,136 | $11.2M | Politics | ~50%+ return on volume |

Below them, **0x006cc834...c16ea** (+$5.16M), **mikatrade77** (+$5.15M), **alexmulti** (+$4.80M), **RN1** (+$4.37M, $201M volume), and **GCottrell93** (+$4.18M) round out the top 15. The volume leaderboard tells a different story: **ImJustKen** (Domer) leads with **$453M traded** but "only" +$2.93M in profit, followed by **cigarettes** ($452.8M volume, +$858K), **gmanas** ($441.2M, +$3.5M), and **swisstony** ($362.9M, +$3.95M) — all running high-frequency or market-making strategies.

**Critical caveat**: At least 4–6 of the top 10 profit accounts belong to Théo. Blockchain analysis by Chainalysis confirmed 11 linked wallets funded via Kraken, bringing his combined haul to approximately **$78.7–85 million**. Without cluster detection, the leaderboard dramatically overstates the number of distinct profitable entities.

---

## Detailed profiles of the most consequential whales

### Théo — "The French Whale" (~$85M profit)

The most profitable prediction market trader ever. A wealthy French national with a banking/finance background who commissioned **private YouGov polls** using "neighbor polling" methodology to detect the shy-Trump-voter effect. He deployed $30M of his own capital (scaling to $80M total) across 11 accounts — Theo4, Fredi9999, PrincessCaro, Michie, RepTrump, zxgngl, and five others — buying Trump "Yes" shares in small increments ($5 to tens of thousands) to avoid moving the market. His bets spanned Trump winning the Electoral College, popular vote, and individual swing states (PA, MI, WI). Self-described as "apolitical" and purely profit-motivated. Profiled by the Wall Street Journal, Bloomberg, CBS 60 Minutes, and The Free Press. France's gambling authority (ANJ) investigated; Polymarket subsequently blocked French users.

### Domer / ImJustKen — The volume king ($2.9M profit, $453M volume)

- **Wallet**: `0x9d84ce0306f8551e02efef1680475fc0f1dc1344`
- **Twitter/X**: @Domahhhh

A former professional online poker player turned full-time prediction market trader since 2008 (Intrade era). Lives outside the US. Trades **entirely manually** — no bots — across 5,000+ markets. His philosophy: "Prediction markets are basically slow motion poker hands where you can out-research your opponents." Admits losing slightly more bets than he wins, but winning more money per win. Featured on CBS 60 Minutes (February 2026) and the On Chain Times. Applies Kahneman & Tversky behavioral frameworks to exploit anchoring, endowment, and loss-aversion biases in other traders.

### kch123 — Sports market dominator ($10.9M profit)

The highest-profit single identity outside the Théo cluster. Career profit exceeds **$11.1 million** with 1,800+ trades. Netted **$1.8 million** going 5-for-5 on Super Bowl LX bets (Seahawks 29-13 over Patriots, February 8, 2026), including $986K from the -4.5 spread alone. His biggest single payday: **$1.095 million** on a Champions League match in January 2026. Consistently appears on both all-time and monthly leaderboards, representing the "professional class" of prediction market participants.

### George Cottrell / GCottrell93 ($4.2M profit, publicly identified)

Real identity confirmed by blockchain investigator ZachXBT: **George Cottrell**, ~30, aide to Nigel Farage, privately educated, aristocratic family (uncle Lord Hesketh), previously convicted of wire fraud in the US. Bought **$9M in Trump shares** and won **$13M** — one of the largest individual election winners. Account was dormant for 12 months before resurfacing with an $80K bet on the Trump-Xi handshake duration (which he lost).

### GCR — Crypto whale and market mover

Well-known crypto advisory figure who took an early, multi-year Trump position on Polymarket when implied odds were under 10%. His October 2024 tweet about taking profits triggered a cascade: whale account "larpas" dumped $3M in Trump shares within minutes, briefly crashing odds by ~4%. Identified by Arkham Intelligence. Emphasizes probabilistic thinking and opposes leverage.

---

## Rising whales who emerged in the last 3–6 months

The February 2026 monthly leaderboard reveals several traders gaining prominence rapidly:

| Trader | Feb 2026 PnL | Volume | Profile |
|--------|-------------|--------|---------|
| **0x4924...c8A3782** | +$3,152,033 | $27.2M | Anonymous; #1 monthly. Previously had -$8.2M all-time losses, now recovering aggressively |
| **beachboy4** | +$2,099,685 | $7.3M | Booked **$6.12M in a single day** (Jan 18, 2026) — sports specialist (football/soccer, NBA spreads) |
| **FeatherLeather** | +$1,756,572 | $3.5M | Extremely high capital efficiency (~50% return on volume); emerging political/macro trader |
| **gmpm** | +$1,224,903 | $8.5M | Diversified high-volume approach |
| **weflyhigh** | +$1,182,299 | $8.0M | Consistent monthly performer |
| **anoin123** | +$1,025,867 | $9.7M | High-volume systematic approach |
| **MrSparklySimpsons** | +$840,380 | $5.4M | Rising sports and diversified trader |
| **BWArmageddon** | +$667,568 | $9.4M | High-volume emerging whale |
| **C.SIN** | +$453,553 | $2.6M | Efficient capital deployment |

Two controversial "rising" traders deserve special mention. **"Burdensome-Mix"** created an account on December 27, 2025, deployed ~$32K on Venezuela invasion and Maduro removal markets when odds sat at 5–8%, then placed $20K+ just **5 hours before** Operation Absolute Resolve commenced on January 2, 2026. Payout: **$436,759** — a 1,200%+ return that triggered federal scrutiny and proposed legislation (the "Public Integrity in Financial Prediction Markets Act of 2026"). **"AlphaRaccoon" (0xafEe)** deposited $3M in December 2025 and correctly predicted 22 of 23 Google Year in Search categories, including d4vd as most-searched person at 0.2% odds, netting ~$1 million in 24 hours. A Meta engineer publicly accused the account of being a Google insider.

---

## Category specialists reveal where the edge lives

The community consensus is clear: **domain specialization beats diversification**. Stand.trade's analysis found that traders with "overwhelming information advantage in a single field" consistently outperform generalists. Several traders have six-figure or seven-figure PnL in one category but negative returns in others.

**Political specialists** include Erasmus (+$1.3M, wallet `0xc6587b11a2209e46dfe3928b31c5514a8e33b784`), WindWalk3 (+$1.1M from a single RFK health policy bet), and RememberAmalek (+$300K on NYC mayoral when Mamdani was at 8% odds — he waits for market overreactions and deep-analyzes polling crosstabs). **Sports specialists** include kch123 (above), S-Works (~$1M, NBA/baseball), 1j59y6nk (~$1.4M, baseball/football), abeautifulmind (NBA), and Joe-Biden (username, $566K Super Bowl 2025 win). **Crypto traders** like HaileyWelsh consistently appear in the "biggest wins" feed, while 0x8dxd runs an automated bot predicting crypto prices in 15-minute increments ($658K total). **Mention-market specialists** like Axios (96% win rate) and GreekGamblerPM dominate speech/broadcast prediction markets. **Weather traders** include gopfan2 and neobrother, with one automated weather bot scaling $1K to $24K since April 2025 by comparing NOAA data to market prices.

Five strategy archetypes dominate the platform: **The Quant Fund** (2,000+ trades, 58% win rate, many small positions), **The Political Insider** (87 trades, 71% win rate, large concentrated bets), **The Crypto Whale** (156 trades, 64% win rate, early positions on Bitcoin milestones), **The Sports Pro** (421 trades, 61% win rate, focused NFL/NBA), and **The Contrarian** (43 trades, 67% win rate, massive size on unpopular positions).

---

## Known wallet addresses for copy-trading integration

| Username | Wallet Address | All-Time PnL | Primary Category |
|----------|---------------|-------------|------------------|
| ImJustKen (Domer) | `0x9d84ce0306f8551e02efef1680475fc0f1dc1344` | +$2.93M | Diversified |
| Erasmus | `0xc6587b11a2209e46dfe3928b31c5514a8e33b784` | +$1.3M | Politics |
| Tsybka | `0xd5ccdf772f795547e299de57f47966e24de8dea4` | +$191K | Systematic/Low-vol |
| Anonymous sports whale | `0x492442EaB586F242B53bDa933fD5dE859c8A3782` | +$3.15M (monthly) | Sports |
| Anonymous trader | `0x876426B52898C295848f56760dd24B55Eda2604a` | +$949K (monthly) | Unknown |
| Anonymous trader | `0x1D8A377C5020f612cE63a0a151970DF64BAAE842` | +$879K (monthly) | Unknown |
| Anonymous high-profit | `0x006cc834Cc092684F1B56626E23BEdB3835c16ea` | +$5.16M | Unknown |
| High-volume whale | `0xd218e474776403a330142299f7796e8ba32eb5c9` | +$958K (30d) | 65–67% win rate |
| High-volume trader | `0xee613b3fc183ee44f9da9c05f53e2da107e3debf` | +$1.34M | 52% win rate |

**Note**: Most Polymarket traders use proxy wallets on Polygon. Additional wallet addresses for any username can be retrieved programmatically via the Polymarket Data API endpoint `GET /leaderboard`, which returns `proxyWallet`, `userName`, `vol`, and `pnl` for each trader. Profile pages at `polymarket.com/@{username}` also expose wallet data.

---

## The complete technical stack for whale tracking and copy trading

### Polymarket's official APIs (all free)

The platform exposes five API services. The **CLOB API** (`https://clob.polymarket.com`) handles prices, orderbooks, and order placement with three authentication tiers: public (L0, no auth), wallet signature (L1, EIP-712), and HMAC (L2, API key + secret). Rate limits sit at ~100 requests/minute for public endpoints and ~60 orders/minute for trading. The **Gamma API** (`https://gamma-api.polymarket.com`) provides market discovery and metadata with no authentication required. The **Data API** (`https://data-api.polymarket.com`) serves user positions, trade history, and the official leaderboard — this is the **critical endpoint for copy-trading**, as polling a target wallet's positions every 1–4 seconds enables trade detection. The **WebSocket** (`wss://ws-subscriptions-clob.polymarket.com/ws/`) delivers real-time orderbook updates, and **RTDS** (`wss://ws-live-data.polymarket.com`) provides low-latency crypto price feeds.

Official SDKs include **py-clob-client** (Python, `pip install py-clob-client`), TypeScript (`@polymarket/clob-client`), Rust, and Go clients. A unified Python wrapper (`polymarket-apis` on PyPI) covers all five API surfaces with Pydantic validation.

### Key smart contract addresses (Polygon mainnet)

| Contract | Address |
|----------|---------|
| CTF Exchange (binary markets) | `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e` |
| NegRisk CTF Exchange (multi-outcome) | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |
| Conditional Tokens (ERC-1155) | `0x4d97dcd97ec945f40cf65f87097ace5ea0476045` |
| USDC (Polygon) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` |
| Proxy Wallet Factory | `0x56C79347e95530c01A2FC76E732f9566dA16E113` |

Monitor `OrderFilled` and `OrdersMatched` events on the CTF Exchange contracts for real-time on-chain trade detection.

### Third-party whale tracking tools

The most actionable platforms for a copy-trading system:

- **Polymarket Analytics** (polymarketanalytics.com) — The gold standard. Trader leaderboards filterable by category, wallet-level PnL/win-rate/positions, updated every 5 minutes via Goldsky indexing. Free. Cited by WSJ and CoinDesk.
- **PolyTrack** (polytrackhq.app) — Real-time whale alerts, cluster detection linking multi-wallet entities, Telegram notifications. Free tier tracks 3 wallets; Pro ($19/month) unlimited.
- **Polywhaler** (polywhaler.com) — Monitors $10K+ trades, insider activity detection, AI predictions on Pro tier.
- **Unusual Whales / Unusual Predictions** (unusualwhales.com/predictions) — Launched January 2026; extends their equity anomaly-detection engine to prediction markets with "Smart Money" filtering.
- **HashDive** — "Smart Score" (-100 to 100) per trader, market screener by whale activity and momentum.
- **Arkham Intelligence** (intel.arkm.com/explorer/entity/polymarket) — Wallet identity deanonymization, entity grouping, dedicated Polymarket page.
- **Dune Analytics** — Key dashboards at `dune.com/genejp999/polymarket-leaderboard` and `dune.com/filarm/polymarket-activity`. Custom SQL queries against raw Polygon data.
- **The Graph / Goldsky Subgraphs** — GraphQL access to on-chain data. PnL subgraph: `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn`. 100K free queries/month.

### Open-source copy-trading bots on GitHub

Several production-ready repositories exist: **Trust412/polymarket-copy-trading-bot-version-3** (TypeScript, monitors wallets every 4 seconds, Safe wallet integration, MongoDB, Docker), **Novus-Tech-LLC/Polymarket-Copytrading-Bot** (enterprise-grade, 1-second polling, multi-trader support, adaptive sizing), and **iengineer/polymarket--whale-trading-bot** (whale-specific with adaptive trailing stops at 15% profit trigger). All use `py-clob-client` or `@polymarket/clob-client` under the hood.

### Telegram alert bots for real-time signals

**PolyAlertHub** (@PolyAlertHubBot), **Polylerts** (tracks 15 wallets, confidence scoring 1–10), **PolyIntel** (whale detection every 10 minutes), **PolyCopy** (real-time with no wallet connection required), and **PolyWatch** by ForgeLabs ($1K+ trade alerts, $25K+ whale feed) all provide push notifications suitable as signal inputs for automated systems.

---

## Conclusion: building a trust-scored whale-watching system

The data supports a clear implementation path. **Start with the Polymarket Data API** to poll the ~50 most profitable wallets every 1–4 seconds, using the leaderboard endpoint to programmatically refresh the target list. Layer in **PolyTrack's cluster detection** to map multi-wallet entities and avoid over-indexing on Théo-like clusters. Assign **trust scores** based on a weighted composite of all-time PnL (30%), win rate (20%), capital efficiency / ROI on volume (20%), consistency across months (15%), and category specialization depth (15%). The highest-signal traders for copy trading are not the biggest winners but the most consistent: kch123, DrPufferfish, Domer, and category specialists like Erasmus (politics) and S-Works (sports) offer more replicable edge than one-time insider-style bets.

The key challenge is the **cat-and-mouse dynamic**: top traders now use secondary and tertiary accounts because they know their primary wallets are being copy-traded within seconds. Stand.trade's analysis found that unrecognized wallet addresses often make major buys on whale feeds before well-known traders do — suggesting smart money is migrating to fresh wallets. Any production system must incorporate new-wallet detection (flag fresh wallets making $5K+ first bets), cross-reference with cluster detection tools, and continuously re-evaluate which wallets represent genuine alpha versus noise.