from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from db.ApiAuth import ApiToken


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, raise_unauthorized: bool = False):
        super().__init__(app)
        self.raise_unauthorized = raise_unauthorized

    async def dispatch(self, request: Request, call_next):
        token = await ApiToken.get_or_none(token=ApiToken.hash_token(request.headers.get('Authorization', '')))
        if token is None:
            request.state.user = None
            if self.raise_unauthorized:
                return JSONResponse({"detail": "Failed auth by token"}, status_code=401)

        else:
            request.state.user = await token.owner

        response = await call_next(request)
        return response
