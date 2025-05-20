"""
Test script for event endpoints.

This script tests the event-related endpoints from Day 2 implementation:
- Create event
- Read events
- Update event
- Delete event
- Event sharing
- Version history
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for our API
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"
EVENTS_URL = f"{BASE_URL}/events"

# Test user credentials
TEST_USER = {
    "email": f"testuser_{int(datetime.now().timestamp())}@example.com",
    "username": f"testuser_{int(datetime.now().timestamp())}",
    "password": "TestPassword123"
}

# Test collaborator credentials
TEST_COLLABORATOR = {
    "email": f"collaborator_{int(datetime.now().timestamp())}@example.com",
    "username": f"collaborator_{int(datetime.now().timestamp())}",
    "password": "CollabPassword123"
}

def print_separator():
    """Print a separator line."""
    print("=" * 70)

def register_user(user_data):
    """Register a test user."""
    print(f"Registering user: {user_data['username']}")
    
    response = requests.post(f"{AUTH_URL}/register", json=user_data)
    
    if response.status_code == 201:
        print(f"✅ User {user_data['username']} registered successfully")
        return response.json()
    else:
        print(f"❌ Failed to register user: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def login_user(username, password):
    """Login a user and get access token."""
    print(f"Logging in as: {username}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(
        f"{AUTH_URL}/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Login successful, token received")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def create_event(token, event_data):
    """Create a new event."""
    print(f"Creating event: {event_data['title']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        EVENTS_URL,
        json=event_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print(f"✅ Event created successfully")
        return response.json()
    else:
        print(f"❌ Failed to create event: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def get_events(token):
    """Get all events for current user."""
    print("Getting all events")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        EVENTS_URL,
        headers=headers
    )
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Got {len(events)} events")
        return events
    else:
        print(f"❌ Failed to get events: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def get_event(token, event_id):
    """Get a specific event by ID."""
    print(f"Getting event with ID: {event_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{EVENTS_URL}/{event_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Got event successfully")
        return response.json()
    else:
        print(f"❌ Failed to get event: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def update_event(token, event_id, update_data):
    """Update an event."""
    print(f"Updating event {event_id} with: {update_data}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.put(
        f"{EVENTS_URL}/{event_id}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Event updated successfully")
        return response.json()
    else:
        print(f"❌ Failed to update event: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def share_event(token, event_id, user_id, role):
    """Share an event with another user."""
    print(f"Sharing event {event_id} with user {user_id}, role: {role}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    share_data = {
        "user_id": user_id,
        "role": role
    }
    
    response = requests.post(
        f"{EVENTS_URL}/{event_id}/share",
        json=share_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Event shared successfully")
        return response.json()
    else:
        print(f"❌ Failed to share event: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def get_event_history(token, event_id):
    """Get event version history."""
    print(f"Getting history for event {event_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{EVENTS_URL}/{event_id}/changelog",
        headers=headers
    )
    
    if response.status_code == 200:
        versions = response.json()
        print(f"✅ Got {len(versions)} versions")
        return versions
    else:
        print(f"❌ Failed to get event history: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def delete_event(token, event_id):
    """Delete an event."""
    print(f"Deleting event {event_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{EVENTS_URL}/{event_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print(f"✅ Event deleted successfully")
        return True
    else:
        print(f"❌ Failed to delete event: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return False

def run_tests():
    """Run all event endpoint tests."""
    print("\n🚀 STARTING EVENT ENDPOINT TESTS 🚀\n")
    
    # Step 1: Register users
    print_separator()
    print("STEP 1: REGISTER TEST USERS")
    owner = register_user(TEST_USER)
    collaborator = register_user(TEST_COLLABORATOR)
    
    if not owner or not collaborator:
        print("❌ Failed to register test users, aborting tests")
        return
    
    # Step 2: Login users
    print_separator()
    print("STEP 2: LOGIN USERS")
    owner_token = login_user(TEST_USER["username"], TEST_USER["password"])
    collaborator_token = login_user(TEST_COLLABORATOR["username"], TEST_COLLABORATOR["password"])
    
    if not owner_token or not collaborator_token:
        print("❌ Failed to login, aborting tests")
        return
    
    # Step 3: Create an event
    print_separator()
    print("STEP 3: CREATE EVENT")
    now = datetime.now()
    event_data = {
        "title": "Test Event",
        "description": "This is a test event created by the test script",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=2)).isoformat(),
        "location": "Virtual Meeting",
        "is_recurring": False
    }
    
    event = create_event(owner_token, event_data)
    
    if not event:
        print("❌ Failed to create event, aborting tests")
        return
    
    event_id = event["id"]
    print(f"Created event with ID: {event_id}")
    
    # Step 4: Get all events
    print_separator()
    print("STEP 4: GET ALL EVENTS")
    events = get_events(owner_token)
    
    if not events:
        print("❌ Failed to get events, aborting tests")
        return
    
    # Step 5: Get specific event
    print_separator()
    print("STEP 5: GET SPECIFIC EVENT")
    event_detail = get_event(owner_token, event_id)
    
    if not event_detail:
        print("❌ Failed to get event detail, aborting tests")
        return
    
    print(f"Event details: {json.dumps(event_detail, indent=2)}")
    
    # Step 6: Update event
    print_separator()
    print("STEP 6: UPDATE EVENT")
    update_data = {
        "title": "Updated Test Event",
        "description": "This event has been updated"
    }
    
    updated_event = update_event(owner_token, event_id, update_data)
    
    if not updated_event:
        print("❌ Failed to update event, aborting tests")
        return
    
    print(f"Updated event: {json.dumps(updated_event, indent=2)}")
    
    # Step 7: Share event with collaborator
    print_separator()
    print("STEP 7: SHARE EVENT")
    share_result = share_event(owner_token, event_id, collaborator["id"], "editor")
    
    if not share_result:
        print("❌ Failed to share event, aborting tests")
        return
    
    # Step 8: Collaborator views the shared event
    print_separator()
    print("STEP 8: COLLABORATOR VIEWS SHARED EVENT")
    collab_view = get_event(collaborator_token, event_id)
    
    if not collab_view:
        print("❌ Collaborator failed to view shared event, aborting tests")
        return
    
    print(f"Collaborator can view the event: {json.dumps(collab_view, indent=2)}")
    
    # Step 9: Get event history
    print_separator()
    print("STEP 9: GET EVENT HISTORY")
    history = get_event_history(owner_token, event_id)
    
    if not history:
        print("❌ Failed to get event history, aborting tests")
        return
    
    print(f"Event has {len(history)} versions")
    
    # Step 10: Delete event
    print_separator()
    print("STEP 10: DELETE EVENT")
    delete_result = delete_event(owner_token, event_id)
    
    if not delete_result:
        print("❌ Failed to delete event")
    
    print_separator()
    print("🎉 EVENT ENDPOINT TESTS COMPLETED 🎉")

if __name__ == "__main__":
    run_tests()
