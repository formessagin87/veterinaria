from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from flask_mail import Message
from flask import abort
from app import mail
from datetime import datetime
from app.models.owner import Owner
from app.models.pet import Pet
from app.models.species import Species
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.models.breed import Breed
from flask_login import login_required, current_user
from app.models.config import ClinicConfig
from app.forms import OwnerForm, PetForm, SpeciesForm, BreedForm, AppointmentForm, MedicalRecordForm, ClinicConfigForm

main = Blueprint('main', __name__)

@main.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    config = ClinicConfig.query.first()
    if request.method == 'POST':
        config.clinic_name = request.form['clinic_name']
        config.logo_url = request.form['logo_url']
        config.primary_color = request.form['primary_color']
        config.secondary_color = request.form['secondary_color']
        config.welcome_message = request.form['welcome_message']
        db.session.commit()
        flash('Configuración actualizada correctamente.', 'success')
        return redirect(url_for('main.configuracion'))

    return render_template('configuracion.html', config=config)

@main.route('/configuracion', methods=['GET', 'POST'])
@login_required  # si tienes login
def configurar_clinica():
    config = ClinicConfig.query.first()
    if not config:
        config = ClinicConfig()
        db.session.add(config)
        db.session.commit()

    form = ClinicConfigForm(obj=config)

    if form.validate_on_submit():
        form.populate_obj(config)
        db.session.commit()
        flash('Configuración actualizada exitosamente.', 'success')
        return redirect(url_for('configurar_clinica'))

    return render_template('configuracion.html', form=form)

# Ruta principal - Dashboard
@main.route('/')
@login_required
def index():
    return render_template('index.html', 
        owners_count=Owner.query.count(), 
        pets_count=Pet.query.count(), 
        upcoming_appointments_count=Appointment.query.filter(Appointment.date >= datetime.now()).count(), 
        title="Dashboard"
    )

# Rutas para dueños
@main.route('/owners', methods=['GET', 'POST'])
@login_required
def list_owners():
    search_query = request.form.get('search', '').strip() if request.method == 'POST' else ''
    owners = Owner.search(search_query) if search_query else Owner.query.all()
    return render_template('list_owners.html', owners=owners, title="Lista de Dueños")

@main.route('/owner/new', methods=['GET', 'POST'])
@login_required
def add_owner():
    form = OwnerForm()
    if form.validate_on_submit():
        # Validaciones de unicidad
        if Owner.query.filter_by(name=form.name.data).first():
            flash('Ya existe un dueño con ese nombre.', 'danger')
        elif Owner.query.filter_by(phone=form.phone.data).first():
            flash('Ya existe un dueño con ese número de teléfono.', 'danger')
        elif Owner.query.filter_by(email=form.email.data).first():
            flash('Ya existe un dueño con ese correo electrónico.', 'danger')
        else:
            new_owner = Owner(name=form.name.data, phone=form.phone.data, email=form.email.data)
            db.session.add(new_owner)
            db.session.commit()
            flash('Dueño agregado correctamente.', 'success')
            return redirect(url_for('main.list_owners'))

    return render_template('add_owner.html', form=form, title="Agregar Dueño")



