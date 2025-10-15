
from ninja import NinjaAPI
from ninja_extra import exceptions
from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router
from ninja_jwt.routers.blacklist import blacklist_router

#Import your routers
from api.endpoints.auth import auth_router
from api.endpoints.sessions import router as sessions_router


api = NinjaAPI()


api.add_router('/auth', auth_router, tags=["Auth"])
api.add_router('/token', obtain_pair_router, tags=["Auth"])
api.add_router('/token/verify', verify_router, tags=["Auth"])
api.add_router('/token/blacklist', blacklist_router, tags=["Auth"])

api.add_router('', sessions_router, tags=["Sessions"])



def api_exception_handler(request, exc):
    """Unified format for errors."""
    if isinstance(exc.detail, (list, dict)):
        data = exc.detail
    else:
        data = {"detail": exc.detail}

    return api.create_response(request, data, status=exc.status_code)

api.exception_handler(exceptions.APIException)(api_exception_handler)