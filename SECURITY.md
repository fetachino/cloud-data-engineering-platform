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

## Verified AWS Posture

## AWS Hardening

- RDS is private, encrypted at rest, single-AZ, and reachable only from the ECS
  API security group on port 5432.
- S3 public access is blocked; CloudFront uses origin access control for reads.
- ECR repositories scan on push and retain only the five newest images.
- API and consumer containers run as non-root `appuser`.
- Database credentials are generated and referenced through Secrets Manager.
- GitHub Actions uses short-lived OIDC credentials with an immutable
  repository-ID and protected `portfolio` environment trust condition instead
  of long-lived AWS keys.
- Workflow token permissions are read-only except for the deployment OIDC token.
- CloudWatch log retention is limited to 14 days for the portfolio environment.

The public ALB uses HTTP because no domain or certificate is
provisioned. The analytics API is intentionally public and read-only; it must
not serve sensitive data. Terraform state can contain generated credential
metadata and must remain outside Git. See [docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md).

## Residual Risks

- The public ALB has no TLS certificate or custom domain.
- The portfolio RDS instance is single-AZ and Terraform state remains local;
  remote encrypted state is a production follow-up.
- Local Compose defaults are for development and expose PostgreSQL and Kafka
  on localhost. Do not bind them publicly or reuse the placeholder passwords.
