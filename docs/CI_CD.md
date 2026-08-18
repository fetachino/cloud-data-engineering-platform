# CI/CD

## CI workflow

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`. It runs:

- Python tests, Ruff, and mypy
- frontend tests, ESLint, and production build
- Terraform format/initialization/validation
- Docker Compose configuration checks
- Alembic SQL generation

It does not start a full Kafka/PostgreSQL integration environment for every
pull request. Runtime smoke testing remains a deliberate local or environment
verification step.

## Deployment workflow

`.github/workflows/deploy.yml` runs manually or after matching changes merge to
`main`. It:

1. assumes the Terraform-created IAM role with GitHub OIDC;
2. builds and pushes the API image with the commit SHA as an immutable tag;
3. registers a new ECS task definition and waits for the service rollout;
4. builds the React frontend with the configured API URL;
5. syncs frontend assets to private S3 and invalidates CloudFront.

The workflow never receives long-lived AWS access keys. It requires a protected
`portfolio` GitHub environment and these repository variables:

| Variable | Purpose |
| --- | --- |
| `AWS_REGION` | Single deployment region |
| `AWS_DEPLOY_ROLE_ARN` | Terraform-created OIDC role ARN |
| `ECR_API_REPOSITORY` | API ECR repository name |
| `ECR_FRONTEND_BUCKET` | Private frontend bucket name |
| `ECS_CLUSTER` | ECS cluster name |
| `ECS_SERVICE` | API ECS service name |
| `ECS_TASK_FAMILY` | API task definition family |
| `CLOUDFRONT_DISTRIBUTION_ID` | Frontend distribution ID |
| `API_BASE_URL` | Public API URL used by the frontend |

The workflow does not apply Terraform automatically. Infrastructure changes
must be reviewed and applied through an intentional operator action before a
deployment workflow is enabled.

## Permissions and trust

The workflows use `contents: read`; only deployment receives `id-token: write`.
The Terraform trust policy restricts OIDC subjects to the repository's immutable
ID and protected `portfolio` environment. The deployment role is scoped to the
project ECR repositories, ECS deployment operations, the frontend bucket, and
its CloudFront invalidation.

## Failure handling

ECS waits for a stable service after registering the task definition. A failed
rollout leaves the previous task definition available for operator rollback.
The workflow does not destroy infrastructure, rotate secrets, or run destructive
database migrations automatically.
