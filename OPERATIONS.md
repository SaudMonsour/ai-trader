# Operations Manual

## 1. Starting the Agent
```bash
python -m src.main
```
Logs will stream to console and `logs/trading.log`.

## 2. Monitoring
- **Logs**: `tail -f logs/trading.log` (JSON structured)
- **State**: Inspect `data/state.json` to see current portfolio and processed news.
- **Order Status**: Check `order_history` in `state.json` for `FILLED` or `FAILED` statuses.

## 3. Maintenance
- **Log Rotation**: Logs can grow large. Archive or delete `logs/trading.log` periodically.
- **State Reset**: To reset the bot completely, delete `data/state.json`. **WARNING**: This deletes your paper trading portfolio history.

## 4. Emergency Procedures
### Stop the Bot
1. Press `Ctrl+C` (Graceful shutdown).
2. Or Find process ID: `ps aux | grep main.py` or check logs for `"pid": ...`. Kill it.

### Emergency Stop Switch
To prevent the bot from placing ANY new trades while keeping the process running (e.g. for draining), set `"emergency_stop": true` in `data/state.json`.
The bot will continue to process news but will log "EMERGENCY STOP ENABLED. Skipping execution." for every trade.

## 5. Troubleshooting
- **Bot crashes**: Check `logs/trading.log` for stack traces.
- **No trades**:
    - Check `dry_run` in config.
    - Check `risk` limits (low cash?).
    - Check network (RSS feeds reachable?).
- **Insufficient Cash**: Risk Manager now includes a 1% buffer for fees. Ensure `cash >= cost * 1.01`.
- **Corrupted State**: If `state.json` is corrupted, the bot attempts to recover (or fail safely). Backup `state.json` regularly.
