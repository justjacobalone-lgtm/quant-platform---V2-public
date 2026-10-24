# Operations

## Emergency stop

Use the authenticated `/kill` endpoint. The execution layer must interpret the halted state as a hard no-new-orders condition and cancel open orders through the exchange adapter.

## Backups

Run `deploy/backup.sh` on a scheduled basis and copy backups to independent storage.

## Monitoring

Prometheus and Grafana are included. Add durable alert routing before production capital is enabled.

## Credentials

Use a secrets manager such as a cloud KMS/Vault integration in production. `.env` is a bootstrap mechanism, not a substitute for a managed secret store.
