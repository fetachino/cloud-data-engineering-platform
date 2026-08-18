from pathlib import Path

ROOT = Path(__file__).parents[1]
TERRAFORM = ROOT / "infra" / "terraform"


def test_terraform_defines_cost_conscious_private_database_and_compute() -> None:
    configuration = (TERRAFORM / "main.tf").read_text()

    for resource in (
        'resource "aws_vpc" "this"',
        'resource "aws_ecs_service" "api"',
        'resource "aws_db_instance" "this"',
        'resource "aws_ecr_repository" "api"',
        'resource "aws_cloudfront_distribution" "frontend"',
        'resource "aws_cloudwatch_log_group" "api"',
    ):
        assert resource in configuration
    assert "publicly_accessible     = false" in configuration
    assert "multi_az                = false" in configuration
    assert "aws_security_group.database.id" in configuration
    assert "aws_security_group.api.id" in configuration


def test_terraform_secrets_and_frontend_origin_are_hardened() -> None:
    configuration = (TERRAFORM / "main.tf").read_text()

    assert 'resource "aws_secretsmanager_secret" "database"' in configuration
    assert 'resource "aws_s3_bucket_public_access_block" "frontend"' in configuration
    assert 'resource "aws_cloudfront_origin_access_control" "frontend"' in configuration
    assert 'resource "aws_iam_openid_connect_provider" "github"' in configuration
    assert "token.actions.githubusercontent.com:sub" in configuration


def test_ci_and_deploy_workflows_use_minimal_permissions_and_oidc() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    deploy = (ROOT / ".github" / "workflows" / "deploy.yml").read_text()

    assert "contents: read" in ci
    assert "id-token: write" in deploy
    assert "configure-aws-credentials" in deploy
    assert "role-to-assume" in deploy
    assert "aws_access_key_id" not in deploy
    assert "AdministratorAccess" not in deploy
    assert "github.sha" in deploy


def test_production_images_drop_root_privileges_and_state_is_ignored() -> None:
    dockerfile = (ROOT / "Dockerfile.api").read_text()
    consumer_dockerfile = (ROOT / "Dockerfile").read_text()
    gitignore = (ROOT / ".gitignore").read_text()

    assert "USER appuser" in dockerfile
    assert "USER appuser" in consumer_dockerfile
    assert ".terraform/" in gitignore
    assert "*.tfstate" in gitignore
    assert "*.tfplan" in gitignore
