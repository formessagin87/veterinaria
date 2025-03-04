"""empty message

Revision ID: 48aadc573348
Revises: 2cad4ce79d92
Create Date: 2025-02-24 00:17:08.859578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48aadc573348'
down_revision = '2cad4ce79d92'
branch_labels = None
depends_on = None


def upgrade():
    # Deshabilitar las restricciones de claves foráneas temporalmente
    op.execute("PRAGMA foreign_keys = OFF")
    
    with op.batch_alter_table('breed', schema=None) as batch_op:
        # Dado que la migración detectó cambios en la clave foránea,
        # no se intenta eliminar una restricción anónima, sino
        # se crea la nueva clave foránea con cascade delete.
        batch_op.create_foreign_key(
            'fk_breed_species',  # Nombre asignado para la nueva restricción
            'species',           # Tabla referenciada
            ['species_id'],      # Columnas de 'breed'
            ['id'],              # Columnas de 'species'
            ondelete='CASCADE'
        )
    
    # Rehabilitar las restricciones de claves foráneas
    op.execute("PRAGMA foreign_keys = ON")


def downgrade():
    op.execute("PRAGMA foreign_keys = OFF")
    
    with op.batch_alter_table('breed', schema=None) as batch_op:
        batch_op.drop_constraint('fk_breed_species', type_='foreignkey')
    
    op.execute("PRAGMA foreign_keys = ON")

