from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
import logging

from app.core.config import settings
from app.db.session import get_db
from app.core.security import create_access_token
from app.models.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}
)

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = f"{settings.FRONTEND_URL}/api/v1/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            user_info = await oauth.google.parse_id_token(request, token)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error.error}")
    
    email = user_info.get("email")
    name = user_info.get("name", "Google User")
    
    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google")
        
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    
    if not user:
        user = User(
            email=email,
            full_name=name,
            hashed_password="",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={access_token}")

@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = f"{settings.FRONTEND_URL}/api/v1/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.github.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error.error}")
        
    resp = await oauth.github.get('user', token=token)
    profile = resp.json()
    
    email = profile.get("email")
    
    if not email:
        # Sometimes github email is private, need to fetch emails list
        emails_resp = await oauth.github.get('user/emails', token=token)
        emails = emails_resp.json()
        for e in emails:
            if e.get("primary") and e.get("verified"):
                email = e.get("email")
                break
                
    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from GitHub")
        
    name = profile.get("name") or profile.get("login") or "GitHub User"
    
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    
    if not user:
        user = User(
            email=email,
            full_name=name,
            hashed_password="",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={access_token}")
