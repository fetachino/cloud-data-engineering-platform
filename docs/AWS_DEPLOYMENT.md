# AWS Deployment

Milestone 5 defines an intentionally small AWS portfolio environment. The
Terraform configuration was applied and the public frontend and API endpoints
were verified in the authenticated `us-east-1` portfolio account. No
credentials or secret values are stored in this repository.

## Architecture

```text
CloudFront + private S3 frontend
             |
             v
      public ALB -> one ECS Fargate API task -> private RDS PostgreSQL
                         |
                         +--> CloudWatch logs

ECR stores the immutable API image; the frontend is static S3 content rather
than a permanently running container.
GitHub Actions assumes an AWS IAM role through GitHub OIDC.
```

The VPC has two public subnets for the ALB and Fargate task, and two private
database subnets for RDS. There is deliberately no NAT Gateway. Fargate tasks
use public IPs to pull ECR images and write logs; the database has no public
address and accepts port 5432 only from the API security group.

Kafka remains a local/demo component in this milestone. Airflow and dbt remain
local orchestration by default; a controlled ECS dbt task can be added later
without paying for always-on MSK or MWAA. This preserves the existing event
architecture without introducing large fixed costs.

## Prerequisites

- AWS account and a single configured region
- AWS CLI credentials with permission to bootstrap the Terraform resources
- Terraform 1.9.8 or newer
- Docker for building the API image
- Node.js 22 for the frontend

For a new account, verify `aws sts get-caller-identity` and the target region
before planning. Do not infer deployment success from Terraform validation
alone.

## Terraform

```powershell
Set-Location infra/terraform
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file=terraform.tfvars
```

Review the plan before applying. The first apply needs a bootstrap identity that
can create the OIDC provider, IAM roles, VPC, ECR, ECS, RDS, S3, and CloudFront
resources. After the OIDC role exists, normal deployments should use the GitHub
Actions role rather than long-lived access keys.

The default state backend is local for this single portfolio environment. State
contains infrastructure metadata and generated database credentials, so keep it
outside Git and protect it with filesystem access controls. A safe next step is
to migrate the state to a private, encrypted S3 bucket with versioning and an
appropriate lock mechanism after the account bootstrap is reviewed. The
repository does not create a bootstrap bucket automatically.

## Deployment sequence

1. Review `terraform plan` and apply the selected portfolio environment.
2. Build and push an immutable API image to the generated ECR repository.
3. Set the GitHub repository variables listed in [CI_CD.md](CI_CD.md).
4. Run the `Deploy portfolio environment` workflow manually, or merge a change
   to `main` that matches its deployment paths.
5. Apply Alembic migrations through a reviewed ECS task or controlled operator
   session. The deployment workflow does not run destructive migrations.
6. Run the local producer and dbt/Airflow workflow while Kafka remains local,
   or execute an explicitly reviewed cloud transformation job.
7. Verify the ALB `/health` endpoint, CloudFront frontend URL, RDS privacy, and
   CloudWatch log stream.

The API is a public read-only analytics surface in this portfolio design. It
does not add authentication merely for appearance; do not put sensitive data
behind it.

## Cost and teardown

No precise price is asserted because pricing depends on region, usage, data
transfer, CloudFront requests, storage, and free-tier eligibility. The main
cost drivers are the ALB, one continuously running Fargate task, RDS storage and
instance hours, and CloudFront/S3 traffic. The design avoids NAT Gateway, MSK,
MWAA, multi-AZ RDS, and custom domains to reduce fixed cost.

For a deliberate teardown after review:

```powershell
Set-Location infra/terraform
terraform plan -destroy -var-file=terraform.tfvars
terraform destroy -var-file=terraform.tfvars
```

Confirm the target account and region before destroying. The configuration uses
`skip_final_snapshot = true` and `deletion_protection = false` for a disposable
portfolio environment; use different settings for retained data.

## Limitations

- The deployment is intentionally sized for portfolio evidence rather than
  high availability or production scale.
- The API uses an internet-facing ALB without HTTPS because no domain or paid
  certificate may be purchased for this milestone.
- Kafka, Airflow, and dbt are not permanently hosted in AWS.
- Terraform state bootstrap and migration to remote state remain operator work.
