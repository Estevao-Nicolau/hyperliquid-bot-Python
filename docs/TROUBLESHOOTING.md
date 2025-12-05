# Troubleshooting Guide

## Common Issues

### "No module named pytest"
```bash
python3 -m pip install pytest pytest-asyncio pytest-mock
```

### Tests not found
```bash
python3 -m pytest tests/ --collect-only
```

### Import errors
```bash
python3 -m pip install -r requirements.txt
```

### Module import issues in src/
Add to Python path:
```bash
export PYTHONPATH=src:$PYTHONPATH
```

### Precision issues with BTC orders
- BTC requires whole dollars for prices
- Size should be 5 decimal places (0.0001 minimum)
- Check `src/exchanges/hyperliquid/adapter.py` for tick size handling

### WebSocket connection issues
- Verify network connectivity
- Check Hyperliquid API status
- Ensure private key is valid
- Try testnet first

### Paper trading not working
- Set `PAPER_TRADING=true` in `.env`
- Verify `PAPER_INITIAL_BALANCE` is set
- Check logs for initialization errors

## Performance Tips

1. **Reduce grid levels** - Fewer levels = faster execution
2. **Increase polling intervals** - Reduces API calls
3. **Use paper trading first** - Test strategy before live
4. **Monitor memory** - Check for memory leaks in long runs

