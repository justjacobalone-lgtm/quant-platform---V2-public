# Quant Platform OS 1.3.3 Hardened Deployment Checkpoint

Baseline restored from v1.2 execution/research package and upgraded with the hardened control-plane layer.

## Safety defaults
- PAPER mode by default
- system HALTED by default
- LIVE trading disabled by default
- LIVE requires explicit configuration enablement, admin approval, and non-halted state
- kill revokes LIVE approval and halts the system
- Android is a control terminal only; exchange secrets stay server-side

## Required before production
1. Configure `.env` with unique secrets.
2. Run `./deploy/preflight-hardened.sh` on a host with Docker.
3. Start the stack and verify health/status.
4. Run the complete test suite.
5. Validate exchange testnet/sandbox connectivity.
6. Validate reconciliation, idempotency, risk limits, audit logging, and rollback.
7. Only then consider enabling LIVE.

No live deployment is represented by this repository artifact itself.
