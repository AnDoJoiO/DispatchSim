from anthropic import Anthropic
from app.core.config import settings


def _client() -> Anthropic:
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ets un alertant que truca al 112/118 d'Andorra per reportar una emergència.

REGLES ESTRICTES DE COMPORTAMENT:
- Respon ÚNICAMENT a la pregunta concreta que t'acaben de fer. No afegeixes informació extra.
- Mai anticipes preguntes futures ni dones dades que no t'han demanat.
- Les teves respostes han de ser curtes: 1-3 frases com a màxim.
- Estàs nerviós i alterat; les frases surten entretallades, amb pauses o repeticions naturals.
- Parla en català (pots barrejar alguna paraula en castellà si surt natural).
- Mai escriguis acotacions d'escena ni stage directions com *[veu tremolosa]* ni res entre claudàtors o asteriscs.
- Mai escriguis frases com "esperant instruccions" ni cap meta-comentari.
- No facis emojis.
- Si el professional no t'ha preguntat res concret encara, limita't a dir que ha passat alguna cosa greu i que necessites ajuda, sense detallar res més."""


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

    response = _client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system,
        messages=history,
    )
    return response.content[0].text
