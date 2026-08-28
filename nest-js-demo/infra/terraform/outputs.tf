output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_registry" {
  description = "ECR registry host (for GitHub Variables)"
  value       = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
}

output "ecr_repository_name" {
  description = "ECR repository name"
  value       = aws_ecr_repository.app.name
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = var.create_cluster ? aws_eks_cluster.this[0].name : var.existing_cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = var.create_cluster ? aws_eks_cluster.this[0].endpoint : data.aws_eks_cluster.existing[0].endpoint
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions OIDC (set as AWS_ROLE_ARN secret)"
  value       = var.enable_github_oidc ? aws_iam_role.github_actions[0].arn : null
}

output "vpc_id" {
  description = "VPC ID for the EKS cluster"
  value       = var.create_cluster ? module.vpc[0].vpc_id : null
}
