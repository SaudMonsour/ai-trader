# Phase 1 MVP Implementation Plan

## Goal Description
Build the MVP of the TradingAgent-Builder, focusing on the core loop: Ingest News -> Analyze -> Generate Signal -> Execute (Paper) -> Log.

## User Review Required
- **News Sources**: We will use free RSS feeds for the MVP to avoid API costs.
- **NLP Model**: We will use lightweight libraries (TextBlob/VADER) for sentiment to keep it fast and local.
- **Paper Trading**: Default starting balance will be $100,000.

## Proposed Changes

### Project Structure
#### [NEW] [structure](file:///c:/Users/saudc/Downloads/استثمر عني/)
- `src/`: Source code
  - `ingestion/`: News and market data fetchers
  - `analysis/`: Sentiment and entity extraction (renamed from nlp)
  - `signals/`: Rule engine and Signal definitions
  - `execution/`: Broker adapters (Paper, Dry Run)
  - `utils/`: Logger, Config, StateManager
  - `main.py`: Entry point
- `config/`: Configuration files
- `logs/`: Log storage
- `data/`: Local data storage (state.json)

### Configuration & State
#### [NEW] [config.yaml](file:///c:/Users/saudc/Downloads/استثمر عني/config/config.yaml)
- Define enabled components, risk limits, news sources, and mode (paper/dry_run).
#### [NEW] [entities.yaml](file:///c:/Users/saudc/Downloads/استثمر عني/config/entities.yaml)
- Static mapping of Company Name -> Ticker (e.g., Apple: AAPL).
#### [NEW] [state.json](file:///c:/Users/saudc/Downloads/استثمر عني/data/state.json)
- Tracks processed news IDs, current portfolio snapshot, cash balance, and last run timestamp.

### Ingestion
#### [NEW] [news_fetcher.py](file:///c:/Users/saudc/Downloads/استثمر عني/src/ingestion/news_fetcher.py)
- Fetch from defined RSS feeds.
- Deduplicate based on URL/Title and check against processed IDs in state.

### Analysis (NLP)
#### [NEW] [processor.py](file:///c:/Users/saudc/Downloads/استثمر عني/src/analysis/processor.py)
- `analyze_sentiment(text)`: Returns score -1 to 1.
- `extract_entities(text)`: Uses `entities.yaml` for keyword matching.

### Signal Engine
#### [NEW] [engine.py](file:///c:/Users/saudc/Downloads/استثمر عني/src/signals/engine.py)
- **Signal Object**:
  ```python
  Signal(asset="AAPL", action="BUY", confidence=0.74, reason=["..."], source_news_id="...")
  ```
- **Rule Evaluator**:
  - Rules have weights (0-1).
  - Sum of weights = Final Confidence.

### Execution
#### [NEW] [broker.py](file:///c:/Users/saudc/Downloads/استثمر عني/src/execution/broker.py)
- **Modes**:
  - `paper`: Simulate orders, update local portfolio/balance.
  - `dry_run`: Log signals only, do not touch portfolio.
- **Logging**:
  - Structured JSON logs for every action.
  ```json
  {"timestamp": "...", "signal": "BUY", "executed": true, "mode": "paper", ...}
  ```

## Verification Plan
### Automated Tests
- Unit tests for Entity Extraction using the static map.
- Unit tests for Rule Engine weights and Signal generation.
- Integration test: Run in `dry_run` mode and verify logs without state change.

### Manual Verification
- Run the agent in `paper` mode.
- Verify `data/state.json` updates correctly after a run.
- Check `logs/trading.log` for structured JSON output.
