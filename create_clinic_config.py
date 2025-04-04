# create_clinic_config.py

from app import create_app, db
from app.models.config import ClinicConfig

app = create_app()

with app.app_context():
    config = ClinicConfig.query.first()

    if config:
        print(f"⚠️ Ya existe una configuración registrada para la clínica: {config.clinic_name}")
        choice = input("¿Deseas actualizarla? (s/n): ").strip().lower()

        if choice == 's':
            config.clinic_name = input(f"Nombre de la clínica [{config.clinic_name}]: ") or config.clinic_name
            config.logo_url = input(f"URL del logo [{config.logo_url}]: ") or config.logo_url
            config.primary_color = input(f"Color primario (hex) [{config.primary_color}]: ") or config.primary_color
            config.secondary_color = input(f"Color secundario (hex) [{config.secondary_color}]: ") or config.secondary_color
            config.welcome_message = input(f"Mensaje de bienvenida [{config.welcome_message}]: ") or config.welcome_message

            db.session.commit()
            print("✅ Configuración actualizada con éxito.")
        else:
            print("ℹ️ No se realizaron cambios.")
    else:
        new_config = ClinicConfig(
            clinic_name=input("Nombre de la clínica: "),
            logo_url=input("URL del logo: "),
            primary_color=input("Color primario (hex): "),
            secondary_color=input("Color secundario (hex): "),
            welcome_message=input("Mensaje de bienvenida: ")
        )
        db.session.add(new_config)
        db.session.commit()
        print("✅ Nueva configuración registrada con éxito.")
