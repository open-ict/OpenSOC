from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = db.query(User).filter(User.email == payload.get('sub')).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


def require_role(*roles):
    def checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail='Forbidden')
        return user
    return checker
