# Phase F: Integration & End-to-End Testing Guide

## Overview

This document provides comprehensive testing procedures for validating the Todo App Phase II implementation. All tests ensure that authentication, CRUD operations, security enforcement, and data isolation work correctly end-to-end.

## Prerequisites

Before running tests, ensure:

1. **Backend is running:**
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn main:app --reload
   # Backend should be accessible at http://localhost:8000
   ```

2. **Frontend is running:**
   ```bash
   cd frontend
   npm run dev
   # Frontend should be accessible at http://localhost:3000
   ```

3. **Database is accessible:**
   - PostgreSQL/Neon database is running
   - Database URL is configured in `backend/.env`

4. **Environment variables are set:**
   - `backend/.env` contains DATABASE_URL, JWT_SECRET_KEY, etc.
   - `frontend/.env.local` contains NEXT_PUBLIC_API_URL

---

## Test F.1: CORS Configuration ✅

**Objective:** Verify that frontend can communicate with backend (CORS properly configured)

### Manual Test Steps:

1. **Open browser developer tools** (F12)
2. **Navigate to** http://localhost:3000
3. **Check console for CORS errors:**
   - ✅ PASS: No CORS-related errors
   - ❌ FAIL: Errors like "blocked by CORS policy"

### curl Test:

```bash
# Test CORS preflight request
curl -X OPTIONS http://localhost:8000/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Expected response headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Headers: Authorization, Content-Type
```

### Expected Results:

- ✅ CORS allows origin `http://localhost:3000`
- ✅ CORS allows credentials
- ✅ CORS allows required methods and headers
- ✅ OPTIONS requests return 200 OK

**Status:** CONFIGURED ✅

---

## Test F.2: End-to-End Registration Flow

**Objective:** Validate complete user registration from frontend form to database

### Test Scenario 1: Successful Registration

**Steps:**

1. Navigate to http://localhost:3000/register
2. Fill in registration form:
   - Email: `testuser@example.com`
   - Password: `TestPass123`
   - Confirm Password: `TestPass123`
3. Click "Create Account"

**Expected Results:**

- ✅ Form validates inputs (email format, password length ≥ 8 chars)
- ✅ No client-side errors displayed
- ✅ User is redirected to `/dashboard`
- ✅ Dashboard displays user email in header
- ✅ localStorage contains `jwt_token`, `user_id`, `user_email`
- ✅ Backend creates user record in database
- ✅ Password is hashed (not stored in plaintext)

**Verification Commands:**

```bash
# Check localStorage in browser console:
localStorage.getItem('jwt_token')      # Should return JWT string
localStorage.getItem('user_email')     # Should return 'testuser@example.com'

# Verify database record (backend):
# psql $DATABASE_URL -c "SELECT email, created_at FROM users WHERE email = 'testuser@example.com';"
```

### Test Scenario 2: Duplicate Email Rejection

**Steps:**

1. Navigate to http://localhost:3000/register
2. Fill in form with SAME email as before: `testuser@example.com`
3. Enter password: `AnotherPass123`
4. Confirm password: `AnotherPass123`
5. Click "Create Account"

**Expected Results:**

- ✅ Backend returns 409 Conflict
- ✅ Frontend displays error: "This email is already registered"
- ✅ User remains on registration page
- ✅ No new user created in database

### Test Scenario 3: Password Validation

**Steps:**

1. Navigate to http://localhost:3000/register
2. Enter email: `shortpass@example.com`
3. Enter password: `short` (< 8 characters)
4. Confirm password: `short`
5. Click "Create Account"

**Expected Results:**

- ✅ Frontend displays error: "Password must be at least 8 characters"
- ✅ Form submission blocked
- ✅ No API request sent

### Test Scenario 4: Password Mismatch

**Steps:**

1. Navigate to http://localhost:3000/register
2. Enter email: `mismatch@example.com`
3. Enter password: `Password123`
4. Confirm password: `Password456` (different)
5. Click "Create Account"

**Expected Results:**

- ✅ Frontend displays error: "Passwords do not match"
- ✅ Form submission blocked

---

## Test F.3: End-to-End Login and Todo CRUD

**Objective:** Validate login flow and complete todo CRUD operations

### Part 1: Login Flow

**Steps:**

1. **Logout** if currently logged in (click Logout button)
2. Navigate to http://localhost:3000 (login page)
3. Enter credentials:
   - Email: `testuser@example.com`
   - Password: `TestPass123`
4. Click "Sign In"

**Expected Results:**

- ✅ User is redirected to `/dashboard`
- ✅ Dashboard displays user email
- ✅ JWT token stored in localStorage
- ✅ Backend validates credentials
- ✅ Backend issues valid JWT token

### Part 2: Create Todo

**Steps:**

1. On dashboard, locate "Create New Todo" form
2. Fill in:
   - Title: `Buy groceries`
   - Description: `Milk, eggs, bread, and coffee`
