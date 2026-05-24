from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from app.models import db, Operator, LoginAuditLog
from app.auth.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle operator login"""
    if current_user.is_authenticated:
        return redirect(url_for('upload.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # Query operator by username
        operator = Operator.query.filter_by(username=username).first()
        
        # Check credentials
        if operator and operator.check_password(password) and operator.is_active:
            # Successful login
            login_user(operator)
            
            # Log successful login
            audit_log = LoginAuditLog(
                operator_id=operator.id,
                attempted_username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status='SUCCESS'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            flash(f'Welcome back, {operator.full_name}!', 'success')
            return redirect(url_for('upload.dashboard'))
        else:
            # Failed login
            operator_id = operator.id if operator else None
            status = 'FAILED_PASSWORD' if operator else 'FAILED_PASSWORD'
            
            audit_log = LoginAuditLog(
                operator_id=operator_id,
                attempted_username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status
            )
            db.session.add(audit_log)
            db.session.commit()
            
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Handle operator logout"""
    if current_user.is_authenticated:
        flash(f'Goodbye, {current_user.full_name}!', 'info')
        logout_user()
    
    return redirect(url_for('auth.login'))
