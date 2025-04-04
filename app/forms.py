# app/forms.py

from wtforms.fields import DateTimeLocalField
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField, 
    DateField, SelectField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp, Optional, ValidationError, URL, Optional
)
from app.models.user import User  # Asegurar que User está importado para validaciones

class ClinicConfigForm(FlaskForm):
    clinic_name = StringField('Nombre de la Clínica', validators=[DataRequired()])
    logo_url = StringField('URL del Logo', validators=[Optional(), URL()])
    primary_color = StringField('Color Primario (Hex)', validators=[Optional()])
    secondary_color = StringField('Color Secundario (Hex)', validators=[Optional()])
    welcome_message = StringField('Mensaje de Bienvenida', validators=[Optional()])
    submit = SubmitField('Guardar')

# Diccionario básico de países y reglas
VALID_PHONE_RULES = {
    '+503': 8,  # El Salvador
    '+52': 10,  # México
    '+57': 10,  # Colombia
    '+1': 10,   # USA/Canadá
    '+54': 10,  # Argentina
    '+55': 10,  # Brasil
    # puedes agregar más
}

def validate_phone_by_country(form, field):
    phone = field.data.strip().replace(' ', '').replace('-', '')
    matched = False
    for code, length in VALID_PHONE_RULES.items():
        if phone.startswith(code):
            number_without_code = phone[len(code):]
            if not number_without_code.isdigit():
                raise ValidationError('El número después del código de país solo debe tener dígitos.')
            if len(number_without_code) != length:
                raise ValidationError(f'El número debe tener {length} dígitos después del código {code}.')
            matched = True
            break
    if not matched:
        raise ValidationError('Debe incluir un código de país válido, como +503 para El Salvador.')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', 
        validators=[
            DataRequired(message="El nombre de usuario es obligatorio."),
            Length(min=3, max=64, message="Debe tener entre 3 y 64 caracteres."),
            Regexp(r'^[a-zA-Z0-9_]+$', message="Solo puede contener letras, números y guiones bajos.")
        ]
    )
    email = StringField('Email', 
        validators=[
            DataRequired(message="El email es obligatorio."),
            Email(message="Ingrese un email válido."),
            Length(max=120, message="No puede exceder los 120 caracteres.")
        ]
    )
    phone = StringField('Teléfono', 
        validators=[
            DataRequired(message="El teléfono es obligatorio."),
            validate_phone_by_country
        ]
    )
    password = PasswordField('Contraseña', 
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, max=128, message="Debe tener entre 6 y 128 caracteres."),
            Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]+$', 
                   message="Debe contener al menos una letra y un número.")
        ]
    )
    confirm_password = PasswordField('Confirmar Contraseña', 
        validators=[
            DataRequired(message="Debe confirmar la contraseña."),
            EqualTo('password', message="Las contraseñas deben coincidir.")
        ]
    )
    submit = SubmitField('Registrarse')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este correo electrónico ya está registrado.')

class LoginForm(FlaskForm):
    username = StringField('Usuario o Email', validators=[DataRequired(message="Ingrese su usuario o email.")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="Ingrese su contraseña.")])
    submit = SubmitField('Iniciar Sesión')

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', 
        validators=[
            DataRequired(),
            Length(min=6, max=128),
            Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]+$', 
                   message="Debe contener al menos una letra y un número.")
        ]
    )
    confirm_password = PasswordField('Confirmar Nueva Contraseña', 
        validators=[
            DataRequired(),
            EqualTo('new_password', message="Las contraseñas deben coincidir.")
        ]
    )
    submit = SubmitField('Actualizar Contraseña')

class OwnerForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Teléfono', validators=[DataRequired(), validate_phone_by_country])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    submit = SubmitField('Guardar')

class PetForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    birth_date = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    observations = TextAreaField('Observaciones', validators=[Optional()])
    species_id = SelectField('Especie', coerce=int, validators=[DataRequired()])
    breed_id = SelectField('Raza', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

class AppointmentForm(FlaskForm):
    date = DateTimeLocalField('Fecha', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    reason = StringField('Motivo', validators=[DataRequired(), Length(max=200)])
    pet_id = SelectField('Mascota', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

class MedicalRecordForm(FlaskForm):
    date = DateField('Fecha', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    pet_id = HiddenField()  # Oculto
    submit = SubmitField('Guardar')

class SpeciesForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Guardar')

class BreedForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    species_id = SelectField('Especie', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

class EditUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField('Rol', choices=[('asistente', 'Asistente'), ('administrador', 'Administrador')], validators=[DataRequired()])
    submit = SubmitField('Actualizar Usuario')
