from fastapi import HTTPException
from starlette.requests import Request
from oauth import oauth
from user import User
from typing import Optional

def authenticated(request: Request):
    if oauth and 'user' not in request.session:
        raise HTTPException(status_code=401, detail='Please login!')


def authenticated_user(request: Request) -> Optional[User]:
    if oauth and 'user' in request.session:
        return User(request.session.get('user'))
    return None