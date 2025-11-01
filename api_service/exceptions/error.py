from fastapi import HTTPException, status

class APIError(Exception):
    pass

class DatabaseError(APIError):
    def to_http(self):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(self))

class AuthError(APIError):
    def to_http(self):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(self))

class ForbiddenError(APIError):
    def to_http(self):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(self))