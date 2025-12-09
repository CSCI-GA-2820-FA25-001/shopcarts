# 🛒 ShopCarts REST API Service

[![Build Status](https://github.com/CSCI-GA-2820-FA25-001/shopcarts/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-001/shopcarts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-001/shopcarts/branch/main/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-FA25-001/shopcarts)
## Overview

This microservice provides a RESTful API for managing customer **ShopCarts** and their **Items**. It allows clients to **create, read, update, delete, and list** shopcarts and items, following REST best practices.

The service is implemented using **Flask**, **SQLAlchemy**, and **PostgreSQL**, developed using **Test Driven Development (TDD)**, and deployed to **OpenShift** with a complete **CI/CD pipeline** using **Tekton**.

## Features

- Full CRUD operations for ShopCarts and Items
- RESTful API design with proper HTTP methods and status codes
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive test coverage (≥95%)
- Behavior-Driven Development (BDD) tests with Behave
- Automated CI/CD pipeline with Tekton
- Kubernetes/OpenShift deployment with health checks
- Container registry integration
- External access via OpenShift Routes

## Technology Stack

### Application
- **Python** 3.11+
- **Flask** 3.x - Web framework
- **Flask-SQLAlchemy** - ORM
- **PostgreSQL** 15 - Database (Alpine image)
- **Gunicorn** - WSGI HTTP Server

### Testing
- **Pytest** - Unit testing framework
- **Coverage.py** - Code coverage (≥95%)
- **Behave** - BDD testing with Selenium
- **Pylint** - Code linting (PEP 8 compliance)

### DevOps & Deployment
- **Docker** - Containerization
- **Kubernetes/OpenShift** - Container orchestration
- **Tekton** - CI/CD pipeline
- **Kaniko** - Container image building
- **K3D** - Local Kubernetes development

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenShift Cluster                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │                  Route (External)                   │ │
│  │    https://shopcarts-<namespace>.apps.cluster.com  │ │
│  └─────────────────┬────────────────────────────────┬─┘ │
│                    │                                 │   │
│  ┌─────────────────▼────────────┐   ┌───────────────▼──┐│
│  │   ShopCarts Service          │   │  Ingress/Route   ││
│  │   ClusterIP:8080             │   │  (Traefik)       ││
│  └─────────────────┬────────────┘   └──────────────────┘│
│                    │                                     │
│  ┌─────────────────▼────────────┐                       │
│  │   ShopCarts Deployment       │                       │
│  │   - Replicas: 1              │                       │
│  │   - Container Port: 8080     │                       │
│  │   - Health Checks: /health   │                       │
│  │   - Readiness & Liveness     │                       │
│  └─────────────────┬────────────┘                       │
│                    │                                     │
│  ┌─────────────────▼────────────┐                       │
│  │   PostgreSQL StatefulSet     │                       │
│  │   - Port: 5432               │                       │
│  │   - Persistent Volume (1Gi)  │                       │
│  │   - ConfigMap & Secrets      │                       │
│  └──────────────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌────────┐    ┌────────────┐
│  GitHub  │───▶│  Webhook │───▶│   Tekton   │───▶│ Deploy │───▶│  BDD Tests │
│  Push    │    │ Trigger  │    │  Pipeline  │    │   App  │    │  (Behave)  │
└──────────┘    └──────────┘    └────────────┘    └────────┘    └────────────┘
                                       │
                        ┌──────────────┼──────────────┐
                        ▼              ▼              ▼
                   ┌────────┐   ┌──────────┐   ┌──────────┐
                   │  Clone │   │   Lint   │   │  Tests   │
                   │  Repo  │   │ (Pylint) │   │ (Pytest) │
                   └────────┘   └──────────┘   └──────────┘
                                       │
                                       ▼
                                ┌──────────┐
                                │  Build   │
                                │  Image   │
                                │ (Kaniko) │
                                └──────────┘
```


## Setup Instructions

### Local Development

#### 1. Clone the Repository
```bash
git clone https://github.com/CSCI-GA-2820-FA25-001/shopcarts.git
cd shopcarts
```

#### 2. Open in VSCode with DevContainer
Assuming VSCode and Docker are installed:
```bash
code .
```
Click "Reopen in Container" when prompted.

#### 3. Run Tests
To ensure everything is working:
```bash
make test
```

#### 4. Run the Service Locally
```bash
make run
# or
flask run -h 0.0.0.0 -p 8080
# or
honcho start
```

The service will be available at `http://localhost:8080`

### Kubernetes/OpenShift Deployment

#### Prerequisites
- OpenShift CLI (`oc`) or Kubernetes CLI (`kubectl`)
- Access to an OpenShift/Kubernetes cluster
- Tekton Pipelines installed on the cluster

#### 1. Create Kubernetes Resources
```bash
# Apply all Kubernetes manifests
oc apply -f k8s/

# Or apply specific resources
oc apply -f k8s/postgresql/
oc apply -f k8s/deployment.yaml
oc apply -f k8s/service.yaml
oc apply -f k8s/route.yaml
```

#### 2. Set Up Tekton Pipeline
```bash
# Apply pipeline resources
oc apply -f .tekton/tasks.yaml
oc apply -f .tekton/pipeline.yaml

# Apply event triggers (for GitHub webhooks)
oc apply -f .tekton/events/
```

#### 3. Verify Deployment
```bash
# Check pods
oc get pods


# Check services
oc get svc

# Check route
oc get route shopcarts

# Test the service
ROUTE_URL=$(oc get route shopcarts -o jsonpath='{.spec.host}')
curl https://$ROUTE_URL/health
```


## Testing

### Unit Tests
Run pytest with coverage:
```bash
make test
```

Requirements:
- Minimum 95% code coverage
- All tests must pass
- Database connection via secret

### BDD Tests
Run Behave tests:
```bash
behave
```

The BDD tests use Selenium WebDriver to test the application through the browser. They automatically target the deployed service using the `BASE_URL` environment variable.

### Linting
Run pylint to check code quality:
```bash
make lint
```

## CI/CD Pipeline

The project uses Tekton for continuous integration and deployment. The pipeline is automatically triggered on pushes to the repository.

### Pipeline Stages

1. **Clone** - Clone the repository
2. **Lint** - Run pylint on the codebase
3. **Unit Tests** - Run pytest with database connection
4. **Build** - Build and push Docker image with Kaniko
5. **Deploy** - Deploy to OpenShift cluster
6. **BDD Tests** - Run Behave tests against deployed service

### Pipeline Parameters

- `APP_NAME` - Application name (default: shopcarts)
- `GIT_REPO` - Git repository URL
- `IMAGE_NAME` - Docker image name
- `GIT_REVISION` - Git branch/tag (default: main)
- `BASE_URL` - Route URL for BDD testing

### Manual Pipeline Run

```bash
# Get the Route URL
ROUTE_URL=$(oc get route shopcarts -o jsonpath='https://{.spec.host}')

# Create a PipelineRun
cat <<EOF | oc apply -f -
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  generateName: cd-pipeline-manual-
spec:
  serviceAccountName: pipeline
  pipelineRef:
    name: cd-pipeline
  params:
    - name: APP_NAME
      value: shopcarts
    - name: GIT_REPO
      value: https://github.com/CSCI-GA-2820-FA25-001/shopcarts.git
    - name: IMAGE_NAME
      value: image-registry.openshift-image-registry.svc:5000/$(oc project -q)/shopcarts
    - name: GIT_REVISION
      value: main
    - name: BASE_URL
      value: $ROUTE_URL
  workspaces:
    - name: pipeline-workspace
      persistentVolumeClaim:
        claimName: pipeline-pvc
    - name: dockerconfig
      emptyDir: {}
EOF
```

### View Pipeline Logs

```bash
# Watch pipeline runs
oc get pipelinerun -w

# Get logs for specific task
LATEST_RUN=$(oc get pipelinerun --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
oc logs -l tekton.dev/pipelineRun=$LATEST_RUN -l tekton.dev/pipelineTask=
```


## API Documentation

### Root Endpoint
```http
GET /
```
Response:
```json
{
  "name": "ShopCarts Demo REST API Service",
  "version": "1.0",
  "paths": "http://localhost:8080/api/shopcarts"
}
```

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "OK"
}
```

### ShopCarts Endpoints

#### Create a Shopcart
```http
POST /api/shopcarts
Content-Type: application/json

{
  "customer_id": 123
}
```
Response: `201 Created`
```json
{
  "shopcart_id": 1,
  "customer_id": 123
}
```

#### List All Shopcarts
```http
GET /api/shopcarts
```
Response: `200 OK`
```json
[
  {
    "shopcart_id": 1,
    "customer_id": 123
  },
  {
    "shopcart_id": 2,
    "customer_id": 456
  }
]
```

#### Get a Shopcart
```http
GET /api/shopcarts/{shopcart_id}
```
Response: `200 OK`
```json
{
  "shopcart_id": 1,
  "customer_id": 123
}
```

#### Update a Shopcart
```http
PUT /api/shopcarts/{shopcart_id}
Content-Type: application/json

{
  "customer_id": 124
}
```
Response: `200 OK`
```json
{
  "shopcart_id": 1,
  "customer_id": 124
}
```

#### Delete a Shopcart
```http
DELETE /api/shopcarts/{shopcart_id}
```
Response: `204 No Content`

### Items Endpoints

#### Add Item to Shopcart
```http
POST /api/shopcarts/{shopcart_id}/items
Content-Type: application/json

{
  "product_id": 101,
  "quantity": 2,
  "price": 19.99
}
```
Response: `201 Created`
```json
{
  "item_id": 1,
  "shopcart_id": 1,
  "product_id": 101,
  "quantity": 2,
  "price": "19.99"
}
```

#### List Items in Shopcart
```http
GET /api/shopcarts/{shopcart_id}/items
```
Response: `200 OK`
```json
[
  {
    "item_id": 1,
    "shopcart_id": 1,
    "product_id": 101,
    "quantity": 2,
    "price": "19.99"
  }
]
```

#### Get an Item
```http
GET /api/shopcarts/{shopcart_id}/items/{item_id}
```
Response: `200 OK`
```json
{
  "item_id": 1,
  "shopcart_id": 1,
  "product_id": 101,
  "quantity": 2,
  "price": "19.99"
}
```

#### Update an Item
```http
PUT /api/shopcarts/{shopcart_id}/items/{item_id}
Content-Type: application/json

{
  "quantity": 3,
  "price": 19.99
}
```
Response: `200 OK`
```json
{
  "item_id": 1,
  "shopcart_id": 1,
  "product_id": 101,
  "quantity": 3,
  "price": "19.99"
}
```

#### Delete an Item
```http
DELETE /api/shopcarts/{shopcart_id}/items/{item_id}
```
Response: `204 No Content`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URI` | PostgreSQL connection string | `postgresql+psycopg://postgres:postgres@localhost:5432/postgres` |
| `PORT` | Application port | `8080` |
| `SECRET_KEY` | Flask secret key for sessions | `sup3r-s3cr3t` |
| `BASE_URL` | Base URL for BDD tests | `http://localhost:8080` |

## Development Commands

| Command | Description |
|---------|-------------|
| `make help` | Display available commands |
| `make install` | Install dependencies |
| `make test` | Run unit tests with coverage |
| `make lint` | Run pylint on code |
| `make run` | Run the service locally |
| `make cluster` | Create local K3D cluster |
| `make deploy` | Deploy to Kubernetes |
| `make build` | Build Docker image |
| `make push` | Push image to registry |
