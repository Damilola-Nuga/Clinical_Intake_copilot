from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ninja import Router
from ninja.errors import HttpError
from ..schema import RegisterSchema

auth_router = Router()

@auth_router.post("/register")
def register_user(request, payload: RegisterSchema):
    # Check if username already exists

    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already taken.")
    
    # Validate password
    try:
        validate_password(payload.password)
    except ValidationError as e:
        raise HttpError(400, {"password_errors": e.messages})
    
    #Create the user
    user = User.objects.create_user(username=payload.username, password=payload.password)
    user.save()

    return {
        "message": "User registered successfully.",
        "username": user.username
    }

