from flask import Blueprint, render_template, request, redirect, url_for, jsonify
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

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    owners_count = Owner.query.count()
    pets_count = Pet.query.count()
    upcoming_appointments_count = Appointment.query.filter(Appointment.date >= datetime.now()).count()
    
    return render_template('index.html', 
                           owners_count=owners_count, 
                           pets_count=pets_count, 
                           upcoming_appointments_count=upcoming_appointments_count,
                           title="Dashboard")

@main.route('/owners', methods=['GET', 'POST'])
@login_required
def list_owners():
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        owners = Owner.search(search_query) if search_query else Owner.query.all()
    else:
        owners = Owner.query.all()

    return render_template('list_owners.html', owners=owners, title="Dueños")

@main.route('/owner/new', methods=['GET', 'POST'])
@login_required
def add_owner():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']

        new_owner = Owner(name=name, phone=phone, email=email)
        db.session.add(new_owner)
        db.session.commit()
        return redirect(url_for('main.list_owners'))

    return render_template('add_owner.html', title="Agregar Dueño")

@main.route('/owner/delete/<int:id>')
@login_required
def delete_owner(id):
    owner = Owner.query.get_or_404(id)
    db.session.delete(owner)
    db.session.commit()
    return redirect(url_for('main.list_owners'))

@main.route('/breeds/by_species/<int:species_id>', methods=['GET'])
def breeds_by_species(species_id):
    species = Species.query.get_or_404(species_id)
    # Ordena alfabéticamente por el nombre de la raza
    breeds = Breed.query.filter_by(species_id=species.id).order_by(Breed.name).all()
    breed_list = [{'id': breed.id, 'name': breed.name} for breed in breeds]
    return jsonify(breed_list)

@main.route('/admin-only')
@login_required
def admin_only():
    if not current_user.is_admin():
        abort(403)  # Prohibido
    return render_template('admin/dashboard.html')
    
# Ruta para editar un dueño
@main.route('/owner/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_owner(id):
    owner = Owner.query.get_or_404(id)
    if request.method == 'POST':
        owner.name = request.form['name']
        owner.phone = request.form['phone']
        owner.email = request.form['email']
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('edit_owner.html', owner=owner, title="Editar Dueño")

# Ruta para mostrar mascotas del dueño
@main.route('/owner/<int:id>')
@login_required
def owner_detail(id):
    owner = Owner.query.get_or_404(id)
    return render_template('owner_detail.html', owner=owner, title=f"Detalle de {owner.name}")
    
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
    msg.body = f"Hola {owner.name},\n\nEste es un recordatorio para cuidar a tus mascotas. ¡No olvides programar su cita!"
    mail.send(msg)
    return redirect(url_for('main.index'))

# Ruta para agregar una nueva mascota
@main.route('/pet/new/<int:owner_id>', methods=['GET', 'POST'])
@login_required
def add_pet(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    species = Species.query.all()  # Cargar especies
    breeds = Breed.query.all()  # Cargar razas (esto lo filtraremos después)

    if request.method == 'POST':
        name = request.form['name']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        species_id = request.form['species_id']
        breed_id = request.form['breed_id']

        new_pet = Pet(
            name=name,
            birth_date=birth_date,
            species_id=species_id,
            breed_id=breed_id,
            owner_id=owner_id
        )
        db.session.add(new_pet)
        db.session.commit()
        return redirect(url_for('main.owner_detail', id=owner_id))

    return render_template('add_pet.html', owner=owner, species=species, breeds=breeds, title="Agregar Mascota")

# Ruta para editar una mascota
@main.route('/pet/edit/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    species = Species.query.all()  # Cargar especies
    breeds = Breed.query.all()  # Cargar razas

    if request.method == 'POST':
        pet.name = request.form['name']
        pet.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        pet.species_id = request.form['species_id']
        pet.breed_id = request.form['breed_id']
        pet.observations = request.form.get('observations', None)
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=pet.id))

    return render_template('edit_pet.html', pet=pet, species=species, breeds=breeds, title="Editar Mascota")

# Ruta para eliminar una mascota
@main.route('/pet/delete/<int:pet_id>')
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    owner_id = pet.owner_id
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('main.owner_detail', id=owner_id))
   
@main.route('/appointment/global/new', methods=['GET'])
@login_required
def new_global_appointment():
    owners = Owner.query.all()  # Se envían los dueños para el dropdown
    return render_template('global_appointment.html', owners=owners, title="Nueva Cita Global")

@main.route('/appointment/global/new', methods=['POST'])
@login_required
def add_global_appointment():
    owner_id = request.form['owner_id']
    pet_id = request.form['pet_id']
    date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
    reason = request.form['reason']
    
    new_appointment = Appointment(date=date, reason=reason, pet_id=pet_id)
    db.session.add(new_appointment)
    db.session.commit()
    return redirect(url_for('main.pet_detail', pet_id=pet_id))
    
