from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.auth import UserCreate, UserLogin, UserResponse, Token, UserUpdate, PasswordChange
from utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        hashed = hash_password(user_data.password)
        db_user = User(email=user_data.email, hashed_password=hashed, full_name=user_data.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
        return {"access_token": token, "token_type": "bearer", "user": db_user}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        token = create_access_token({"sub": user.email, "user_id": user.id})
        return {"access_token": token, "token_type": "bearer", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me", response_model=UserResponse)
def update_me(update_data: UserUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if update_data.full_name:
            user.full_name = update_data.full_name
        if update_data.email and update_data.email != user.email:
            existing = db.query(User).filter(User.email == update_data.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
            user.email = update_data.email
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me/password")
def change_password(pwd_data: PasswordChange, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(pwd_data.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        if len(pwd_data.new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
        user.hashed_password = hash_password(pwd_data.new_password)
        db.commit()
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me")
def delete_account(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"message": "Account deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
