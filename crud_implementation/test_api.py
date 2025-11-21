#!/usr/bin/env python3
"""
Test script for CRUD API with MVC Architecture
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """Test all API endpoints"""
    print("🚀 Testing CRUD API with MVC Architecture...")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Create User
    print("\n2. Creating a new user...")
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "bio": "Software Developer with 5 years experience"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", params=user_data)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"Created user: {user['user']['username']} (ID: {user['user']['id']})")
            user_id = user['user']['id']
        else:
            print(f"❌ Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 3: Create Product
    print("\n3. Creating a new product...")
    product_data = {
        "name": "Laptop",
        "price": 999.99,
        "description": "High-performance laptop for developers",
        "category": "Electronics",
        "stock_quantity": 10
    }
    
    try:
        response = requests.post(f"{BASE_URL}/products/", params=product_data)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            product = response.json()
            print(f"Created product: {product['product']['name']} (ID: {product['product']['id']})")
            product_id = product['product']['id']
        else:
            print(f"❌ Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 4: Create Order
    print("\n4. Creating a new order...")
    order_data = {
        "user_id": user_id,
        "product_id": product_id,
        "quantity": 2,
        "shipping_address": "123 Main St, City, State",
        "notes": "Please handle with care"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/orders/", params=order_data)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            order = response.json()
            print(f"Created order: ID {order['order']['id']}, Total: ${order['order']['total_amount']}")
            order_id = order['order']['id']
        else:
            print(f"❌ Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 5: Get All Users
    print("\n5. Getting all users...")
    try:
        response = requests.get(f"{BASE_URL}/users/")
        print(f"✅ Status: {response.status_code}")
        users = response.json()
        print(f"Found {users['count']} users")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Get All Products
    print("\n6. Getting all products...")
    try:
        response = requests.get(f"{BASE_URL}/products/")
        print(f"✅ Status: {response.status_code}")
        products = response.json()
        print(f"Found {products['count']} products")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Get All Orders
    print("\n7. Getting all orders...")
    try:
        response = requests.get(f"{BASE_URL}/orders/")
        print(f"✅ Status: {response.status_code}")
        orders = response.json()
        print(f"Found {orders['count']} orders")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Update Order Status
    print(f"\n8. Updating order {order_id} status...")
    try:
        response = requests.put(f"{BASE_URL}/orders/{order_id}/status", params={"status": "confirmed"})
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("Order status updated to 'confirmed'")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 9: Get Order Statistics
    print("\n9. Getting order statistics...")
    try:
        response = requests.get(f"{BASE_URL}/orders/statistics/")
        print(f"✅ Status: {response.status_code}")
        stats = response.json()
        print(f"Statistics: {stats['statistics']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 MVC CRUD API testing completed!")
    print("📖 View API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()

