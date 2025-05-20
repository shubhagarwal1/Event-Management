"""
Integration test script for Collaborative Event Management System.

This script tests the integration between Day 1 (Authentication) and Day 2 (Events/Collaboration) 
implementations, demonstrating a complete user flow from registration to event collaboration.
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys
from typing import Dict, Any, Optional, List, Tuple

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"
EVENTS_URL = f"{BASE_URL}/events"

class IntegrationTest:
    """
    Integration test class that follows SOLID principles with single responsibility
    for each method and proper separation of concerns.
    """
    
    def __init__(self):
        """Initialize test data and results storage."""
        self.admin = None
        self.organizer = None
        self.participant = None
        self.admin_token = None
        self.organizer_token = None
        self.participant_token = None
        self.event_id = None
        self.test_results = []
    
    def run_all_tests(self):
        """Run all integration tests in sequence."""
        print("\n🔄 RUNNING INTEGRATION TESTS FOR EVENT MANAGEMENT SYSTEM 🔄\n")
        
        try:
            # Step 1: Setup users
            self.setup_users()
            
            # Step 2: Login users
            self.login_users()
            
            # Step 3: Create event
            self.create_event()
            
            # Step 4: Event operations
            self.test_event_operations()
            
            # Step 5: Collaboration
            self.test_collaboration()
            
            # Step 6: Versioning
            self.test_versioning()
            
            # Step 7: Permission changes
            self.test_permission_changes()
            
            # Step 8: Cleanup
            self.cleanup()
            
            # Print results
            self.print_results()
            
        except Exception as e:
            print(f"❌ Test execution failed: {str(e)}")
            sys.exit(1)
    
    def record_result(self, test_name: str, success: bool, message: str):
        """Record test result with details."""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
        if success:
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")
    
    def setup_users(self):
        """Register test users with different roles."""
        print("\n📋 STEP 1: REGISTERING USERS\n")
        
        # Register admin user
        self.admin = self.register_user({
            "email": f"admin_{int(time.time())}@example.com",
            "username": f"admin_{int(time.time())}",
            "password": "AdminPass123"
        })
        
        # Register organizer
        self.organizer = self.register_user({
            "email": f"organizer_{int(time.time())}@example.com",
            "username": f"organizer_{int(time.time())}",
            "password": "OrganizerPass123"
        })
        
        # Register participant
        self.participant = self.register_user({
            "email": f"participant_{int(time.time())}@example.com",
            "username": f"participant_{int(time.time())}",
            "password": "ParticipantPass123"
        })
        
        if self.admin and self.organizer and self.participant:
            self.record_result(
                "User Registration", 
                True, 
                f"All users registered successfully: Admin ID={self.admin['id']}, "
                f"Organizer ID={self.organizer['id']}, Participant ID={self.participant['id']}"
            )
        else:
            self.record_result(
                "User Registration", 
                False, 
                "Failed to register all users"
            )
            sys.exit(1)
    
    def login_users(self):
        """Login all users and get tokens."""
        print("\n🔑 STEP 2: LOGGING IN USERS\n")
        
        # Login as admin
        self.admin_token = self.login_user(self.admin["username"], "AdminPass123")
        
        # Login as organizer
        self.organizer_token = self.login_user(self.organizer["username"], "OrganizerPass123")
        
        # Login as participant
        self.participant_token = self.login_user(self.participant["username"], "ParticipantPass123")
        
        if self.admin_token and self.organizer_token and self.participant_token:
            self.record_result(
                "User Authentication", 
                True, 
                "All users authenticated successfully"
            )
        else:
            self.record_result(
                "User Authentication", 
                False, 
                "Failed to authenticate all users"
            )
            sys.exit(1)
    
    def create_event(self):
        """Create a test event as organizer."""
        print("\n📅 STEP 3: CREATING EVENT\n")
        
        now = datetime.now()
        event_data = {
            "title": "Integration Test Event",
            "description": "This event tests the integration between Day 1 and Day 2 features",
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat(),
            "location": "Virtual Meeting Room",
            "is_recurring": False
        }
        
        response = requests.post(
            EVENTS_URL,
            json=event_data,
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 201:
            event = response.json()
            self.event_id = event["id"]
            self.record_result(
                "Event Creation", 
                True, 
                f"Event created successfully with ID {self.event_id}"
            )
        else:
            self.record_result(
                "Event Creation", 
                False, 
                f"Failed to create event: {response.status_code}"
            )
            try:
                print(response.json())
            except:
                print(response.text)
            sys.exit(1)
    
    def test_event_operations(self):
        """Test basic event operations."""
        print("\n🔄 STEP 4: TESTING EVENT OPERATIONS\n")
        
        # Get all events for organizer
        response = requests.get(
            EVENTS_URL,
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 200:
            events = response.json()
            if len(events) > 0 and any(e["id"] == self.event_id for e in events):
                self.record_result(
                    "List Events", 
                    True, 
                    f"Successfully retrieved events list containing event {self.event_id}"
                )
            else:
                self.record_result(
                    "List Events", 
                    False, 
                    "Event list does not contain our created event"
                )
        else:
            self.record_result(
                "List Events", 
                False, 
                f"Failed to list events: {response.status_code}"
            )
        
        # Get specific event
        response = requests.get(
            f"{EVENTS_URL}/{self.event_id}",
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 200:
            event = response.json()
            if event["id"] == self.event_id:
                self.record_result(
                    "Get Event Detail", 
                    True, 
                    f"Successfully retrieved event {self.event_id}"
                )
            else:
                self.record_result(
                    "Get Event Detail", 
                    False, 
                    "Retrieved wrong event"
                )
        else:
            self.record_result(
                "Get Event Detail", 
                False, 
                f"Failed to get event: {response.status_code}"
            )
        
        # Update event
        update_data = {
            "title": "Updated Integration Test Event",
            "description": "This event has been updated during integration testing"
        }
        
        response = requests.put(
            f"{EVENTS_URL}/{self.event_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 200:
            updated_event = response.json()
            if (updated_event["title"] == update_data["title"] and 
                updated_event["description"] == update_data["description"]):
                self.record_result(
                    "Update Event", 
                    True, 
                    "Successfully updated event"
                )
            else:
                self.record_result(
                    "Update Event", 
                    False, 
                    "Event not updated correctly"
                )
        else:
            self.record_result(
                "Update Event", 
                False, 
                f"Failed to update event: {response.status_code}"
            )
    
    def test_collaboration(self):
        """Test collaboration and permission features."""
        print("\n👥 STEP 5: TESTING COLLABORATION\n")
        
        # Share event with participant as editor
        share_data = {
            "user_id": self.participant["id"],
            "role": "editor"
        }
        
        response = requests.post(
            f"{EVENTS_URL}/{self.event_id}/share",
            json=share_data,
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 200:
            self.record_result(
                "Share Event", 
                True, 
                f"Successfully shared event with participant as editor"
            )
        else:
            self.record_result(
                "Share Event", 
                False, 
                f"Failed to share event: {response.status_code}"
            )
            return
        
        # Participant views shared event
        response = requests.get(
            f"{EVENTS_URL}/{self.event_id}",
            headers={"Authorization": f"Bearer {self.participant_token}"}
        )
        
        if response.status_code == 200:
            event = response.json()
            permissions_found = False
            
            for permission in event.get("permissions", []):
                if permission["user_id"] == self.participant["id"] and permission["role"] == "editor":
                    permissions_found = True
                    break
            
            if permissions_found:
                self.record_result(
                    "View Shared Event", 
                    True, 
                    "Participant can view shared event with correct permissions"
                )
            else:
                self.record_result(
                    "View Shared Event", 
                    False, 
                    "Participant permissions not correctly displayed"
                )
        else:
            self.record_result(
                "View Shared Event", 
                False, 
                f"Participant cannot view shared event: {response.status_code}"
            )
        
        # Participant updates event
        update_data = {
            "description": "This event has been updated by participant"
        }
        
        response = requests.put(
            f"{EVENTS_URL}/{self.event_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.participant_token}"}
        )
        
        if response.status_code == 200:
            updated_event = response.json()
            if updated_event["description"] == update_data["description"]:
                self.record_result(
                    "Update as Collaborator", 
                    True, 
                    "Participant successfully updated event as editor"
                )
            else:
                self.record_result(
                    "Update as Collaborator", 
                    False, 
                    "Event not updated correctly by participant"
                )
        else:
            self.record_result(
                "Update as Collaborator", 
                False, 
                f"Participant failed to update event: {response.status_code}"
            )
    
    def test_versioning(self):
        """Test event versioning features."""
        print("\n📚 STEP 6: TESTING VERSION HISTORY\n")
        
        # Get event changelog
        response = requests.get(
            f"{EVENTS_URL}/{self.event_id}/changelog",
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 200:
            versions = response.json()
            if len(versions) >= 3:  # Initial + organizer update + participant update
                self.record_result(
                    "Version History", 
                    True, 
                    f"Event has {len(versions)} versions in history as expected"
                )
                
                # If we have at least 2 versions, test diff
                if len(versions) >= 2:
                    # Get version 1
                    v1_id = versions[-1]["version"]  # Oldest version
                    v2_id = versions[0]["version"]   # Newest version
                    
                    response = requests.get(
                        f"{EVENTS_URL}/{self.event_id}/diff/{v1_id}/{v2_id}",
                        headers={"Authorization": f"Bearer {self.organizer_token}"}
                    )
                    
                    if response.status_code == 200:
                        diff = response.json()
                        if "diff" in diff and len(diff["diff"]) > 0:
                            self.record_result(
                                "Version Diff", 
                                True, 
                                f"Successfully retrieved diff between versions {v1_id} and {v2_id}"
                            )
                        else:
                            self.record_result(
                                "Version Diff", 
                                False, 
                                "Diff contains no changes"
                            )
                    else:
                        self.record_result(
                            "Version Diff", 
                            False, 
                            f"Failed to get diff: {response.status_code}"
                        )
            else:
                self.record_result(
                    "Version History", 
                    False, 
                    f"Expected at least 3 versions, but found {len(versions)}"
                )
        else:
            self.record_result(
                "Version History", 
                False, 
                f"Failed to get version history: {response.status_code}"
            )
    
    def test_permission_changes(self):
        """Test changing permissions and permission enforcement."""
        print("\n🔒 STEP 7: TESTING PERMISSION CHANGES\n")
        
        # Change participant role to viewer
        update_data = {
            "role": "viewer"
        }
        
        response = requests.put(
            f"{EVENTS_URL}/{self.event_id}/permissions/{self.participant['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 200:
            self.record_result(
                "Change Role", 
                True, 
                "Changed participant role from editor to viewer"
            )
        else:
            self.record_result(
                "Change Role", 
                False, 
                f"Failed to change participant role: {response.status_code}"
            )
            return
        
        # Participant tries to update (should fail)
        update_data = {
            "title": "Unauthorized Update by Viewer"
        }
        
        response = requests.put(
            f"{EVENTS_URL}/{self.event_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.participant_token}"}
        )
        
        if response.status_code == 403:
            self.record_result(
                "Permission Enforcement", 
                True, 
                "Viewer correctly prevented from updating event"
            )
        else:
            self.record_result(
                "Permission Enforcement", 
                False, 
                f"Viewer incorrectly allowed to update event (status {response.status_code})"
            )
        
        # Participant still can view event
        response = requests.get(
            f"{EVENTS_URL}/{self.event_id}",
            headers={"Authorization": f"Bearer {self.participant_token}"}
        )
        
        if response.status_code == 200:
            self.record_result(
                "Viewer Access", 
                True, 
                "Viewer can still view the event"
            )
        else:
            self.record_result(
                "Viewer Access", 
                False, 
                f"Viewer cannot view event: {response.status_code}"
            )
        
        # Remove participant's access entirely
        response = requests.delete(
            f"{EVENTS_URL}/{self.event_id}/permissions/{self.participant['id']}",
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 204:
            self.record_result(
                "Remove Access", 
                True, 
                "Successfully removed participant's access"
            )
        else:
            self.record_result(
                "Remove Access", 
                False, 
                f"Failed to remove participant's access: {response.status_code}"
            )
            return
        
        # Participant tries to view event (should fail)
        response = requests.get(
            f"{EVENTS_URL}/{self.event_id}",
            headers={"Authorization": f"Bearer {self.participant_token}"}
        )
        
        if response.status_code == 403:
            self.record_result(
                "Access Removal", 
                True, 
                "Participant correctly prevented from viewing event after access removal"
            )
        else:
            self.record_result(
                "Access Removal", 
                False, 
                f"Participant incorrectly allowed to view event after access removal (status {response.status_code})"
            )
    
    def cleanup(self):
        """Clean up test data."""
        print("\n🧹 STEP 8: CLEANUP\n")
        
        # Delete event
        response = requests.delete(
            f"{EVENTS_URL}/{self.event_id}",
            headers={"Authorization": f"Bearer {self.organizer_token}"}
        )
        
        if response.status_code == 204:
            self.record_result(
                "Event Deletion", 
                True, 
                f"Successfully deleted event {self.event_id}"
            )
        else:
            self.record_result(
                "Event Deletion", 
                False, 
                f"Failed to delete event: {response.status_code}"
            )
    
    def print_results(self):
        """Print test results summary."""
        total = len(self.test_results)
        passed = sum(1 for result in self.test_results if result["success"])
        failed = total - passed
        
        print("\n📊 TEST RESULTS SUMMARY 📊")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"- {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"- {result['test']}")
        
        print("\n" + "="*70)
        if failed == 0:
            print("🎉 ALL INTEGRATION TESTS PASSED! 🎉")
        else:
            print(f"⚠️ {failed} TEST(S) FAILED ⚠️")
        print("="*70 + "\n")
    
    def register_user(self, user_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Register a user and return user data if successful."""
        response = requests.post(f"{AUTH_URL}/register", json=user_data)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to register {user_data['username']}: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return None
    
    def login_user(self, username: str, password: str) -> Optional[str]:
        """Login a user and return token if successful."""
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
            return response.json().get("access_token")
        else:
            print(f"Failed to login {username}: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return None

# Run the integration tests if executed directly
if __name__ == "__main__":
    test = IntegrationTest()
    test.run_all_tests()
