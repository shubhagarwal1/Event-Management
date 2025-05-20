"""
Comprehensive test script for authentication endpoints.

This script tests all authentication endpoints with various scenarios 
including edge cases and error conditions.
"""

import requests
import json
import time
from datetime import datetime

# Base URL for our API
BASE_URL = "http://localhost:8000/api/v1/auth"

def print_separator():
    """Print a separator line."""
    print("=" * 60)

def test_register_success():
    """Test successful user registration."""
    print_separator()
    print("TEST: Register - Success Case")
    
    # Create unique identifiers for test
    timestamp = int(datetime.now().timestamp())
    email = f"test{timestamp}@example.com"
    username = f"testuser{timestamp}"
    
    # Test data
    user_data = {
        "email": email,
        "username": username,
        "password": "TestPassword123"
    }
    
    print(f"Registering user: {username}")
    
    # Send request
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Assert expected results
    assert response.status_code == 201, "Expected status code 201"
    assert response.json()["username"] == username, "Username mismatch"
    assert response.json()["email"] == email, "Email mismatch"
    assert "id" in response.json(), "ID missing in response"
    
    print("✅ Test passed")
    
    # Return credentials for subsequent tests
    return username, "TestPassword123", email

def test_register_duplicate_username(username):
    """Test registration with duplicate username."""
    print_separator()
    print("TEST: Register - Duplicate Username")
    
    # Create unique email but use existing username
    timestamp = int(datetime.now().timestamp())
    email = f"test{timestamp}_new@example.com"
    
    # Test data
    user_data = {
        "email": email,
        "username": username,  # Using existing username
        "password": "TestPassword123"
    }
    
    print(f"Attempting to register duplicate username: {username}")
    
    # Send request
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code != 200 and response.status_code != 201:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error content: {response.text}")
    
    # We expect an error because username should be unique
    assert response.status_code >= 400, "Expected error status code"
    
    print("✅ Test passed - Server rejected duplicate username")

def test_register_duplicate_email(email):
    """Test registration with duplicate email."""
    print_separator()
    print("TEST: Register - Duplicate Email")
    
    # Create unique username but use existing email
    timestamp = int(datetime.now().timestamp())
    username = f"testuser{timestamp}_new"
    
    # Test data
    user_data = {
        "email": email,  # Using existing email
        "username": username,
        "password": "TestPassword123"
    }
    
    print(f"Attempting to register duplicate email: {email}")
    
    # Send request
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code != 200 and response.status_code != 201:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error content: {response.text}")
    
    # We expect an error because email should be unique
    assert response.status_code >= 400, "Expected error status code"
    
    print("✅ Test passed - Server rejected duplicate email")

def test_register_invalid_password():
    """Test registration with invalid password (too short)."""
    print_separator()
    print("TEST: Register - Invalid Password")
    
    # Create unique identifiers for test
    timestamp = int(datetime.now().timestamp())
    email = f"test{timestamp}@example.com"
    username = f"testuser{timestamp}"
    
    # Test data with short password
    user_data = {
        "email": email,
        "username": username,
        "password": "short"  # Too short, should be rejected
    }
    
    print(f"Registering with invalid password (too short)")
    
    # Send request
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code != 200 and response.status_code != 201:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error content: {response.text}")
    
    # We expect an error because password is too short
    assert response.status_code >= 400, "Expected error status code"
    
    print("✅ Test passed - Server rejected invalid password")

def test_login_success(username, password):
    """Test successful login."""
    print_separator()
    print("TEST: Login - Success Case")
    
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
    
    # Assert expected results
    assert response.status_code == 200, "Expected status code 200"
    assert "access_token" in response.json(), "Access token missing in response"
    assert response.json()["token_type"] == "bearer", "Token type should be bearer"
    
    print("✅ Test passed")
    
    # Return token for subsequent tests
    return response.json()["access_token"]

def test_login_wrong_password(username):
    """Test login with wrong password."""
    print_separator()
    print("TEST: Login - Wrong Password")
    
    # Test data with wrong password
    login_data = {
        "username": username,
        "password": "WrongPassword123"
    }
    
    print(f"Attempting login with wrong password for: {username}")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error content: {response.text}")
    
    # We expect an error because password is wrong
    assert response.status_code == 401, "Expected 401 Unauthorized"
    
    print("✅ Test passed - Server rejected invalid credentials")

def test_login_nonexistent_user():
    """Test login with non-existent user."""
    print_separator()
    print("TEST: Login - Non-existent User")
    
    # Test data with non-existent user
    login_data = {
        "username": f"nonexistent_user_{int(time.time())}",
        "password": "TestPassword123"
    }
    
    print(f"Attempting login with non-existent user: {login_data['username']}")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error content: {response.text}")
    
    # We expect an error because user doesn't exist
    assert response.status_code == 401, "Expected 401 Unauthorized"
    
    print("✅ Test passed - Server rejected invalid credentials")

def test_refresh_token_success(token):
    """Test successful token refresh."""
    print_separator()
    print("TEST: Refresh Token - Success Case")
    
    print("Refreshing token")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/refresh",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Assert expected results
    assert response.status_code == 200, "Expected status code 200"
    assert "access_token" in response.json(), "Access token missing in response"
    assert response.json()["token_type"] == "bearer", "Token type should be bearer"
    
    print("✅ Test passed")
    
    # Return new token
    return response.json()["access_token"]

def test_refresh_token_invalid():
    """Test token refresh with invalid token."""
    print_separator()
    print("TEST: Refresh Token - Invalid Token")
    
    # Invalid token
    invalid_token = "invalid.token.signature"
    
    print("Attempting to refresh with invalid token")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/refresh",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error content: {response.text}")
    
    # We expect an error because token is invalid
    assert response.status_code == 401, "Expected 401 Unauthorized"
    
    print("✅ Test passed - Server rejected invalid token")

def test_logout(token):
    """Test logout."""
    print_separator()
    print("TEST: Logout")
    
    print("Logging out")
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Print result
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Assert expected results
    assert response.status_code == 200, "Expected status code 200"
    assert "message" in response.json(), "Message missing in response"
    
    print("✅ Test passed")

def run_all_tests():
    """Run all authentication tests."""
    try:
        print("\n🔒 STARTING COMPREHENSIVE AUTHENTICATION TESTS 🔒\n")
        
        # Test registration
        username, password, email = test_register_success()
        
        # Test duplicate registration
        test_register_duplicate_username(username)
        test_register_duplicate_email(email)
        
        # Test invalid password
        test_register_invalid_password()
        
        # Test login
        token = test_login_success(username, password)
        test_login_wrong_password(username)
        test_login_nonexistent_user()
        
        # Test token refresh
        new_token = test_refresh_token_success(token)
        test_refresh_token_invalid()
        
        # Test logout
        test_logout(new_token)
        
        print_separator()
        print("🎉 ALL AUTHENTICATION TESTS COMPLETED SUCCESSFULLY 🎉")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
