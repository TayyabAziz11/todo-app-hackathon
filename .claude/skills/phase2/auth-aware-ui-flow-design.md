# Skill: auth-aware-ui-flow-design

## 1. Skill Name
`auth-aware-ui-flow-design`

## 2. Purpose
Specify UI behavior and navigation flows based on authentication state, defining how the frontend responds to logged-in, logged-out, token-expired, and loading states to provide seamless, secure user experience.

## 3. Applicable Agents
- **nextjs-frontend-architect** (primary)
- fullstack-spec-architect (UX coordination)
- auth-security-architect (auth state requirements)

## 4. Inputs
- **Authentication States**: logged-in, logged-out, token-expired, loading, error
- **JWT Lifecycle**: Token issuance, validation, expiration, refresh
- **Protected Routes**: Pages requiring authentication
- **User Workflows**: Login, logout, session persistence, auto-logout

## 5. Outputs
- **Authentication State Machine**: All auth states and transitions
- **Route Protection Specification**: Which routes require auth
- **Redirect Rules**: Where to send users based on auth state
- **Token Storage Strategy**: localStorage vs sessionStorage vs cookies
- **Session Persistence**: Remember-me functionality, auto-login
- **Error Handling**: Expired token, invalid token, network errors

## 6. Scope & Boundaries

### In Scope
- Authentication state management (global state)
- Protected route enforcement (client-side guards)
- Login/logout flows and redirects
- Token storage and retrieval
- Session expiration handling
- Loading and error states

### Out of Scope
- OAuth provider UI flows (Phase 3)
- Multi-factor authentication UI (Phase 3+)
- Password reset flows (Phase 3)
- Email verification UI (Phase 3)

## 7. Reusability Notes
- **Phase 2**: Basic email/password authentication flows
- **Phase 3**: Extends to OAuth provider buttons, password reset
- **Phase 4**: Multi-user collaboration invitations
- **Phase 5**: AI chatbot authentication awareness

## 8. Dependencies

### Upstream Dependencies
- `jwt-auth-flow-specification` (token lifecycle)
- `api-auth-enforcement-definition` (backend auth requirements)
- Frontend routing library (Next.js App Router)

### Downstream Dependencies
- `frontend-backend-contract-alignment` (API integration)
- Frontend implementation tasks
- E2E authentication tests

## 9. Quality Expectations

### Security
- Tokens stored securely (XSS considerations)
- Expired tokens trigger logout/re-login
- Protected routes inaccessible without auth

### UX
- Seamless login/logout experience
- Clear feedback on auth errors
- Loading states prevent UI flicker
- Session persistence across page refreshes

## 10. Example Usage (Spec-Level)

### Authentication State Machine

**States:**
```
1. UNAUTHENTICATED: No token, user logged out
2. LOADING: Checking stored token validity
3. AUTHENTICATED: Valid token, user logged in
4. TOKEN_EXPIRED: Token expired, needs re-login
5. ERROR: Authentication error occurred
```

**Transitions:**
```
UNAUTHENTICATED → LOADING: Page load, check localStorage
LOADING → AUTHENTICATED: Valid token found
LOADING → UNAUTHENTICATED: No token or invalid
AUTHENTICATED → TOKEN_EXPIRED: API returns 401 expired_token
AUTHENTICATED → UNAUTHENTICATED: User clicks logout
TOKEN_EXPIRED → UNAUTHENTICATED: User acknowledges, redirects to login
ERROR → UNAUTHENTICATED: User dismisses error
```

### Route Protection Specification

**Public Routes (No Auth Required):**
```
/login - Login page
/register - Registration page
/ - Landing page (Phase 2: redirects to /login if not authenticated)
```

**Protected Routes (Auth Required):**
```
/todos - Todo list page (main app)
/profile - User profile page
```

**Route Guard Logic:**
```
On Route Access:
  1. Check auth state
  2. If UNAUTHENTICATED or TOKEN_EXPIRED:
     - Save intended destination
     - Redirect to /login
     - After login: Redirect to saved destination
  3. If AUTHENTICATED:
     - Allow access
  4. If LOADING:
     - Show loading spinner
     - Wait for auth check to complete
```

