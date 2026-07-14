import secrets
import httpx
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Setting
from app.schemas.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefresh,
    PasswordResetRequest, PasswordReset, TwoFactorVerify,
)
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, generate_totp_secret,
    get_totp_uri, verify_totp, generate_totp_qr,
)
from app.api.deps.auth import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()

    user_settings = Setting(user_id=user.id)
    db.add(user_settings)

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login = datetime.now(timezone.utc)

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_access_token = create_access_token({"sub": user.id})
    new_refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if name:
        current_user.name = name
    return current_user


@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user:
        import secrets
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(data: PasswordReset, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.password_reset_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user.password_hash = hash_password(data.password)
    user.password_reset_token = None
    user.password_reset_expires = None

    return {"message": "Password reset successfully"}


@router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email_verification_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    user.email_verified = True
    user.email_verification_token = None
    return {"message": "Email verified successfully"}


# ── Google OAuth ────────────────────────────────────────────────────────────

@router.get("/google/login")
async def google_login():
    redirect_uri = quote(f"{settings.FRONTEND_URL}/api/v1/auth/google/callback", safe="")
    url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=openid%20email%20profile&"
        "access_type=offline"
    )
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    redirect_uri = f"{settings.FRONTEND_URL}/api/v1/auth/google/callback"
    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://oauth2.googleapis.com/token", data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Google OAuth failed")

        tokens = token_res.json()
        userinfo_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        if userinfo_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Google user info")

        info = userinfo_res.json()
        email = info.get("email")
        name = info.get("name", email.split("@")[0])
        google_id = info.get("id")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            name=name,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            google_id=google_id,
            email_verified=True,
        )
        db.add(user)
        await db.flush()
        user_settings = Setting(user_id=user.id)
        db.add(user_settings)

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}")


# ── GitHub OAuth ────────────────────────────────────────────────────────────

@router.get("/github/login")
async def github_login():
    url = (
        "https://github.com/login/oauth/authorize?"
        f"client_id={settings.GITHUB_CLIENT_ID}&"
        f"redirect_uri={settings.FRONTEND_URL}/api/v1/auth/github/callback&"
        "scope=read:user%20user:email"
    )
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            }
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub OAuth failed")

        tokens = token_res.json()
        userinfo_res = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "Accept": "application/json",
            }
        )
        if userinfo_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get GitHub user info")

        info = userinfo_res.json()
        github_id = str(info["id"])
        name = info.get("name") or info.get("login")
        email = info.get("email")

        if not email:
            emails_res = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            emails = emails_res.json()
            primary = next((e for e in emails if e.get("primary")), {})
            email = primary.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="No email found from GitHub")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            name=name,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            github_id=github_id,
            email_verified=True,
        )
        db.add(user)
        await db.flush()
        user_settings = Setting(user_id=user.id)
        db.add(user_settings)

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}")


@router.post("/2fa/enable")
async def enable_2fa(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    secret = generate_totp_secret()
    current_user.two_factor_secret = secret

    uri = get_totp_uri(secret, current_user.email)
    qr_code = generate_totp_qr(uri)

    return {"secret": secret, "qr_code": qr_code, "uri": uri}


@router.post("/2fa/verify")
async def verify_2fa(
    data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA not set up")

    if verify_totp(current_user.two_factor_secret, data.code):
        current_user.two_factor_enabled = True
        return {"message": "2FA enabled successfully"}

    raise HTTPException(status_code=400, detail="Invalid 2FA code")


@router.post("/2fa/disable")
async def disable_2fa(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    return {"message": "2FA disabled successfully"}
