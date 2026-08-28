variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
  default     = "nest-js-demo"
}

variable "environment" {
  description = "Environment label (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}

variable "create_cluster" {
  description = "Whether to create a new EKS cluster"
  type        = bool
  default     = true
}

variable "existing_cluster_name" {
  description = "Existing EKS cluster name when create_cluster is false"
  type        = string
  default     = ""
}

variable "cluster_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "Instance types for the managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 3
}

variable "ecr_repository_name" {
  description = "ECR repository name for application images"
  type        = string
  default     = "nest-js-demo"
}

variable "github_org" {
  description = "GitHub organization or user that owns the repository"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_branches" {
  description = "Git branches allowed to assume the GitHub Actions IAM role"
  type        = list(string)
  default     = ["main"]
}

variable "enable_github_oidc" {
  description = "Create GitHub OIDC provider and IAM role for Actions"
  type        = bool
  default     = true
}