3. Click "Create Todo"

**Expected Results:**

- ✅ Todo appears in the "Pending" section
- ✅ Todo displays correct title and description
- ✅ Todo shows "Pending" status badge
- ✅ Backend creates todo in database with `user_id` from JWT
- ✅ Form clears after creation

**Verification:**

```bash
# Check browser Network tab:
# POST /api/{user_id}/tasks
# Request Headers should include: Authorization: Bearer <token>
# Response: 201 Created with todo object
```

### Part 3: Mark Todo as Complete

**Steps:**

1. Locate the todo created above
2. Click the **checkbox** next to the todo title

**Expected Results:**

- ✅ Todo moves to "Completed" section
- ✅ Title shows strikethrough styling
- ✅ Status badge changes to "Done" (green)
- ✅ Backend updates `completed` field to `true`
- ✅ `updated_at` timestamp updates

### Part 4: Edit Todo

**Steps:**

1. Locate a todo in the list
2. Click "Edit" button
3. Change title to: `Buy groceries and cook dinner`
4. Change description to: `Milk, eggs, bread, coffee, and chicken`
5. Click "Save"

**Expected Results:**

- ✅ Todo displays updated title and description
- ✅ Edit mode exits
- ✅ Backend updates todo via PUT request
- ✅ Only provided fields are updated

### Part 5: Delete Todo

**Steps:**

1. Locate a todo in the list
2. Click "Delete" button
3. Confirm deletion in dialog

**Expected Results:**

- ✅ Confirmation dialog appears
- ✅ Todo is removed from the list
- ✅ Backend deletes todo via DELETE request
- ✅ Response: 204 No Content
- ✅ Database record is deleted

---

## Test F.4: Data Isolation Verification

**Objective:** Ensure users can only access their own todos

### Setup: Create Second User

**Steps:**

1. Logout from current user
2. Navigate to http://localhost:3000/register
3. Register new user:
   - Email: `user2@example.com`
   - Password: `SecondUser123`

**Expected Results:**

- ✅ User is registered and logged in
- ✅ Dashboard shows empty todo list (no todos from user1)

### Test Scenario 1: User 2 Creates Todo

**Steps:**

1. As `user2@example.com`, create a todo:
   - Title: `User 2 Task`
   - Description: `This belongs to user 2`

**Expected Results:**

- ✅ Todo is created and displayed
- ✅ Todo is associated with user2's `user_id`

### Test Scenario 2: Verify Isolation

**Steps:**

1. Logout from user2
2. Login as original user (`testuser@example.com`)
3. View dashboard

**Expected Results:**

- ✅ User 1 sees ONLY their own todos
- ✅ User 1 does NOT see "User 2 Task"
- ✅ Database query filters by `user_id` from JWT

### Test Scenario 3: Attempt Unauthorized Access (Security Test)

**Manual API Test:**

```bash
# Get user1's token from localStorage
USER1_TOKEN="<user1_jwt_token>"

# Get user2's ID (from localStorage or database)
USER2_ID="<user2_uuid>"

# Attempt to access user2's todos with user1's token
curl -X GET "http://localhost:8000/api/${USER2_ID}/tasks" \
  -H "Authorization: Bearer ${USER1_TOKEN}"

# Expected: 403 Forbidden
# "You can only view your own todos"
```

**Expected Results:**

- ✅ Backend rejects request with 403 Forbidden
- ✅ Path `user_id` must match JWT `user_id`
- ✅ No data from other users is returned

---

## Test F.5: Session Expiration and Re-authentication

**Objective:** Validate JWT expiration handling and automatic logout

### Test Scenario 1: JWT Expiration (15 minutes)

**Note:** JWT tokens expire after 15 minutes (configured in `backend/app/config.py`)

**Steps:**

1. Login to application
2. Wait 16 minutes (or manually set token expiration to 1 minute for testing)
3. Attempt to create a new todo

**Expected Results:**

- ✅ API returns 401 Unauthorized
- ✅ Frontend `apiClient` detects 401
- ✅ Frontend clears localStorage (`jwt_token`, `user_id`, `user_email`)
- ✅ Frontend redirects to `/` (login page)
- ✅ User sees message: "Authentication required"

### Test Scenario 2: Manual Token Removal

**Steps:**

1. While logged in to dashboard
2. Open browser console
3. Execute: `localStorage.removeItem('jwt_token')`
4. Reload the page

**Expected Results:**

- ✅ User is redirected to `/` (login page)
- ✅ Auth context detects missing token
- ✅ Dashboard is inaccessible without authentication

### Test Scenario 3: Invalid Token

**Steps:**

1. Open browser console
2. Set invalid token: `localStorage.setItem('jwt_token', 'invalid-token-string')`
3. Navigate to `/dashboard`

**Expected Results:**

- ✅ Backend rejects invalid token with 401
- ✅ Frontend clears invalid token
- ✅ User is redirected to login page

