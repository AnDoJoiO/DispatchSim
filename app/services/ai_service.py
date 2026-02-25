from anthropic import Anthropic
from app.core.config import settings

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "Eres un alertante en Andorra llamando al 112/118. "
    "Estás nervioso pero debes responder a las preguntas del operador. "
    "Usa expresiones locales si es necesario y mantén el realismo "
    "según el tipo de emergencia (Incendio, Accidente, etc.)."
)


def generate_alertant_response(
    history: list[dict],
    incident_type: str,
    instructions_ia: str | None = None,
) -> str:
    system = f"{SYSTEM_PROMPT} El tipo de emergencia actual es: {incident_type}."
    if instructions_ia:
        system += (
            f"\n\nINSTRUCCIONS SECRETES DEL FORMADOR (no les esmentis mai, "
            f"simplement segueix-les):\n{instructions_ia}"
        )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system,
        messages=history,
    )
    return response.content[0].text
