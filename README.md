# R-Python-project
# E-Commerce Backend API

## Project Description

This project is a backend system for an E-Commerce application built using FastAPI.

The system allows users to register, login, browse products, manage shopping carts, and place orders. It also includes admin features for managing products, categories, orders, users, caching, logging, monitoring, and testing.

The project follows a clean and modular structure with separated routes, models, schemas, authentication, caching, logging, middleware, and tests.

---

## Main Features

* User registration and login
* JWT authentication
* Role-based authorization
* Admin and Customer roles
* Product management
* Category management
* Shopping cart functionality
* Order placement and tracking
* Order items management
* Basic inventory management
* Product search, filtering, and pagination
* Redis caching
* Cache invalidation after create, update, and delete operations
* Structured logging
* Monitoring endpoints
* API testing using pytest
* Docker support
* Simple frontend integration

---

## User Roles

### Admin

The admin can:

* Manage products
* Manage categories
* View all orders
* Manage users
* Access monitoring endpoints
* Perform delete and update operations

### Customer

The customer can:

* Register and login
* Browse products
* Search and filter products
* Manage shopping cart
* Place orders
* Track personal orders

---

## Project Structure

app/
├── cache/
│   └── redis_cache.py
│
├── core/
│   └── security.py
│
├── database/
│   └── database.py
│
├── logging/
│   └── logger.py
│
├── middleware/
│   └── logging_middleware.py
│
├── models/
│   ├── user.py
│   ├── product.py
│   └── order.py
│
├── routes/
│   ├── auth.py
│   ├── users.py
│   ├── products.py
│   ├── categories.py
│   ├── cart.py
│   ├── orders.py
│   └── monitoring.py
│
├── schemas/
│   ├── user.py
│   ├── product.py
│   └── order.py
│
├── dependencies.py
└── main.py

tests/
├── conftest.py
├── test_auth.py
├── test_products.py
└── test_orders.py

frontend/
Dockerfile
docker-compose.yml
requirements.txt
README.md

---

## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT
* Redis
* Pytest
* Docker
* Docker Compose
* Prometheus
* HTML
* CSS
* JavaScript

---

## Authentication

The project uses JWT Authentication.

Authentication includes:

* User registration
* User login
* JWT token generation
* JWT token validation
* Protected routes
* Role-based access control

After login, the user receives an access token.

This token must be sent in the Authorization header:

Authorization: Bearer <token>

---

## API Endpoints

### Authentication

POST /auth/register
POST /auth/login

### Users

GET /users
GET /users/{user_id}
PUT /users/{user_id}
DELETE /users/{user_id}

### Products

GET /products
GET /products/{product_id}
POST /products
PUT /products/{product_id}
DELETE /products/{product_id}

### Categories

GET /categories
GET /categories/{category_id}
POST /categories
PUT /categories/{category_id}
DELETE /categories/{category_id}

### Cart

GET /cart
POST /cart
PUT /cart/{item_id}
DELETE /cart/{item_id}

### Orders

GET /orders
GET /orders/{order_id}
POST /orders
PUT /orders/{order_id}

### Monitoring

GET /health
GET /metrics

---

## Redis Caching

Redis is used to improve API performance by caching frequently requested data.

Cached data includes:

* Product list
* Product details by ID
* Category data

The project follows the Cache-Aside Pattern.

Cache is invalidated when:

* A new product is created
* A product is updated
* A product is deleted
* A category is updated or deleted

---

## Logging and Monitoring

The project includes structured logging for:

* Incoming API requests
* API responses
* Response time
* Authentication events
* Login attempts
* Token validation
* CRUD operations
* Errors and exceptions

Monitoring endpoints are included to display:

* API request count
* Response time
* Error rate
* System health status

---

## Testing

The project includes tests using pytest and FastAPI TestClient.

Tests cover:

* User registration
* User login
* JWT token generation
* Protected endpoints
* Role-based restrictions
* Product CRUD operations
* Order operations
* Error handling
* Invalid inputs

To run tests:

pytest

---

## Installation and Setup

### 1. Clone the Repository

git clone <repository-url>
cd ecommerce-backend-api

### 2. Create Virtual Environment

python -m venv venv

### 3. Activate Virtual Environment

For Windows:

venv\Scripts\activate

For Mac/Linux:

source venv/bin/activate

### 4. Install Requirements

pip install -r requirements.txt

### 5. Run the Application

uvicorn app.main:app --reload

The API will run on:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs

---

## Docker Setup

To run the project using Docker:

docker-compose up --build

This will start:

* FastAPI application
* Database service
* Redis service
* Monitoring service

---

## Environment Variables

Create a .env file and add the required environment variables:

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./ecommerce.db
REDIS_HOST=localhost
REDIS_PORT=6379

Do not upload the .env file to GitHub.

---

## GitHub Collaboration Strategy

The team used Git and GitHub for version control.

Branching strategy:

main
develop
feature/auth-users-jwt
feature/products-categories
feature/cart-orders
feature/redis-logging-monitoring
feature/tests-frontend-docs





---

## Notes

* The project follows RESTful API principles.
* Request validation is handled using Pydantic schemas.
* HTTP status codes are used properly.
* Errors are handled using HTTPException.
* Admin and Customer roles are separated.
* GitHub commits show individual team member contributions.

---

