# TradingAgent-Builder Task List

## Phase 1: MVP (News Ingestion, NLP, Basic Rules, Paper Trading)
- [x] Project Scaffolding <!-- id: 0 -->
    - [x] Create directory structure (src, config, logs, data)
    - [x] Initialize Python project (requirements.txt, venv)
    - [x] Create Dockerfile and docker-compose.yml
- [x] Configuration & Logging <!-- id: 1 -->
    - [x] Implement configuration loader (config.yaml)
    - [x] Setup structured logging (JSON schema)
    - [x] Define static entity mapping (entities.yaml)
- [x] State Management <!-- id: 8 -->
    - [x] Implement StateManager (load/save state.json)
    - [x] Track processed news IDs and portfolio state
- [x] Ingestion Service <!-- id: 2 -->
    - [x] Implement NewsFetcher (RSS/API)
    - [x] Implement MarketDataFetcher (Mock/API)
- [x] Analysis Engine (formerly NLP) <!-- id: 3 -->
    - [x] Implement text normalization
    - [x] Implement basic sentiment analysis (TextBlob/VADER)
    - [x] Implement entity extraction (Keyword matching via entities.yaml)
- [x] Signal Engine <!-- id: 4 -->
    - [x] Define Signal object (distinct from execution)
    - [x] Implement RuleEvaluator with confidence weights
    - [x] Define basic rules in config
- [x] Execution Engine <!-- id: 5 -->
    - [x] Implement PaperBroker adapter
    - [x] Implement DryRun mode
    - [x] Implement OrderManager
    - [x] Implement PortfolioTracker
- [x] Main Loop & Orchestration <!-- id: 6 -->
    - [x] Integrate all components into a main loop
    - [x] Ensure graceful shutdown
- [x] Verification & Documentation <!-- id: 7 -->
    - [x] Run end-to-end simulation
    - [x] Verify logs and decisions
    - [x] Create README.md

## Phase 2: Risk Engine & Backtesting
- [ ] Risk Management
- [ ] Backtesting Engine
- [ ] Dashboard

## Phase 3: Live Trading & Hardening
- [ ] Live Broker Adapter
- [ ] Security Hardening