@main.route('/pets/by_owner/<int:owner_id>', methods=['GET'])
@login_required
def pets_by_owner(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    pets = owner.pets  # Asumiendo que la relación está definida en el modelo Owner
    pet_list = [{'id': pet.id, 'name': pet.name} for pet in pets]
    return jsonify(pet_list)

@main.route('/appointments', methods=['GET'])
@login_required
def appointments():
    search = request.args.get('search')
    if search:
        # Ejemplo de filtrado: buscar por motivo, nombre del paciente o del dueño
        appointments = Appointment.query.join(Appointment.pet).join(Pet.owner).filter(
            Appointment.reason.ilike(f"%{search}%") |
            Pet.name.ilike(f"%{search}%") |
            Owner.name.ilike(f"%{search}%")
        ).order_by(Appointment.date).all()
    else:
        appointments = Appointment.query.order_by(Appointment.date).all()
    return render_template('appointments.html', appointments=appointments, title="Gestión de Citas")
    
# Ruta para agregar una cita
@main.route('/appointment/new/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_appointment(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
        reason = request.form['reason']

        new_appointment = Appointment(
            date=date,
            reason=reason,
            pet_id=pet_id
        )
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=pet_id))
    return render_template('add_appointment.html', pet=pet, title="Agregar Cita")

# Ruta para editar una cita
@main.route('/appointment/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
        appointment.reason = request.form['reason']
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=appointment.pet_id))
    return render_template('edit_appointment.html', appointment=appointment, title="Editar Cita")

# Ruta para cancelar una cita
@main.route('/appointment/delete/<int:appointment_id>')
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    pet_id = appointment.pet_id
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('main.pet_detail', pet_id=pet_id))

# Ruta para detalle de mascota
@main.route('/pet/<int:pet_id>')
@login_required
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pet_detail.html', pet=pet, title=f"Detalle de {pet.name}")

# Ruta para agregar registro medico
@main.route('/medical_record/new/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_medical_record(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        description = request.form['description']

        new_record = MedicalRecord(
            date=date,
            description=description,
            pet_id=pet_id
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=pet_id))
    return render_template('add_medical_record.html', pet=pet, title="Agregar Registro Médico")

# Ruta para editar registro medico
@main.route('/medical_record/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_medical_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        record.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        record.description = request.form['description']
        db.session.commit()
        return redirect(url_for('main.pet_detail', pet_id=record.pet_id))
    return render_template('edit_medical_record.html', record=record, title="Editar Registro Médico")

# Ruta para eliminar registro medico
@main.route('/medical_record/delete/<int:record_id>')
@login_required
def delete_medical_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    pet_id = record.pet_id
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('main.pet_detail', pet_id=pet_id))

# Listar todas las especies
@main.route('/species')
@login_required
def list_species():
    species = Species.query.all()
    return render_template('species_list.html', species=species, title="Especies")

# Agregar una nueva especie
@main.route('/species/new', methods=['GET', 'POST'])
@login_required
def add_species():
    if request.method == 'POST':
        name = request.form['name']
        new_species = Species(name=name)
        db.session.add(new_species)
        db.session.commit()
        return redirect(url_for('main.list_species'))
    return render_template('add_species.html', title="Agregar Especie")

# Editar una especie existente
@main.route('/species/edit/<int:species_id>', methods=['GET', 'POST'])
@login_required
def edit_species(species_id):
    species = Species.query.get_or_404(species_id)
    if request.method == 'POST':
        species.name = request.form['name']
        db.session.commit()
        return redirect(url_for('main.list_species'))
    return render_template('edit_species.html', species=species, title="Editar Especie")

# Eliminar una especie
@main.route('/species/delete/<int:species_id>')
@login_required
def delete_species(species_id):
    species = Species.query.get_or_404(species_id)
    db.session.delete(species)
    db.session.commit()
    return redirect(url_for('main.list_species'))

# Listar las razas de una especie
@main.route('/species/<int:species_id>/breeds')
@login_required
def list_breeds(species_id):
    species = Species.query.get_or_404(species_id)
    return render_template('breeds_list.html', species=species, title=f"Razas de {species.name}")

# Agregar una nueva raza
@main.route('/species/<int:species_id>/breeds/new', methods=['GET', 'POST'])
@login_required
def add_breed(species_id):
    species = Species.query.get_or_404(species_id)
    if request.method == 'POST':
        name = request.form['name']
        new_breed = Breed(name=name, species_id=species_id)
        db.session.add(new_breed)
        db.session.commit()
        return redirect(url_for('main.list_breeds', species_id=species_id))
    return render_template('add_breed.html', species=species, title="Agregar Raza")

# Editar una raza existente
@main.route('/breeds/edit/<int:breed_id>', methods=['GET', 'POST'])
@login_required
def edit_breed(breed_id):
    breed = Breed.query.get_or_404(breed_id)
    if request.method == 'POST':
        breed.name = request.form['name']
        db.session.commit()
        return redirect(url_for('main.list_breeds', species_id=breed.species_id))
    return render_template('edit_breed.html', breed=breed, title="Editar Raza")

# Eliminar una raza
@main.route('/breeds/delete/<int:breed_id>')
@login_required
def delete_breed(breed_id):
    breed = Breed.query.get_or_404(breed_id)
    species_id = breed.species_id
    db.session.delete(breed)
    db.session.commit()
    return redirect(url_for('main.list_breeds', species_id=species_id))
