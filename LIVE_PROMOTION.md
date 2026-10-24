# Live Promotion Procedure

Live trading is intentionally a separate operational event.

1. Run paper validation.
2. Run shadow validation against live market data without placing orders.
3. Verify risk limits and position reconciliation.
4. Verify exchange connectivity and clock synchronization.
5. Verify audit logging and backups.
6. Verify kill switch.
7. Require explicit operator approval.
8. Promote to `LIVE_CANDIDATE`.
9. Perform final readiness checks.
10. Promote to `LIVE` only after the second authorization.

Never place exchange secrets in the Android application. The Android app should call the authenticated control plane over TLS.

The deployment pack does not certify a strategy as profitable, safe for a particular investor, or compliant with any jurisdiction's investment-management rules.
