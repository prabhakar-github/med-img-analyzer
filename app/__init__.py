from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.auth.routes import router as auth_router
from app.config import settings
from app.upload.routes import router as upload_router


def create_app():
    app = FastAPI(title='DICOM-AI Upload System', debug=settings.DEBUG)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        https_only=settings.SESSION_COOKIE_SECURE,
        same_site=settings.SESSION_COOKIE_SAMESITE,
        max_age=settings.PERMANENT_SESSION_LIFETIME,
    )

    app.include_router(auth_router, prefix='/auth')
    app.include_router(upload_router, prefix='/upload')

    @app.get('/', name='index')
    async def index(request: Request):
        if request.session.get('operator_id'):
            return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)
        return RedirectResponse(url=request.url_for('login'), status_code=303)

    return app


app = create_app()
