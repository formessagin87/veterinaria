from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from app.forms import RegistrationForm, LoginForm, UpdatePasswordForm

auth = Blueprint('auth', __name__, template_folder='templates/auth')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data.strip()
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email, role='asistente')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title="Registro", form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("Formulario validado ✅")
        username_or_email = form.username.data.strip()
        password = form.password.data.strip()
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user:
            print("Usuario encontrado:", user.username)
            if user.check_password(password):
                print("Contraseña correcta 🔐")
                login_user(user)
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('main.index'))
            else:
                print("Contraseña incorrecta ❌")
        else:
            print("Usuario no encontrado ❌")
        flash('Credenciales incorrectas', 'danger')
    else:
        print("Formulario no válido ❌")
        print(form.errors)
    return render_template('auth/login.html', title="Login", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data.strip()
        new_password = form.new_password.data.strip()
        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('auth.update_password'))
        current_user.set_password(new_password)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada.', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/update_password.html', title="Actualizar Contraseña", form=form)
