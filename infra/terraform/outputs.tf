output "api_base_url" {
  description = "Public HTTP endpoint for the analytics API load balancer."
  value       = "http://${aws_lb.api.dns_name}"
}

output "frontend_url" {
  description = "CloudFront URL for the React dashboard."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "api_ecr_repository_url" {
  description = "ECR repository URL for the API image."
  value       = aws_ecr_repository.api.repository_url
}

output "frontend_bucket_name" {
  description = "Private S3 bucket used as the CloudFront frontend origin."
  value       = aws_s3_bucket.frontend.bucket
}

output "github_deploy_role_arn" {
  description = "OIDC role ARN for the GitHub Actions deployment workflow."
  value       = aws_iam_role.github_deploy.arn
}

output "database_secret_arn" {
  description = "Secrets Manager ARN containing the generated application database URL."
  value       = aws_secretsmanager_secret.database.arn
  sensitive   = true
}
