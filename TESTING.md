# Collaborative Event Management System - Testing Guide

This document provides a comprehensive testing guide for the Collaborative Event Management System, organized by functional areas.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Day 1: Authentication Testing](#day-1-authentication-testing)
- [Day 2: Event Management Testing](#day-2-event-management-testing)
- [Collaboration Features Testing](#collaboration-features-testing)
- [Versioning Features Testing](#versioning-features-testing)
- [Permission Testing](#permission-testing)
- [Cleanup](#cleanup)
- [Automated Testing](#automated-testing)

## Prerequisites

Ensure the server is running:

```bash
source venv/bin/activate && uvicorn app.main:app --reload
```

The server will be available at: `http://localhost:8000`

For easy access to the API documentation, visit: `http://localhost:8000/docs`

## Day 1: Authentication Testing

### Register Users

```bash
# Register an admin user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "AdminPassword123"
  }'

# Register an organizer
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizer@example.com",
    "username": "organizer",
    "password": "OrganizerPass123"
  }'

# Register a participant
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "participant@example.com",
    "username": "participant",
    "password": "ParticipantPass123"
  }'
```

Expected response (status 201):
```json
{
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "id": 1
}
```

### Login and Get Tokens

```bash
# Login as organizer
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=organizer&password=OrganizerPass123"

# Login as participant
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=participant&password=ParticipantPass123"

# Save the returned tokens (replace with actual tokens)
ORGANIZER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
PARTICIPANT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
PARTICIPANT_ID=3  # The user ID of the participant (from registration response)
```

Expected response (status 200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Test Token Refresh

```bash
# Refresh the organizer token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Test Logout

```bash
# Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 200):
```json
{
  "message": "Successfully logged out"
}
```

## Day 2: Event Management Testing

### Create an Event

```bash
# Create an event as organizer
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ORGANIZER_TOKEN" \
  -d '{
    "title": "Team Planning Meeting",
    "description": "Quarterly planning session",
    "start_time": "2025-06-15T10:00:00+05:30",
    "end_time": "2025-06-15T12:00:00+05:30",
    "location": "Conference Room A",
    "is_recurring": false
  }'

# Save the returned event ID
EVENT_ID=1
```

Expected response (status 201):
```json
{
  "id": 1,
  "title": "Team Planning Meeting",
  "description": "Quarterly planning session",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": null,
  "version": 1
}
```

### Get Event Details

```bash
# Get all events (as organizer)
curl -X GET http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"

# Get specific event details
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response for list (status 200):
```json
[
  {
    "id": 1,
    "title": "Team Planning Meeting",
    "description": "Quarterly planning session",
    "start_time": "2025-06-15T10:00:00+05:30",
    "end_time": "2025-06-15T12:00:00+05:30",
    "location": "Conference Room A",
    "is_recurring": false,
    "recurrence_pattern": "none",
    "recurrence_rule": null,
    "owner_id": 2,
    "created_at": "2025-05-20T10:00:00+05:30",
    "updated_at": null,
    "version": 1
  }
]
```

Expected response for detail (status 200):
```json
{
  "id": 1,
  "title": "Team Planning Meeting",
  "description": "Quarterly planning session",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": null,
  "version": 1,
  "permissions": []
}
```

### Update Event

```bash
# Update event as organizer
curl -X PUT http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ORGANIZER_TOKEN" \
  -d '{
    "title": "Updated Team Planning Meeting",
    "description": "Quarterly planning session with department heads"
  }'
```

Expected response (status 200):
```json
{
  "id": 1,
  "title": "Updated Team Planning Meeting",
  "description": "Quarterly planning session with department heads",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": "2025-05-20T10:10:00+05:30",
  "version": 2
}
```

## Collaboration Features Testing

### Share Event

```bash
# Share event with participant as editor
curl -X POST http://localhost:8000/api/v1/events/$EVENT_ID/share \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ORGANIZER_TOKEN" \
  -d '{
    "user_id": '$PARTICIPANT_ID',
    "role": "editor"
  }'
```

Expected response (status 200):
```json
{
  "id": 1,
  "user_id": 3,
  "role": "editor",
  "created_at": "2025-05-20T10:15:00+05:30",
  "updated_at": null
}
```

### Test Participant Access

```bash
# Participant views the shared event
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Authorization: Bearer $PARTICIPANT_TOKEN"

# Participant updates the event (as editor)
curl -X PUT http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PARTICIPANT_TOKEN" \
  -d '{
    "description": "Quarterly planning session updated by participant"
  }'
```

Expected response for view (status 200):
```json
{
  "id": 1,
  "title": "Updated Team Planning Meeting",
  "description": "Quarterly planning session with department heads",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": "2025-05-20T10:10:00+05:30",
  "version": 2,
  "permissions": [
    {
      "id": 1,
      "user_id": 3,
      "role": "editor",
      "created_at": "2025-05-20T10:15:00+05:30",
      "updated_at": null
    }
  ]
}
```

Expected response for update (status 200):
```json
{
  "id": 1,
  "title": "Updated Team Planning Meeting",
  "description": "Quarterly planning session updated by participant",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": "2025-05-20T10:20:00+05:30",
  "version": 3
}
```

## Versioning Features Testing

```bash
# Get event version history
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID/changelog \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 200):
```json
[
  {
    "id": 3,
    "version": 3,
    "changed_by_id": 3,
    "created_at": "2025-05-20T10:20:00+05:30",
    "change_description": "Description updated"
  },
  {
    "id": 2,
    "version": 2,
    "changed_by_id": 2,
    "created_at": "2025-05-20T10:10:00+05:30",
    "change_description": "Title changed from 'Team Planning Meeting' to 'Updated Team Planning Meeting'; Description updated"
  },
  {
    "id": 1,
    "version": 1,
    "changed_by_id": 2,
    "created_at": "2025-05-20T10:00:00+05:30",
    "change_description": "Initial creation"
  }
]
```

```bash
# Compare versions (version IDs may vary)
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID/diff/1/3 \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 200):
```json
{
  "version1": 1,
  "version2": 3,
  "diff": {
    "title": {
      "version1": "Team Planning Meeting",
      "version2": "Updated Team Planning Meeting"
    },
    "description": {
      "version1": "Quarterly planning session",
      "version2": "Quarterly planning session updated by participant"
    }
  }
}
```

```bash
# View a specific version
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID/history/1 \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 200):
```json
{
  "id": 1,
  "version": 1,
  "data": {
    "id": 1,
    "title": "Team Planning Meeting",
    "description": "Quarterly planning session",
    "start_time": "2025-06-15T10:00:00+05:30",
    "end_time": "2025-06-15T12:00:00+05:30",
    "location": "Conference Room A",
    "is_recurring": false,
    "recurrence_pattern": "none",
    "recurrence_rule": null,
    "owner_id": 2,
    "version": 1,
    "created_at": "2025-05-20T10:00:00+05:30",
    "updated_at": null
  },
  "changed_by_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "change_description": "Initial creation"
}
```

```bash
# Rollback to a previous version
curl -X POST http://localhost:8000/api/v1/events/$EVENT_ID/rollback/1 \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 200):
```json
{
  "id": 1,
  "title": "Team Planning Meeting",
  "description": "Quarterly planning session",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": "2025-05-20T10:30:00+05:30",
  "version": 4
}
```

## Permission Testing

```bash
# Change participant's role from editor to viewer
curl -X PUT http://localhost:8000/api/v1/events/$EVENT_ID/permissions/$PARTICIPANT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ORGANIZER_TOKEN" \
  -d '{
    "role": "viewer"
  }'
```

Expected response (status 200):
```json
{
  "id": 1,
  "user_id": 3,
  "role": "viewer",
  "created_at": "2025-05-20T10:15:00+05:30",
  "updated_at": "2025-05-20T10:40:00+05:30"
}
```

```bash
# Participant tries to update as viewer (should fail)
curl -X PUT http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PARTICIPANT_TOKEN" \
  -d '{
    "title": "This update should be rejected"
  }'
```

Expected response (status 403):
```json
{
  "detail": "Not enough permissions to edit this event"
}
```

```bash
# Participant can still view event
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Authorization: Bearer $PARTICIPANT_TOKEN"
```

Expected response (status 200):
```json
{
  "id": 1,
  "title": "Team Planning Meeting",
  "description": "Quarterly planning session",
  "start_time": "2025-06-15T10:00:00+05:30",
  "end_time": "2025-06-15T12:00:00+05:30",
  "location": "Conference Room A",
  "is_recurring": false,
  "recurrence_pattern": "none",
  "recurrence_rule": null,
  "owner_id": 2,
  "created_at": "2025-05-20T10:00:00+05:30",
  "updated_at": "2025-05-20T10:30:00+05:30",
  "version": 4,
  "permissions": [
    {
      "id": 1,
      "user_id": 3,
      "role": "viewer",
      "created_at": "2025-05-20T10:15:00+05:30",
      "updated_at": "2025-05-20T10:40:00+05:30"
    }
  ]
}
```

```bash
# Remove participant's permission entirely
curl -X DELETE http://localhost:8000/api/v1/events/$EVENT_ID/permissions/$PARTICIPANT_ID \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 204, no content)

```bash
# Participant tries to view event (should fail)
curl -X GET http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Authorization: Bearer $PARTICIPANT_TOKEN"
```

Expected response (status 403):
```json
{
  "detail": "Not enough permissions to view this event"
}
```

## Cleanup

```bash
# Delete the event
curl -X DELETE http://localhost:8000/api/v1/events/$EVENT_ID \
  -H "Authorization: Bearer $ORGANIZER_TOKEN"
```

Expected response (status 204, no content)

## Automated Testing

For more comprehensive automated testing, use the included `integration_test.py` script:

```bash
source venv/bin/activate && python integration_test.py
```

This script will automatically:
1. Register test users
2. Authenticate and obtain tokens
3. Create and manage events
4. Test collaboration features
5. Test versioning
6. Test permission enforcement
7. Clean up after testing

### Shell Script for Testing

You can also create a shell script with these curl commands to automate testing:

```bash
#!/bin/bash

# Start the API server in a separate terminal window first:
# source venv/bin/activate && uvicorn app.main:app --reload

# Register users
echo "Registering users..."
ADMIN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "AdminPassword123"
  }')
ADMIN_ID=$(echo $ADMIN | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

ORGANIZER=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizer@example.com",
    "username": "organizer",
    "password": "OrganizerPass123"
  }')
ORGANIZER_ID=$(echo $ORGANIZER | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

PARTICIPANT=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "participant@example.com",
    "username": "participant",
    "password": "ParticipantPass123"
  }')
PARTICIPANT_ID=$(echo $PARTICIPANT | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "Created users: Admin=$ADMIN_ID, Organizer=$ORGANIZER_ID, Participant=$PARTICIPANT_ID"

# Get tokens
echo "Getting tokens..."
ORGANIZER_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=organizer&password=OrganizerPass123" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

PARTICIPANT_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=participant&password=ParticipantPass123" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Got tokens"

# Create an event
echo "Creating event..."
EVENT=$(curl -s -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ORGANIZER_TOKEN" \
  -d '{
    "title": "Team Planning Meeting",
    "description": "Quarterly planning session",
    "start_time": "2025-06-15T10:00:00+05:30",
    "end_time": "2025-06-15T12:00:00+05:30",
    "location": "Conference Room A",
    "is_recurring": false
  }')
EVENT_ID=$(echo $EVENT | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "Created event ID: $EVENT_ID"

# Continue with other tests...
# ...

echo "Testing complete!"
```

Save this as `test.sh` and run it with:

```bash
chmod +x test.sh
./test.sh
```
