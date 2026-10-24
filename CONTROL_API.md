# Android Control API

The Android terminal should expose:
- system health
- current mode
- risk status
- strategy/shadow status
- PnL and positions
- audit events
- emergency kill switch
- controlled promotion workflow

All mutating requests require authentication. LIVE promotion additionally requires an explicit approval token and confirmation screen. Exchange credentials never belong in the APK.