@main.route('/owner/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_owner(id):
    owner = Owner.query.get_or_404(id)
    form = OwnerForm(obj=owner)
    if form.validate_on_submit():
        form.populate_obj(owner)
        db.session.commit()
        flash('Dueño actualizado correctamente.', 'success')
        return redirect(url_for('main.list_owners'))
    return render_template('edit_owner.html', form=form, owner=owner, title="Editar Dueño")


@main.route('/owner/delete/<int:id>')
@login_required
def delete_owner(id):
    owner = Owner.query.get_or_404(id)
    db.session.delete(owner)
    db.session.commit()
    flash('Dueño eliminado correctamente.', 'success')
    return redirect(url_for('main.list_owners'))

# Rutas para mascotas
@main.route('/pet/new/<int:owner_id>', methods=['GET', 'POST'])
@login_required
def add_pet(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    form = PetForm()

    # Opción por defecto para species
    species_choices = [(0, 'Selecciona una especie')] + [(s.id, s.name) for s in Species.query.all()]
    form.species_id.choices = species_choices

    # Detectar especie seleccionada
    selected_species_id = None
    if form.species_id.data and form.species_id.data != 0:
        selected_species_id = form.species_id.data
    elif request.method == 'POST':
        selected_species_id = request.form.get('species_id', type=int)

    # Opción por defecto para breed
    if selected_species_id:
        breed_choices = [(0, 'Selecciona una raza')] + [
            (b.id, b.name) for b in Breed.query.filter_by(species_id=selected_species_id).all()
        ]
        form.breed_id.choices = breed_choices
    else:
        form.breed_id.choices = [(0, 'Selecciona una raza')]

    if form.validate_on_submit():
        if form.species_id.data == 0 or form.breed_id.data == 0:
            flash('Debe seleccionar una especie y una raza válidas.', 'danger')
        else:
            pet = Pet(
                name=form.name.data,
                birth_date=form.birth_date.data,
                species_id=form.species_id.data,
                breed_id=form.breed_id.data,
                owner_id=owner_id
            )
            db.session.add(pet)
            db.session.commit()
            flash('Mascota agregada correctamente.', 'success')
            return redirect(url_for('main.owner_detail', id=owner_id))

    return render_template('add_pet.html', form=form, owner=owner, title="Agregar Mascota")



@main.route('/pet/edit/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = PetForm(obj=pet)
    form.species_id.choices = [(s.id, s.name) for s in Species.query.all()]
    form.breed_id.choices = [(b.id, b.name) for b in Breed.query.all()]
    if form.validate_on_submit():
        form.populate_obj(pet)
        db.session.commit()
        flash('Mascota actualizada correctamente.', 'success')
        return redirect(url_for('main.pet_detail', pet_id=pet.id))
    return render_template('edit_pet.html', form=form, pet=pet, title="Editar Mascota")

@main.route('/pet/delete/<int:pet_id>')
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    owner_id = pet.owner_id
    db.session.delete(pet)
    db.session.commit()
    flash('Mascota eliminada correctamente.', 'success')
    return redirect(url_for('main.owner_detail', id=owner_id))

@main.route('/pet/<int:pet_id>')
@login_required
def pet_detail(pet_id):
    return render_template('pet_detail.html', pet=Pet.query.get_or_404(pet_id), title="Detalle de Mascota")

# Rutas para citas
@main.route('/appointment/new/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_appointment(pet_id):
    form = AppointmentForm()
    pet = Pet.query.get_or_404(pet_id)

    # Establece solo la opción actual en el select (para mantener compatibilidad con el form)
    form.pet_id.choices = [(pet.id, pet.name)]
    form.pet_id.data = pet.id  # preselecciona el valor

    if form.validate_on_submit():
        appointment = Appointment(
            date=form.date.data,
            reason=form.reason.data,
            pet_id=pet.id
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Cita registrada correctamente.', 'success')
        return redirect(url_for('main.pet_detail', pet_id=pet.id))

    return render_template('add_appointment.html', form=form, pet=pet, title="Agregar Cita")




@main.route('/appointment/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm(obj=appointment)

    # Asegúrate de cargar los choices ANTES de validar
    form.pet_id.choices = [(p.id, p.name) for p in Pet.query.all()]

    if form.validate_on_submit():
        form.populate_obj(appointment)
        db.session.commit()
        flash('Cita actualizada correctamente.', 'success')
        return redirect(url_for('main.appointments'))

    return render_template('edit_appointment.html', form=form, title="Editar Cita", appointment=appointment)



@main.route('/appointment/delete/<int:appointment_id>')
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    pet_id = appointment.pet_id
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('main.pet_detail', pet_id=pet_id))

# Rutas para registros médicos
@main.route('/medical_record/new/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_medical_record(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = MedicalRecordForm()
    if form.validate_on_submit():
        record = MedicalRecord(
            date=form.date.data,
            description=form.description.data,
            pet_id=pet_id
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=pet_id))
    # Establecer el pet_id manualmente si es GET
    form.pet_id.data = pet_id
    return render_template('add_medical_record.html', form=form, pet=pet, title="Agregar Registro Médico")



@main.route('/medical_record/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_medical_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    form = MedicalRecordForm(obj=record)
    form.pet_id.choices = [(p.id, p.name) for p in Pet.query.all()]

    if form.validate_on_submit():
        form.populate_obj(record)
        db.session.commit()
        flash('Registro médico actualizado correctamente.', 'success')
        return redirect(url_for('main.pet_detail', pet_id=record.pet_id))

    return render_template(
        'edit_medical_record.html',
        form=form,
        title="Editar Registro Médico",
        record=record  # ✅ Esta línea es la clave
    )


@main.route('/medical_record/delete/<int:record_id>')
@login_required
def delete_medical_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    pet_id = record.pet_id
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('main.pet_detail', pet_id=pet_id))

# Rutas para especies
@main.route('/species', methods=['GET', 'POST'])
@login_required
def list_species():
    species = Species.query.all()
    return render_template('species_list.html', species=species, title="Lista de Especies")

@main.route('/species/new', methods=['GET', 'POST'])
@login_required
def add_species():
    form = SpeciesForm()
    if form.validate_on_submit():
        db.session.add(Species(name=form.name.data))
        db.session.commit()
        flash('Especie agregada correctamente.', 'success')
        return redirect(url_for('main.list_species'))
    return render_template('add_species.html', form=form, title="Agregar Especie")

@main.route('/species/edit/<int:species_id>', methods=['GET', 'POST'])
@login_required
def edit_species(species_id):
    species = Species.query.get_or_404(species_id)
    form = SpeciesForm(obj=species)
    if form.validate_on_submit():
        form.populate_obj(species)
        db.session.commit()
        flash('Especie actualizada correctamente.', 'success')
        return redirect(url_for('main.list_species'))
    return render_template('edit_species.html', form=form, title="Editar Especie", species=species)


@main.route('/species/delete/<int:species_id>')
@login_required
def delete_species(species_id):
    species = Species.query.get_or_404(species_id)
    db.session.delete(species)
    db.session.commit()
    flash('Especie eliminada correctamente.', 'success')
    return redirect(url_for('main.list_species'))

# Rutas para razas
@main.route('/breeds/by_species/<int:species_id>', methods=['GET'])
def breeds_by_species(species_id):
    species = Species.query.get_or_404(species_id)
    breeds = Breed.query.filter_by(species_id=species.id).order_by(Breed.name).all()
    return jsonify([{'id': breed.id, 'name': breed.name} for breed in breeds])

@main.route('/species/<int:species_id>/breeds')
@login_required
def list_breeds(species_id):
    species = Species.query.get_or_404(species_id)
    return render_template('breeds_list.html', species=species, title=f"Razas de {species.name}")

@main.route('/species/<int:species_id>/breeds/new', methods=['GET', 'POST'])
@login_required
def add_breed(species_id):
    species = Species.query.get_or_404(species_id)
    form = BreedForm()

    # ✅ Establece choices para evitar el error
    form.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name).all()]
    form.species_id.data = species_id  # ✅ Seteamos el valor preseleccionado

    if form.validate_on_submit():
        db.session.add(Breed(name=form.name.data, species_id=species_id))
        db.session.commit()
        return redirect(url_for('main.list_breeds', species_id=species_id))

    return render_template('add_breed.html', form=form, species=species, title="Agregar Raza")


@main.route('/breeds/edit/<int:breed_id>', methods=['GET', 'POST'])
@login_required
def edit_breed(breed_id):
    breed = Breed.query.get_or_404(breed_id)
    form = BreedForm(obj=breed)

    # ✅ Establecer los choices para species_id
    form.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name).all()]
    form.species_id.data = breed.species_id  # Asegura que el valor actual esté seleccionado

    if form.validate_on_submit():
        form.populate_obj(breed)
        db.session.commit()
        flash('Raza actualizada correctamente.', 'success')
        return redirect(url_for('main.list_breeds', species_id=breed.species_id))

    return render_template('edit_breed.html', form=form, breed=breed, title="Editar Raza")


@main.route('/breeds/delete/<int:breed_id>')
@login_required
def delete_breed(breed_id):
    breed = Breed.query.get_or_404(breed_id)
    species_id = breed.species_id
    db.session.delete(breed)
    db.session.commit()
    return redirect(url_for('main.list_breeds', species_id=species_id))

# Ruta para enviar recordatorios
@main.route('/owner/reminder/<int:id>')
@login_required
def send_reminder(id):
    owner = Owner.query.get_or_404(id)
    msg = Message(
        'Recordatorio de Cuidado de Mascotas',
        sender='formessaging87@gmail.com',
        recipients=[owner.email]
    )
    msg.body = f"Hola {owner.name},Este es un recordatorio para cuidar a tus mascotas. ¡No olvides programar su cita!"
    mail.send(msg)
    return redirect(url_for('main.index'))

# Ruta para nuevas citas globales
@main.route('/appointment/global/new', methods=['GET', 'POST'])
@login_required
def add_global_appointment():
    owners = Owner.query.all()
    if request.method == 'POST':
        new_appointment = Appointment(
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
            reason=request.form['reason'],
            pet_id=request.form['pet_id']
        )
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=new_appointment.pet_id))
    return render_template('global_appointment.html', owners=owners, title="Nueva Cita Global")

