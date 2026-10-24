# Production Gates

A deployment is not considered live-ready merely because containers start.

Required gates:

1. Static checks and unit tests
2. Integration tests
3. Exchange adapter contract tests
4. Market-data reconnect tests
5. Order idempotency tests
6. Position reconciliation tests
7. Risk-limit tests
8. Kill-switch tests
9. Audit persistence tests
10. Backup/restore test
11. Shadow performance validation
12. Operator approval
13. Limited live-candidate stage
14. Controlled live enablement

The repository intentionally keeps exchange adapters non-trading until those gates are completed.
