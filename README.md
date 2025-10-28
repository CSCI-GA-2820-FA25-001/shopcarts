# 🛒 ShopCarts REST API Service

[![Build Status](https://github.com/CSCI-GA-2820-FA25-001/shopcarts/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-001/shopcarts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-001/shopcarts/branch/main/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-FA25-001/shopcarts)
## Overview
This microservice provides a RESTful API for managing customer **ShopCarts** and their **Items**.  
It allows clients to **create, read, update, delete, and list** shopcarts and items, following REST best practices.  
The service is implemented using **Flask**, **SQLAlchemy**, and **PostgreSQL**, and developed using **Test Driven Development (TDD)**.


## Sprint 1 Goal
**Develop a local REST API** implementing CRUD operations for ShopCarts and Items.  
Testing, linting, and documentation are part of every story.


## Technology Stack
- Python 3.11+
- Flask 3.x
- Flask-SQLAlchemy
- PostgreSQL 15 (via Docker)
- Pytest + Coverage (≥ 95%)
- Pylint (PEP 8 compliance)



## Setup Instructions

### 1. Clone the Repository
In a new terminal window:
```bash
git clone https://github.com/CSCI-GA-2820-FA25-001/shopcarts.git
cd shopcarts
```
### 2. Open in VSCode
Assuming VSCode and Docker are already installed, run this:
```bash
code .
```
and click "Reopen in Container"

### 3. Run Tests
To ensure everything is working:
```bash
make test
```

### 4. Running the Service
```bash
  make run
  # or
  flask run -h 0.0.0.0 -p 8080
  # or
  honcho start
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
  "paths": "http://localhost:8080/shopcarts"
}
```
### <u>ShopCarts Endpoints and Expected Responses</u>
```http
POST   /shopcarts
GET    /shopcarts
GET    /shopcarts/<shopcart_id>
DELETE /shopcarts/<shopcart_id>
```
- **Create a Shopcart** (expects a json input) 
    ```http
    POST /shopcarts
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
    GET /shopcarts
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
    GET /shopcarts/<shopcart_id>
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
    DELETE /shopcarts/<shopcart_id>
    ```
- **Update a Shopcart**
  ```http
  PUT /shopcarts/<shopcart_id>
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
POST   /shopcarts/<shopcart_id>/items
GET    /shopcarts/<shopcart_id>/items
GET    /shopcarts/<shopcart_id>/items/<item_id>
PUT    /shopcarts/<shopcart_id>/items/<item_id>
```

- **Create an Item inside a Shopcart**
  ```http
  POST /shopcarts/<shopcart_id>/items
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
  GET /shopcarts/<shopcart_id>/items
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
  GET /shopcarts/<shopcart_id>/items/<item_id>
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
  DELETE /shopcarts/<shopcart_id>/items/<item_id>
  ```

- **Update an Item in a Shopcart**
  ```http
  PUT /shopcarts/<shopcart_id>/items/<item_id>
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
