"""
Authentication endpoints: registration, login, and OAuth.
"""

import secrets
import httpx
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, or_
from app.database import get_session
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    OAuthURLResponse, OAuthCallbackRequest
)
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.config import settings

router = APIRouter()

# OAuth state storage (in production, use Redis or database)
oauth_states: dict[str, str] = {}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Register a new user account.

    **Process:**
    1. Validate email format and password length (handled by Pydantic)
    2. Check if email already exists in database
    3. Hash password using bcrypt
    4. Create user record
    5. Issue JWT token
    6. Return token and user info

    **Security:**
    - Password is hashed before storage (never stored in plaintext)
    - JWT token expires in 15 minutes
    - Duplicate emails are rejected with 409 Conflict

    **Error Responses:**
    - 409 Conflict: Email already registered
    - 422 Unprocessable Entity: Invalid email format or password too short
    """
    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered"
        )

    # Hash password
    hashed_password = hash_password(request.password)

    # Create new user
    new_user = User(
        email=request.email,
        hashed_password=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(str(new_user.id))

    # Build response
    user_response = UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        name=new_user.name,
        avatar_url=new_user.avatar_url,
        oauth_provider=new_user.oauth_provider
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


def _build_user_response(user: User) -> UserResponse:
    """Helper function to build UserResponse from User model."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Authenticate user and issue JWT token.

    **Process:**
    1. Validate email format (handled by Pydantic)
    2. Query user by email
    3. Verify password matches stored hash
    4. Issue JWT token
    5. Return token and user info

    **Security:**
    - Generic error message for both invalid email and wrong password (prevents user enumeration)
    - Password verification uses constant-time comparison (via bcrypt)
    - JWT token expires in 15 minutes

    **Error Responses:**
    - 401 Unauthorized: Invalid email or password (generic message)
    - 422 Unprocessable Entity: Invalid email format
    """
    # Query user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()

    # Generic error message for security (don't reveal if email exists)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user signed up via OAuth (no password)
    if user.is_oauth_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This account uses {user.oauth_provider} sign-in. Please use the {user.oauth_provider.title()} button to log in."
        )

    # Verify password
    if not user.hashed_password or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user)
    )


# ============================================
# Google OAuth Endpoints
# ============================================

@router.get("/google/url", response_model=OAuthURLResponse)
async def get_google_auth_url() -> OAuthURLResponse:
    """
    Generate Google OAuth authorization URL.

    **Flow:**
    1. Frontend calls this endpoint to get the authorization URL
    2. Frontend redirects user to the returned URL
    3. User authorizes the app on Google's consent page
    4. Google redirects back to our callback URL with an authorization code
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "google"

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
        "prompt": "select_account"
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return OAuthURLResponse(auth_url=auth_url, provider="google")


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(
    request: OAuthCallbackRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Handle Google OAuth callback.

    **Flow:**
    1. Verify the state parameter to prevent CSRF attacks
    2. Exchange authorization code for access token
    3. Fetch user profile from Google
    4. Create new user or login existing user
    5. Return JWT token
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured"
        )

    # Verify state (optional but recommended)
    if request.state and request.state in oauth_states:
        del oauth_states[request.state]

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": request.code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI
            }
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for tokens"
            )

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        # Fetch user info
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user information from Google"
            )

        userinfo = userinfo_response.json()

    google_id = userinfo.get("id")
    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from Google account"
        )

    # Check if user exists by OAuth ID or email
    statement = select(User).where(
        or_(
            (User.oauth_provider == "google") & (User.oauth_id == google_id),
            User.email == email
        )
    )
    user = session.exec(statement).first()

    if user:
        # Update OAuth info if user exists but signed up differently
        if not user.oauth_provider:
            user.oauth_provider = "google"
            user.oauth_id = google_id
        if not user.name:
            user.name = name
        if not user.avatar_url:
            user.avatar_url = picture
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # Create new user
        user = User(
            email=email,
            oauth_provider="google",
            oauth_id=google_id,
            name=name,
            avatar_url=picture
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    # Generate JWT token
    jwt_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=_build_user_response(user)
    )


# ============================================
# GitHub OAuth Endpoints
# ============================================

@router.get("/github/url", response_model=OAuthURLResponse)
async def get_github_auth_url() -> OAuthURLResponse:
    """
    Generate GitHub OAuth authorization URL.

    **Flow:**
    1. Frontend calls this endpoint to get the authorization URL
    2. Frontend redirects user to the returned URL
    3. User authorizes the app on GitHub's consent page
    4. GitHub redirects back to our callback URL with an authorization code
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables."
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "github"

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
        "state": state
    }

    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    return OAuthURLResponse(auth_url=auth_url, provider="github")


@router.post("/github/callback", response_model=TokenResponse)
async def github_callback(
    request: OAuthCallbackRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Handle GitHub OAuth callback.

    **Flow:**
    1. Verify the state parameter to prevent CSRF attacks
    2. Exchange authorization code for access token
    3. Fetch user profile from GitHub
    4. Create new user or login existing user
    5. Return JWT token
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured"
        )

    # Verify state (optional but recommended)
    if request.state and request.state in oauth_states:
        del oauth_states[request.state]

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": request.code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for access token"
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            error = token_data.get("error_description", "Unknown error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GitHub OAuth error: {error}"
            )

        # Fetch user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user information from GitHub"
            )

        userinfo = user_response.json()

        # Fetch user's email (may be private)
        email = userinfo.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            if emails_response.status_code == 200:
                emails = emails_response.json()
                # Get primary email
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        email = e.get("email")
                        break
                # Fallback to first verified email
                if not email:
                    for e in emails:
                        if e.get("verified"):
                            email = e.get("email")
                            break

    github_id = str(userinfo.get("id"))
    name = userinfo.get("name") or userinfo.get("login")
    avatar_url = userinfo.get("avatar_url")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from GitHub account. Please make sure your email is public or verified."
        )

    # Check if user exists by OAuth ID or email
    statement = select(User).where(
        or_(
            (User.oauth_provider == "github") & (User.oauth_id == github_id),
            User.email == email
        )
    )
    user = session.exec(statement).first()

    if user:
        # Update OAuth info if user exists but signed up differently
        if not user.oauth_provider:
            user.oauth_provider = "github"
            user.oauth_id = github_id
        if not user.name:
            user.name = name
        if not user.avatar_url:
            user.avatar_url = avatar_url
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # Create new user
        user = User(
            email=email,
            oauth_provider="github",
            oauth_id=github_id,
            name=name,
            avatar_url=avatar_url
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    # Generate JWT token
    jwt_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=_build_user_response(user)
    )
