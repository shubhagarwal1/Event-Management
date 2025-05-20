"""
Test script for authentication endpoints.

This script tests the authentication endpoints implemented in Day 1:
- Register
- Login
- Refresh token
- Logout
"""

import requests
import json
from datetime import datetime

# Base URL for our API
BASE_URL = "http://localhost:8000/api/v1/auth"

def test_register():
    """Test user registration endpoint."""
    print("\n===== Testing Register Endpoint =====")
    
    # Test data
    user_data = {
        "email": f"test{datetime.now().timestamp()}@example.com",
        "username": f"testuser{int(datetime.now().timestamp())}",
        "password": "testpassword123"
    }
    
    print(f"Registering user: {user_data['username']}")
    
    # Send request
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Return username for login test
    return user_data["username"], user_data["password"]

def test_login(username, password):
    """Test user login endpoint."""
    print("\n===== Testing Login Endpoint =====")
    
    # Test data
    login_data = {
        "username": username,
        "password": password
    }
    
    print(f"Logging in as: {username}")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/login", 
        data=login_data,  # Note: OAuth2 expects form data, not JSON
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Return token for refresh test
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_refresh_token(token):
    """Test token refresh endpoint."""
    print("\n===== Testing Refresh Token Endpoint =====")
    
    print("Refreshing token")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/refresh",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Return new token
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_logout(token):
    """Test logout endpoint."""
    print("\n===== Testing Logout Endpoint =====")
    
    print("Logging out")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def run_tests():
    """Run all tests in sequence."""
    try:
        # Register
        username, password = test_register()
        
        # Login
        token = test_login(username, password)
        if not token:
            print("Login failed, cannot continue tests")
            return
        
        # Refresh token
        new_token = test_refresh_token(token)
        if not new_token:
            print("Token refresh failed, using original token for logout")
            new_token = token
        
        # Logout
        test_logout(new_token)
        
        print("\n===== All tests completed =====")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Connection error. Make sure the API server is running.")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    run_tests()
