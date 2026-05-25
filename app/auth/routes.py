from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import LoginAuditLog, Operator
from app.template_helpers import flash, templates


router = APIRouter()


async def get_current_operator(request: Request, db: AsyncSession) -> Operator | None:
    operator_id = request.session.get('operator_id')
    if not operator_id:
        return None
    return await db.get(Operator, int(operator_id))


@router.get('/login', name='login')
async def login_page(request: Request, db: AsyncSession = Depends(get_db)):
    operator = await get_current_operator(request, db)
    if operator:
        return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)
    return templates.TemplateResponse('auth/login.html', {'request': request, 'current_user': None, 'errors': {}})


@router.post('/login', name='login_post')
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Operator).where(Operator.username == username))
    operator = result.scalar_one_or_none()
    ip_address = request.client.host if request.client else ''
    user_agent = request.headers.get('User-Agent', '')

    if operator and operator.check_password(password) and operator.is_active:
        request.session['operator_id'] = operator.id
        db.add(LoginAuditLog(
            operator_id=operator.id,
            attempted_username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status='SUCCESS',
        ))
        await db.commit()
        flash(request, f'Welcome back, {operator.full_name}!', 'success')
        return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)

    db.add(LoginAuditLog(
        operator_id=operator.id if operator else None,
        attempted_username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        status='FAILED_PASSWORD',
    ))
    await db.commit()
    flash(request, 'Invalid username or password.', 'danger')
    return RedirectResponse(url=request.url_for('login'), status_code=303)


@router.get('/logout', name='logout')
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    operator = await get_current_operator(request, db)
    if operator:
        flash(request, f'Goodbye, {operator.full_name}!', 'info')
    request.session.pop('operator_id', None)
    return RedirectResponse(url=request.url_for('login'), status_code=303)
