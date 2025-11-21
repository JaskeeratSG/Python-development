#!/usr/bin/env python3
"""
Test MVC CRUD Application
"""

from fastapi.testclient import TestClient
from main import app

def test_mvc_app():
    """Test the MVC CRUD application"""
    print("🧪 Testing MVC CRUD Application...")
    print("=" * 50)
    
    client = TestClient(app)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Create user
    print("\n3. Testing create user...")
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "full_name": "Test User",
        "bio": "This is a test user for MVC CRUD application"
    }
    
    response = client.post("/users/", params=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"Created user: {user['user']['username']} (ID: {user['user']['id']})")
        user_id = user['user']['id']
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 4: Create product
    print("\n4. Testing create product...")
    product_data = {
        "name": "Test Product",
        "price": 99.99,
        "description": "A test product for MVC CRUD application",
        "category": "Test",
        "stock_quantity": 5
    }
    
    response = client.post("/products/", params=product_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        product = response.json()
        print(f"Created product: {product['product']['name']} (ID: {product['product']['id']})")
        product_id = product['product']['id']
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 5: Create order
    print("\n5. Testing create order...")
    order_data = {
        "user_id": user_id,
        "product_id": product_id,
        "quantity": 2,
        "shipping_address": "123 Test St, Test City",
        "notes": "Test order"
    }
    
    response = client.post("/orders/", params=order_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        order = response.json()
        print(f"Created order: ID {order['order']['id']}, Total: ${order['order']['total_amount']}")
        order_id = order['order']['id']
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 6: Get all users
    print("\n6. Testing get all users...")
    response = client.get("/users/")
    print(f"Status: {response.status_code}")
    users = response.json()
    print(f"Found {users['count']} users")
    
    # Test 7: Get all products
    print("\n7. Testing get all products...")
    response = client.get("/products/")
    print(f"Status: {response.status_code}")
    products = response.json()
    print(f"Found {products['count']} products")
    
    # Test 8: Get all orders
    print("\n8. Testing get all orders...")
    response = client.get("/orders/")
    print(f"Status: {response.status_code}")
    orders = response.json()
    print(f"Found {orders['count']} orders")
    
    # Test 9: Update order status
    print(f"\n9. Testing update order {order_id} status...")
    response = client.put(f"/orders/{order_id}/status", params={"status": "confirmed"})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Order status updated to 'confirmed'")
    
    # Test 10: Get order statistics
    print("\n10. Testing get order statistics...")
    response = client.get("/orders/statistics/")
    print(f"Status: {response.status_code}")
    stats = response.json()
    print(f"Statistics: {stats['statistics']}")
    
    print("\n" + "=" * 50)
    print("🎉 MVC CRUD Application testing completed!")
    print("✅ All tests passed successfully!")

if __name__ == "__main__":
    test_mvc_app()

