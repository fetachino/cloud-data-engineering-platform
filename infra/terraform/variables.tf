variable "project_name" {
  description = "Short project name used in AWS resource names."
  type        = string
  default     = "cloud-data-platform"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "portfolio"
}

variable "aws_region" {
  description = "Single AWS region for this portfolio environment."
  type        = string
  default     = "us-east-1"
}

variable "availability_zones" {
  description = "Availability zones used for the public and private subnet pairs."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Exactly two availability zones are expected for this portfolio deployment."
  }
}

variable "vpc_cidr" {
  description = "CIDR range for the deployment VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "api_image_uri" {
  description = "Optional immutable ECR image URI for the analytics API."
  type        = string
  default     = null
}

variable "image_tag" {
  description = "Immutable image tag used when api_image_uri is not supplied."
  type        = string
  default     = "bootstrap"
}

variable "api_cpu" {
  description = "Fargate CPU units for the single API task."
  type        = number
  default     = 256
}

variable "api_memory" {
  description = "Fargate memory in MiB for the single API task."
  type        = number
  default     = 512
}

variable "api_desired_count" {
  description = "Number of API tasks kept running. One is intentional for cost control."
  type        = number
  default     = 1
}

variable "db_instance_class" {
  description = "Small RDS instance class for the portfolio environment."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Application database name."
  type        = string
  default     = "ecommerce"
}

variable "db_username" {
  description = "Application database username."
  type        = string
  default     = "platform"
}

variable "github_repository" {
  description = "GitHub owner/repository allowed to assume the deployment role."
  type        = string
  default     = "fetachino/cloud-data-engineering-platform"
}

variable "frontend_bucket_name" {
  description = "Optional globally unique S3 bucket name for the frontend."
  type        = string
  default     = null
}
