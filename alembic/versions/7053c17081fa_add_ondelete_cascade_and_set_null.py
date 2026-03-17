"""add_ondelete_cascade_and_set_null

Revision ID: 7053c17081fa
Revises: 02c688e14b2b
Create Date: 2026-03-17 18:17:49.821504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7053c17081fa'
down_revision: Union[str, Sequence[str], None] = '02c688e14b2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Naming convention so batch mode can resolve anonymous FK names
_naming = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def upgrade() -> None:
    """Add ondelete CASCADE / SET NULL to all foreign keys."""
    # chatmessage.incident_id → CASCADE
    with op.batch_alter_table('chatmessage', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_chatmessage_incident_id_incident', type_='foreignkey')
        batch_op.create_foreign_key('fk_chatmessage_incident_id_incident', 'incident', ['incident_id'], ['id'], ondelete='CASCADE')

    # incident: creator_id, operator_id, scenario_id → SET NULL
    with op.batch_alter_table('incident', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_incident_creator_id_app_user', type_='foreignkey')
        batch_op.drop_constraint('fk_incident_operator_id_app_user', type_='foreignkey')
        batch_op.drop_constraint('fk_incident_scenario_id_scenario', type_='foreignkey')
        batch_op.create_foreign_key('fk_incident_creator_id_app_user', 'app_user', ['creator_id'], ['id'], ondelete='SET NULL')
        batch_op.create_foreign_key('fk_incident_operator_id_app_user', 'app_user', ['operator_id'], ['id'], ondelete='SET NULL')
        batch_op.create_foreign_key('fk_incident_scenario_id_scenario', 'scenario', ['scenario_id'], ['id'], ondelete='SET NULL')

    # interventiondata.incident_id → CASCADE
    with op.batch_alter_table('interventiondata', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_interventiondata_incident_id_incident', type_='foreignkey')
        batch_op.create_foreign_key('fk_interventiondata_incident_id_incident', 'incident', ['incident_id'], ['id'], ondelete='CASCADE')

    # scenario.creator_id → SET NULL
    with op.batch_alter_table('scenario', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_scenario_creator_id_app_user', type_='foreignkey')
        batch_op.create_foreign_key('fk_scenario_creator_id_app_user', 'app_user', ['creator_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Remove ondelete rules (revert to NO ACTION)."""
    with op.batch_alter_table('scenario', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_scenario_creator_id_app_user', type_='foreignkey')
        batch_op.create_foreign_key('fk_scenario_creator_id_app_user', 'app_user', ['creator_id'], ['id'])

    with op.batch_alter_table('interventiondata', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_interventiondata_incident_id_incident', type_='foreignkey')
        batch_op.create_foreign_key('fk_interventiondata_incident_id_incident', 'incident', ['incident_id'], ['id'])

    with op.batch_alter_table('incident', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_incident_creator_id_app_user', type_='foreignkey')
        batch_op.drop_constraint('fk_incident_operator_id_app_user', type_='foreignkey')
        batch_op.drop_constraint('fk_incident_scenario_id_scenario', type_='foreignkey')
        batch_op.create_foreign_key('fk_incident_creator_id_app_user', 'app_user', ['creator_id'], ['id'])
        batch_op.create_foreign_key('fk_incident_operator_id_app_user', 'app_user', ['operator_id'], ['id'])
        batch_op.create_foreign_key('fk_incident_scenario_id_scenario', 'scenario', ['scenario_id'], ['id'])

    with op.batch_alter_table('chatmessage', naming_convention=_naming) as batch_op:
        batch_op.drop_constraint('fk_chatmessage_incident_id_incident', type_='foreignkey')
        batch_op.create_foreign_key('fk_chatmessage_incident_id_incident', 'incident', ['incident_id'], ['id'])