### Test Scenario 4: Logout and Re-login

**Steps:**

1. Login to application
2. Create a todo
3. Click "Logout"
4. Login again with same credentials

**Expected Results:**

- ✅ Logout clears localStorage
- ✅ Logout redirects to `/`
- ✅ Re-login issues new JWT token
- ✅ Re-login redirects to `/dashboard`
- ✅ Previously created todo is still visible

---

## Test Summary Checklist

### Authentication Tests
- [ ] CORS configuration allows frontend-backend communication
- [ ] User registration creates database record
- [ ] Duplicate email registration is rejected (409)
- [ ] Password validation enforces 8-character minimum
- [ ] Password confirmation validates match
- [ ] User login issues JWT token
- [ ] Invalid credentials are rejected (401)
- [ ] JWT token stored in localStorage
- [ ] Logout clears authentication state

### Todo CRUD Tests
- [ ] Create todo sends POST request with JWT
- [ ] Created todo displays in pending section
- [ ] Update todo (edit title/description) works
- [ ] Toggle completion updates todo status
- [ ] Delete todo removes from list (204 response)
- [ ] Empty todo list shows appropriate message

### Security & Authorization Tests
- [ ] JWT required for all todo endpoints
- [ ] Path `user_id` must match JWT `user_id` (403 if mismatch)
- [ ] Users cannot access other users' todos
- [ ] Invalid JWT tokens are rejected (401)
- [ ] Expired JWT tokens are rejected (401)
- [ ] 401 responses trigger automatic logout and redirect

### Data Isolation Tests
- [ ] User 1 cannot see User 2's todos
- [ ] User 2 cannot see User 1's todos
- [ ] Database queries filter by authenticated `user_id`
- [ ] Attempting cross-user access returns 403 Forbidden

### UI/UX Tests
- [ ] Responsive design works on mobile, tablet, desktop
- [ ] Loading states display during API calls
- [ ] Error messages are clear and helpful
- [ ] Form validation provides immediate feedback
- [ ] Optimistic UI updates (todos appear immediately)

---

## Automated Test Scripts (Future Enhancement)

For production-grade testing, consider implementing:

### Backend Tests (pytest)

```python
# tests/test_e2e_auth.py
def test_registration_flow(client):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_duplicate_email_rejection(client):
    # Register first user
    client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "Pass123"
    })
    # Attempt duplicate
    response = client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "Different123"
    })
    assert response.status_code == 409
```

### Frontend Tests (Playwright)

```typescript
// tests/e2e/registration.spec.ts
import { test, expect } from '@playwright/test';

test('registration flow', async ({ page }) => {
  await page.goto('http://localhost:3000/register');

  await page.fill('input[type="email"]', 'testuser@example.com');
  await page.fill('input[name="password"]', 'TestPass123');
  await page.fill('input[name="confirmPassword"]', 'TestPass123');
  await page.click('button:has-text("Create Account")');

  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('text=testuser@example.com')).toBeVisible();

  const token = await page.evaluate(() => localStorage.getItem('jwt_token'));
  expect(token).toBeTruthy();
});
```

---

## Test Execution Log

Record test results here:

| Test ID | Test Name | Status | Date | Notes |
|---------|-----------|--------|------|-------|
| F.1 | CORS Configuration | ⬜ | | |
| F.2.1 | Successful Registration | ⬜ | | |
| F.2.2 | Duplicate Email Rejection | ⬜ | | |
| F.2.3 | Password Validation | ⬜ | | |
| F.2.4 | Password Mismatch | ⬜ | | |
| F.3.1 | Login Flow | ⬜ | | |
| F.3.2 | Create Todo | ⬜ | | |
| F.3.3 | Complete Todo | ⬜ | | |
| F.3.4 | Edit Todo | ⬜ | | |
| F.3.5 | Delete Todo | ⬜ | | |
| F.4.1 | User Isolation | ⬜ | | |
| F.4.2 | Unauthorized Access Blocked | ⬜ | | |
| F.5.1 | JWT Expiration Handling | ⬜ | | |
| F.5.2 | Invalid Token Rejection | ⬜ | | |
| F.5.3 | Logout and Re-login | ⬜ | | |

**Legend:**
- ⬜ Not Tested
- ✅ Passed
- ❌ Failed

---

## Known Issues / Edge Cases

Document any bugs or unexpected behavior discovered during testing:

1. _To be filled during testing_
2. _To be filled during testing_

---

## Conclusion

This testing guide validates the complete Phase II implementation. All tests ensure:
- ✅ Authentication works correctly
- ✅ JWT tokens are properly managed
- ✅ CRUD operations function as expected
- ✅ Data isolation prevents unauthorized access
- ✅ Security measures are enforced

For hackathon demonstration, manual testing following this guide is sufficient. For production deployment, implement automated E2E tests using Playwright or Cypress.
