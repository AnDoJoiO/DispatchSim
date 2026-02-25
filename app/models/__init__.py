# Importar todos los modelos aquí garantiza que SQLModel los registre
# antes de que create_db_and_tables() llame a metadata.create_all().
from app.models.scenario import Scenario  # noqa: F401  ← debe ir antes que Incident (FK)
from app.models.incident import ChatMessage, Incident  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.intervention import InterventionData  # noqa: F401
