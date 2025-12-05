# Development Guidelines

## Code Style
- Follow existing patterns in the codebase
- Use type hints consistently
- Keep functions focused and single-purpose

## Architecture Patterns
- **Interface-based design** - Clear separation between business logic and implementation
- **Dependency injection** - Adapters injected into strategies and engines
- **Event-driven** - WebSocket events trigger strategy decisions
- **Async/await** - Non-blocking I/O for real-time operations

## Error Handling
- Use custom exceptions from `src/utils/exceptions.py`
- Graceful degradation for network issues
- Comprehensive logging at appropriate levels
- Clean shutdown on signals (SIGINT, SIGTERM)

## Testing Requirements
- Validate against Hyperliquid testnet
- Test all learning examples ensure they work with real API responses
- Configuration validation verify all parameters work
- Integration testing end-to-end trading workflows

## Environment Setup
**Required Environment Variables:**
```bash
# .env file
HYPERLIQUID_TESTNET_PRIVATE_KEY=0x...  # For testnet trading
HYPERLIQUID_TESTNET=true               # Enable testnet mode
```

**Development Workflow:**
1. Set up environment variables
2. Test with learning examples first
3. Configure bot with small allocation percentages
4. Validate configuration with `--validate` flag
5. Test on testnet before any mainnet deployment

## Private Key Security
- Never commit private keys to git
- Use `.env` file for local development
- Consider environment variables for CI/CD

## Running Tests
```bash
# Basic test run
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=src

# Specific test file
python3 -m pytest tests/test_enhanced_config.py -v
```

