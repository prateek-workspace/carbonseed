from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas, auth
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_redirect_url(role: models.UserRole) -> str:
    """Get redirect URL based on user role"""
    if role == models.UserRole.ADMIN:
        return "/admin/dashboard"
    elif role == models.UserRole.FACTORY_OWNER:
        return "/dashboard"
    elif role == models.UserRole.OPERATOR:
        return "/dashboard"
    else:  # VIEWER
        return "/dashboard"


@router.post("/login", response_model=schemas.LoginResponse)
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint for enterprise users.
    Returns JWT access token along with user details and redirect URL based on role.
    
    Roles:
    - ADMIN: Full system access, redirects to /admin/dashboard
    - FACTORY_OWNER: Factory management, redirects to /dashboard
    - OPERATOR: Operations view, redirects to /dashboard
    - VIEWER: Read-only access, redirects to /dashboard
    """
    user = auth.authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role.value}, 
        expires_delta=access_token_expires
    )
    
    # Get redirect URL based on role
    redirect_url = get_redirect_url(user.role)
    
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=schemas.UserRole(user.role.value),
            factory_id=user.factory_id,
            is_active=user.is_active,
            created_at=user.created_at
        ),
        redirect_url=redirect_url
    )


@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Get current user information.
    """
    return current_user


@router.post("/signup", response_model=schemas.User)
async def signup(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Public signup endpoint.
    Creates a new user with VIEWER role by default.
    Users can be promoted to other roles by admins later.
    """
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user with VIEWER role (default for public signup)
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=models.UserRole.VIEWER,  # Default role for public signup
        factory_id=None,  # No factory assigned initially
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/register", response_model=schemas.User)
async def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Register a new user (Admin only).
    Only admins can create new users in the system.
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can register new users"
        )
    
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Validate factory_id if provided
    if user_data.factory_id:
        factory = db.query(models.Factory).filter(
            models.Factory.id == user_data.factory_id
        ).first()
        if not factory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Factory not found"
            )
    
    # Create new user
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=models.UserRole(user_data.role.value),
        factory_id=user_data.factory_id,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.put("/users/{user_id}/role", response_model=schemas.User)
async def update_user_role(
    user_id: int,
    role: schemas.UserRole,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update a user's role (Admin only).
    Use this to manually set a user as admin or factory owner.
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update user roles"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = models.UserRole(role.value)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users", response_model=list[schemas.User])
async def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    List all users (Admin only).
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list users"
        )
    
    users = db.query(models.User).all()
    return users
