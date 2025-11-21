# CRUD API with MVC Architecture

A complete CRUD (Create, Read, Update, Delete) API implementation using FastAPI with proper MVC (Model-View-Controller) architecture pattern.

## 🏗️ Architecture Overview

```
crud_implementation/
├── config/                 # Configuration layer
│   └── database.py         # Database configuration
├── models/                 # Model layer (Data)
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── product.py         # Product model
│   └── order.py           # Order model
├── controllers/            # Controller layer (Business Logic)
│   ├── __init__.py
│   ├── user_controller.py # User business logic
│   ├── product_controller.py # Product business logic
│   └── order_controller.py # Order business logic
├── views/                  # View layer (API Interface)
│   ├── __init__.py
│   ├── user_views.py      # User API endpoints
│   ├── product_views.py   # Product API endpoints
│   └── order_views.py     # Order API endpoints
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── test_api.py           # API testing script
└── README.md             # This file
```

## 🎯 MVC Pattern Explanation

### **Model Layer** (`models/`)
- **Purpose**: Represents data and business rules
- **Contains**: Database models, data validation, relationships
- **Files**: `user.py`, `product.py`, `order.py`

### **View Layer** (`views/`)
- **Purpose**: Handles user interface and API endpoints
- **Contains**: FastAPI routes, request/response handling
- **Files**: `user_views.py`, `product_views.py`, `order_views.py`

### **Controller Layer** (`controllers/`)
- **Purpose**: Contains business logic and coordinates between Model and View
- **Contains**: CRUD operations, business rules, data processing
- **Files**: `user_controller.py`, `product_controller.py`, `order_controller.py`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
Update `config/database.py` with your database credentials:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/crud_db"
```

### 3. Run the Application
```bash
python main.py
```

### 4. Access the API
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    category VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Orders Table
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    total_amount FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address VARCHAR(200),
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔗 API Endpoints

### Users
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get user by ID
- `POST /users/` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /users/search/` - Search users
- `POST /users/{user_id}/activate` - Activate user
- `POST /users/{user_id}/deactivate` - Deactivate user

### Products
- `GET /products/` - Get all products
- `GET /products/{product_id}` - Get product by ID
- `POST /products/` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product
- `GET /products/search/` - Search products
- `PUT /products/{product_id}/stock` - Update stock
- `POST /products/{product_id}/toggle-availability` - Toggle availability

### Orders
- `GET /orders/` - Get all orders
- `GET /orders/{order_id}` - Get order by ID
- `POST /orders/` - Create new order
- `PUT /orders/{order_id}/status` - Update order status
- `POST /orders/{order_id}/cancel` - Cancel order
- `DELETE /orders/{order_id}` - Delete order
- `GET /orders/statistics/` - Get order statistics

## 🧪 Testing

### Run the test script:
```bash
python test_api.py
```

### Manual testing with curl:
```bash
# Create a user
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "bio": "Software Developer"
  }'

# Get all users
curl http://localhost:8000/users/

# Create a product
curl -X POST "http://localhost:8000/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "price": 999.99,
    "description": "High-performance laptop",
    "category": "Electronics",
    "stock_quantity": 10
  }'
```

## 🎯 Key Features

### MVC Architecture Benefits:
- **Separation of Concerns**: Each layer has a specific responsibility
- **Maintainability**: Easy to modify and extend
- **Testability**: Each layer can be tested independently
- **Scalability**: Easy to add new features and endpoints

### Business Logic Features:
- **User Management**: Complete user CRUD with activation/deactivation
- **Product Management**: Product CRUD with stock management
- **Order Management**: Order processing with status tracking
- **Search Functionality**: Search across users, products
- **Statistics**: Order statistics and reporting

### Technical Features:
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy ORM**: Database abstraction layer
- **Pydantic**: Data validation and serialization
- **PostgreSQL**: Production-ready database
- **Automatic Documentation**: Interactive API docs
- **Error Handling**: Comprehensive error responses

## 🔧 Configuration

### Environment Variables:
```bash
# Database URL
DATABASE_URL=postgresql://username:password@localhost:5432/crud_db

# Alternative databases:
# SQLite: sqlite:///./crud.db
# MySQL: mysql://username:password@localhost:3306/crud_db
```

### Database Setup:
1. Install PostgreSQL
2. Create database: `CREATE DATABASE crud_db;`
3. Update `config/database.py` with your credentials
4. Run the application (tables will be created automatically)

## 📚 Learning Outcomes

This implementation demonstrates:
- **MVC Pattern**: Proper separation of concerns
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM usage
- **API Design**: RESTful API principles
- **Error Handling**: Comprehensive error management
- **Testing**: API testing strategies
- **Documentation**: Self-documenting APIs

## 🚀 Next Steps

1. **Authentication**: Add JWT authentication
2. **Authorization**: Implement role-based access control
3. **Validation**: Add more comprehensive data validation
4. **Logging**: Implement structured logging
5. **Monitoring**: Add health checks and metrics
6. **Deployment**: Docker containerization
7. **CI/CD**: Automated testing and deployment

## 📖 Documentation

- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

**Happy Coding! 🚀**