### Login Flow

**Flow Steps:**
```
1. User navigates to /login
2. User enters email and password
3. Frontend validates input (required fields, email format)
4. Frontend calls POST /api/auth/login
5. Backend validates credentials:
   - Success: Returns { access_token, user: { id, email, name } }
   - Failure: Returns 401 { error: "invalid_credentials" }
6. On success:
   - Store access_token in localStorage
   - Update auth state: AUTHENTICATED
   - Update user state: { id, email, name }
   - Redirect to /todos (or saved destination)
7. On failure:
   - Display error message: "Invalid email or password"
   - Keep user on /login page
```

### Logout Flow

**Flow Steps:**
```
1. User clicks "Logout" button
2. Frontend calls POST /api/auth/logout (optional backend call)
3. Frontend clears localStorage:
   - Remove access_token
   - Remove user data
4. Update auth state: UNAUTHENTICATED
5. Redirect to /login
6. Display message: "You have been logged out"
```

### Token Expiration Handling

**Scenario: Token Expires During Session**
```
1. User authenticated, browsing /todos
2. Token expires (15 minutes elapsed)
3. User triggers API call (e.g., GET /api/todos)
4. Backend returns 401 { error: "expired_token" }
5. Frontend interceptor catches 401:
   - Update auth state: TOKEN_EXPIRED
   - Clear localStorage (invalid token)
   - Show modal: "Your session has expired. Please log in again."
6. User clicks "Log In":
   - Save current URL (/todos)
   - Redirect to /login
7. After successful login:
   - Redirect back to /todos
   - Resume workflow
```

### Session Persistence (Page Refresh)

**Flow:**
```
1. User authenticated, navigating app
2. User refreshes page or closes/reopens browser
3. App initialization:
   - State: LOADING
   - Check localStorage for access_token
4. If token exists:
   - Decode token (client-side) to extract user info
   - Check expiration: if exp > now, token still valid
   - Update state: AUTHENTICATED
   - Update user state: { id, email, name }
   - User remains logged in
5. If no token or expired:
   - Update state: UNAUTHENTICATED
   - Redirect to /login
```

### Token Storage Strategy

**Phase 2 Choice: localStorage**
```
Storage: localStorage.setItem('access_token', token)
Retrieval: localStorage.getItem('access_token')
Removal: localStorage.removeItem('access_token')

Benefits:
  - Persists across browser sessions
  - Simple API
  - Survives page refresh

Trade-offs:
  - XSS Risk: Mitigated by Content Security Policy
  - Accessible to JavaScript (not HttpOnly)
  - Phase 3+ Alternative: HttpOnly cookies (more secure)
```

### Protected Component Pattern

**Specification:**
```
Pattern: ProtectedRoute HOC or Layout

Usage:
  - Wrap protected pages with authentication check
  - Automatically redirect unauthenticated users

Example (Conceptual):
  Page: /todos
  Component: TodosPage
  Wrapper: <ProtectedRoute><TodosPage /></ProtectedRoute>

  ProtectedRoute Logic:
    1. Check auth state
    2. If UNAUTHENTICATED: Redirect to /login
    3. If LOADING: Show loading spinner
    4. If AUTHENTICATED: Render children
```

### UI State Indicators

**Loading State:**
```
Display: Spinner or skeleton UI
Scenarios:
  - Initial page load (checking token)
  - Login button clicked (waiting for backend)
  - API calls in progress
Message: "Loading..." or "Checking authentication..."
```

**Error State:**
```
Display: Error message banner or toast
Scenarios:
  - Login failed (invalid credentials)
  - Network error during auth
  - Token validation failed
Messages:
  - "Invalid email or password"
  - "Network error. Please try again."
  - "Session expired. Please log in."
```

**Authenticated State:**
```
Display: User navbar with email and logout button
Example:
  Header: "Logged in as alice@example.com [Logout]"
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (nextjs-frontend-architect)