# Ruta para buscar mascotas por dueño
@main.route('/pets/by_owner/<int:owner_id>', methods=['GET'])
@login_required
def pets_by_owner(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    return jsonify([{'id': pet.id, 'name': pet.name} for pet in owner.pets])

# Ruta para administrar citas
@main.route('/appointments', methods=['GET'])
@login_required
def appointments():
    search = request.args.get('search')
    appointments = Appointment.query.join(Appointment.pet).join(Pet.owner).filter(
        Appointment.reason.ilike(f"%{search}%") |
        Pet.name.ilike(f"%{search}%") |
        Owner.name.ilike(f"%{search}%")
    ).order_by(Appointment.date).all() if search else Appointment.query.order_by(Appointment.date).all()
    return render_template('appointments.html', appointments=appointments, title="Gestión de Citas")

# Ruta de acceso solo para administradores
@main.route('/admin-only')
@login_required
def admin_only():
    if not current_user.is_admin():
        abort(403)  # Prohibido
    return render_template('admin/dashboard.html')

# Ruta para mostrar mascotas del dueño
@main.route('/owner/<int:id>')
@login_required
def owner_detail(id):
    owner = Owner.query.get_or_404(id)
    return render_template('owner_detail.html', owner=owner, title=f"Detalle de {owner.name}")
    
