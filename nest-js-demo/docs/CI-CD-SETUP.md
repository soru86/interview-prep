# nest-js-demo CI/CD Setup Guide

This guide walks through provisioning AWS infrastructure, configuring GitHub Actions, and running the full CI/CD pipeline for **nest-js-demo** on **Amazon EKS** with images stored in **Amazon ECR**.

## Pipeline overview

| Phase | Step | Where it runs |
|-------|------|---------------|
| CI | Build + lint | GitHub Actions runner |
| CI | Unit tests | Kubernetes Job in `nest-js-demo-ci` |
| CI | Integration tests (e2e) | Kubernetes Job + ephemeral Kafka |
| CI | Build container image | GitHub Actions → ECR |
| CI | Deploy staging | Helm → `nest-js-demo-staging` namespace |
| CI | Automation tests | Kubernetes Job (Playwright) |
| CD | Deploy production | Helm → `nest-js-demo-prod` namespace |

Workflow file: [`.github/workflows/nest-js-demo-cicd.yml`](../../.github/workflows/nest-js-demo-cicd.yml)

---

## 1. Prerequisites

### Tools

Install locally:

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) v2
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/) v3
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [Docker](https://docs.docker.com/get-docker/)
- Node.js 20+ (for local validation)

### Accounts and access

- AWS account with permissions to create VPC, EKS, ECR, and IAM roles
- GitHub repository containing this monorepo
- Ability to configure GitHub Actions secrets/variables and environments

---

## 2. Provision AWS with Terraform

All infrastructure lives under [`infra/terraform/`](../infra/terraform/).

### 2.1 Configure variables

```bash
cd nest-js-demo/infra/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

| Variable | Description |
|----------|-------------|
| `aws_region` | AWS region (e.g. `us-east-1`) |
| `github_org` | GitHub user or organization |
| `github_repo` | Repository name (e.g. `learning-code-labs`) |
| `create_cluster` | `true` to create EKS; `false` to use existing cluster |
| `existing_cluster_name` | Required when `create_cluster = false` |

### 2.2 Apply Terraform

```bash
terraform init
terraform plan
terraform apply
```

Capture outputs:

```bash
terraform output ecr_registry
terraform output ecr_repository_name
terraform output eks_cluster_name
terraform output github_actions_role_arn
```

### 2.3 What Terraform creates

- **ECR repository** (`nest-js-demo`) with scan-on-push and lifecycle policy
- **VPC** with public/private subnets and NAT gateway (when creating cluster)
- **EKS cluster** with managed node group
- **GitHub OIDC provider** and **IAM role** for Actions (ECR + EKS access)
- **EKS access entry** granting the GitHub Actions role cluster admin (when cluster is created)

---

## 3. Configure kubectl for EKS

```bash
aws eks update-kubeconfig \
  --name "$(terraform -chdir=nest-js-demo/infra/terraform output -raw eks_cluster_name)" \
  --region us-east-1

kubectl get nodes
```

You should see worker nodes in `Ready` state.

---

## 4. Install EKS cluster add-ons

These steps are manual post-Terraform requirements for ingress and autoscaling.

### 4.1 AWS Load Balancer Controller

Required for ALB Ingress resources created by the Helm chart.

Follow the [official installation guide](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html):

1. Create IAM policy and service account for the controller
2. Install via Helm:

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=YOUR_CLUSTER_NAME \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller
```

### 4.2 metrics-server (optional, for HPA)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## 5. Create Kubernetes namespaces

Apply base namespaces once:

```bash
kubectl apply -f nest-js-demo/k8s/base/namespaces.yaml
kubectl apply -f nest-js-demo/k8s/base/namespace-ci.yaml
```

| Namespace | Purpose |
|-----------|---------|
| `nest-js-demo-ci` | CI test Jobs |
| `nest-js-demo-staging` | Staging deployment |
| `nest-js-demo-prod` | Production deployment |

---

## 6. Sanity-check ECR locally (optional)

```bash
export AWS_REGION=us-east-1
export ECR_REGISTRY="$(terraform -chdir=nest-js-demo/infra/terraform output -raw ecr_registry)"

aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

docker build -t nest-js-demo:local nest-js-demo
docker tag nest-js-demo:local "${ECR_REGISTRY}/nest-js-demo:local"
docker push "${ECR_REGISTRY}/nest-js-demo:local"
```

---

## 7. Configure GitHub Actions

Reference file: [`.github/env.example`](../.github/env.example)

### 7.1 Repository variables

GitHub → **Settings → Secrets and variables → Actions → Variables**

| Name | Example value |
|------|-----------------|
| `AWS_REGION` | `us-east-1` |
| `EKS_CLUSTER_NAME` | `nest-js-demo-dev-cluster` |
| `ECR_REGISTRY` | `123456789012.dkr.ecr.us-east-1.amazonaws.com` |
| `ECR_REPOSITORY` | `nest-js-demo` |

### 7.2 Repository secrets

| Name | Source |
|------|--------|
| `AWS_ROLE_ARN` | `terraform output github_actions_role_arn` |
| `JWT_SECRET` | Generate a long random string |

### 7.3 GitHub Environments (recommended)

Create two environments under **Settings → Environments**:

**staging**
- Used by the `deploy-staging` job
- No required reviewers (auto-deploy after tests)

**production**
- Used by the `deploy-production` job
- Enable **Required reviewers** for manual approval before production deploy

---

## 8. Customize Helm values

Before first deploy, update hostnames in:

- [`helm/nest-js-demo/values-staging.yaml`](../helm/nest-js-demo/values-staging.yaml)
- [`helm/nest-js-demo/values-prod.yaml`](../helm/nest-js-demo/values-prod.yaml)

Replace `*.example.com` with your real DNS names (or disable Ingress and use port-forward for testing).

Manual staging deploy example:

```bash
helm upgrade --install nest-js-demo-staging nest-js-demo/helm/nest-js-demo \
  --namespace nest-js-demo-staging \
  --create-namespace \
  -f nest-js-demo/helm/nest-js-demo/values-staging.yaml \
  --set image.repository="${ECR_REGISTRY}/nest-js-demo" \
  --set image.tag=local \
  --set testRunner.repository="${ECR_REGISTRY}/nest-js-demo" \
  --set testRunner.tag=local-test \
  --set secrets.jwtSecret="your-jwt-secret"
```

---

## 9. Run the pipeline

### Automatic triggers

| Event | Behavior |
|-------|----------|
| Pull request (paths: `nest-js-demo/**`) | Build, lint, K8s unit/integration tests, Docker build (no push/deploy) |
| Push to `main` | Full CI + staging deploy + automation tests + production deploy |
| Manual | **Actions → NestJS Demo CI/CD → Run workflow** |

### Monitor a run

1. Open **Actions** tab in GitHub
2. Select **NestJS Demo CI/CD**
3. Watch jobs in order: `build` → `unit-tests` → `integration-tests` → `publish-image` → `deploy-staging` → `automation-tests` → `deploy-production`

---

## 10. Verify CI steps

### Unit test Job

```bash
kubectl get jobs -n nest-js-demo-ci
kubectl logs job/nest-js-demo-unit-test -n nest-js-demo-ci
```

### Integration test Job

```bash
kubectl logs job/nest-js-demo-integration-test -n nest-js-demo-ci
```

### ECR image

```bash
aws ecr describe-images \
  --repository-name nest-js-demo \
  --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags'
```

### Staging health check

```bash
kubectl port-forward svc/nest-js-demo-staging -n nest-js-demo-staging 3000:3000
curl http://localhost:3000/api/health
```

### Automation test Job

```bash
kubectl logs job/nest-js-demo-automation-test -n nest-js-demo-ci
```

---

## 11. Verify CD (production)

After the `deploy-production` job succeeds:

```bash
kubectl rollout status deployment/nest-js-demo -n nest-js-demo-prod
kubectl get ingress -n nest-js-demo-prod
kubectl get pods -n nest-js-demo-prod
```

If Ingress is configured with a real hostname:

```bash
curl https://nest-js-demo.example.com/api/health
```

---

## 12. Troubleshooting

### OIDC / AWS authentication failures

- Confirm `AWS_ROLE_ARN` matches Terraform output
- Verify `github_org` and `github_repo` in `terraform.tfvars` match the actual repository
- Ensure workflow has `permissions: id-token: write`

### Image pull errors on EKS nodes

- Worker nodes use `AmazonEC2ContainerRegistryReadOnly` policy (created by Terraform)
- Confirm image was pushed: `aws ecr list-images --repository-name nest-js-demo`

### Unit/integration Job failures

```bash
kubectl describe job/nest-js-demo-unit-test -n nest-js-demo-ci
kubectl logs job/nest-js-demo-unit-test -n nest-js-demo-ci --all-containers=true
```

Common causes:
- Insufficient cluster resources (scale node group)
- Test-runner image not pushed to ECR

### Kafka not ready (integration tests)

```bash
kubectl get pods -n nest-js-demo-ci -l app.kubernetes.io/name=kafka
kubectl logs deployment/kafka -n nest-js-demo-ci
```

### App pod CrashLoopBackOff

The app requires Kafka at startup. Verify Kafka pod is running in the same namespace:

```bash
kubectl get pods -n nest-js-demo-staging
kubectl logs deployment/nest-js-demo-staging -n nest-js-demo-staging
```

### Automation tests cannot reach staging

The automation Job uses in-cluster DNS:

`http://nest-js-demo-staging.nest-js-demo-staging.svc.cluster.local:3000`

Ensure staging deployment is healthy before the automation Job runs.

### Helm deploy timeout

```bash
helm status nest-js-demo-staging -n nest-js-demo-staging
kubectl describe pod -n nest-js-demo-staging -l app.kubernetes.io/name=nest-js-demo
```

Check init container `seed-database` logs if the main container never starts.

---

## 13. Local parity

### Run unit tests locally

```bash
cd nest-js-demo
npm ci
npm test
```

### Run integration (e2e) tests locally

```bash
npm run docker:up
npm run test:e2e
```

### Run automation tests locally

```bash
npm run start:dev &
export BASE_URL=http://localhost:3000
npm run test:automation
```

### Build and run test-runner image locally

```bash
docker build -f nest-js-demo/docker/test-runner/Dockerfile -t nest-js-demo-test nest-js-demo
docker run --rm nest-js-demo-test npm test
```

### Build production image locally

```bash
docker build -t nest-js-demo:local nest-js-demo
docker run --rm -p 3000:3000 \
  -e KAFKA_BROKERS=host.docker.internal:9092 \
  -e JWT_SECRET=local-secret \
  nest-js-demo:local
```

---

## 14. Repository layout reference

```
nest-js-demo/
├── Dockerfile                          # Production image
├── docker/test-runner/Dockerfile       # CI test image
├── k8s/
│   ├── base/                           # Namespaces
│   ├── jobs/                           # Unit/integration/automation Jobs
│   └── test-deps/                      # Ephemeral Kafka for CI
├── helm/nest-js-demo/                  # Staging/production chart
├── infra/terraform/                    # AWS bootstrap
├── tests/automation/                   # Playwright smoke tests
├── scripts/k8s-run-job.sh              # Job runner helper
└── docs/CI-CD-SETUP.md                 # This guide

.github/workflows/nest-js-demo-cicd.yml # Pipeline definition
```

---

## 15. Security notes

- Never commit `terraform.tfvars`, `.env`, or real secrets
- Rotate `JWT_SECRET` regularly in production
- Use GitHub Environment protection rules for production deploys
- ECR image scanning is enabled by Terraform; review findings in AWS Console
- Consider AWS Secrets Manager or External Secrets Operator for production JWT management instead of Helm `--set secrets.jwtSecret`

---

## 16. Cost considerations

Approximate monthly cost drivers:

- EKS control plane (~$73/month)
- EC2 worker nodes (e.g. 2× `t3.medium`)
- NAT gateway (~$32/month + data transfer)
- ECR storage (minimal for demo usage)

To reduce cost in dev:
- Set `node_desired_size = 1` in Terraform
- Use `single_nat_gateway = true` (already default)
- Tear down with `terraform destroy` when not in use
