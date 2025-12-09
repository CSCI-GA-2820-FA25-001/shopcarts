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

## API Details

### <u> Root Endpoint </u>
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
### <u>ShopCarts Endpoints and Expected Responses</u>
```http
POST   /api/shopcarts
GET    /api/shopcarts
GET    /api/shopcarts/<shopcart_id>
DELETE /api/shopcarts/<shopcart_id>
```
- **Create a Shopcart** (expects a json input) 
    ```http
    POST /api/shopcarts
    Content-Type: application/json
    ```
    Request Body:
    ```json
    {
    "customer_id": 123
    }
    ```
    Response:
    ```json
    {
    "customer_id": 123
    "shopcart_id": 1
    }
    ```
- **List Shopcarts**
     ```http
    GET /api/shopcarts
    ```
    Response 
    ```json
   [
      {
        "customer_id": 123,
        "shopcart_id": 855
      },
      {
        "customer_id": 13,
        "shopcart_id": 857
      }
    ]
    ```
- **Read a Shopcart**
    
    ```http
    GET /api/shopcarts/<shopcart_id>
    ```
  Response (assuming input 855)
  ```json
  {
  "customer_id": 123,
  "shopcart_id": 855
  }
  ```
- **Delete a Shopcart** 
  ```http
    DELETE /api/shopcarts/<shopcart_id>
  ```
- **Update a Shopcart**
  ```http
  PUT /api/shopcarts/<shopcart_id>
  Content-Type: application/json
  ```
  Request Body:
  ```json
  {
  "shopcart_id": 855,
  "customer_id": 124
  }
  ```

  Response (assuming input 855)
  ```json
  {
  "shopcart_id": 855,
  "customer_id": 124
  }
  ```



### <u>Items Endpoints and Expected Responses</u>
```http
POST   /api/shopcarts/<shopcart_id>/items
GET    /api/shopcarts/<shopcart_id>/items
GET    /api/shopcarts/<shopcart_id>/items/<item_id>
PUT    /api/shopcarts/<shopcart_id>/items/<item_id>
```

- **Create an Item inside a Shopcart**
  ```http
  POST /api/shopcarts/<shopcart_id>/items
  Content-Type: application/json
  ```
  Request Body:
  ```json
  {
    "product_id": 101,
    "quantity": 2,
    "price": 19.99
  }
  ```
  Response:
  ```json
  {
    "item_id": 1,
    "shopcart_id": 855,
    "product_id": 101,
    "quantity": 2,
    "price": "19.99"
  }
  ```

- **List All Items in a Shopcart**
  ```http
  GET /api/shopcarts/<shopcart_id>/items
  ```
  Response:
  ```json
  [
    {
      "item_id": 1,
      "shopcart_id": 855,
      "product_id": 101,
      "quantity": 2,
      "price": "19.99"
    },
    {
      "item_id": 2,
      "shopcart_id": 855,
      "product_id": 102,
      "quantity": 1,
      "price": "9.99"
    }
  ]
  ```

- **Retrieve a Specific Item**
  ```http
  GET /api/shopcarts/<shopcart_id>/items/<item_id>
  ```
  Response:
  ```json
  {
    "item_id": 1,
    "shopcart_id": 855,
    "product_id": 101,
    "quantity": 2,
    "price": "19.99"
  }
  ```
- **Delete an Item in a Shopcart**
    ```http
  DELETE /api/shopcarts/<shopcart_id>/items/<item_id>
  ```

- **Update an Item in a Shopcart**
  ```http
  PUT /api/shopcarts/<shopcart_id>/items/<item_id>
  Content-Type: application/json
  ```
  Request Body:
  ```json
  {
    "quantity": 3,
    "unit_price": 19.99
  }
  ```
  Response:
  ```json
  {
    "item_id": 1,
    "shopcart_id": 855,
    "product_id": 101,
    "quantity": 3,
    "price": "59.97"
  }
  ```
