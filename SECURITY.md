# Security

This repository is a portfolio project with local development defaults.

## Secrets

- Do not commit `.env`.
- `.env.example` contains development-only placeholders.
- Use environment variables for runtime configuration.

## Data

Synthetic events use fictional data only. Email addresses use the reserved `example.test` domain and no real customer data is included.

## Local Services

Docker Compose exposes PostgreSQL and Kafka ports for local development. These settings are not hardened for production or public network exposure.

## Future Hardening

Cloud security hardening belongs to Milestone 5 and is intentionally not implemented in Milestone 1.
