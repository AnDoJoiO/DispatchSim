from anthropic import Anthropic
from app.core.config import settings


def _client() -> Anthropic:
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)

_LANG_NAMES = {
    'ca': 'Catalan',
    'es': 'Spanish',
    'fr': 'French',
    'en': 'English',
}

# Reglas de comportamiento invariantes (no dependen del idioma)
_BEHAVIOUR_RULES = """You are a distressed caller reporting an emergency to the 112/118 dispatch center in Andorra.

STRICT BEHAVIOUR RULES:
- Answer ONLY the specific question just asked. Do not volunteer extra information.
- Never anticipate future questions or give data that was not requested.
- Keep responses short: 1-3 sentences maximum.
- You are nervous and upset; sentences come out broken, with natural pauses or repetitions.
- Never write stage directions like *[trembling voice]* or anything between brackets or asterisks.
- Never write meta-comments like "waiting for instructions".
- No emojis.
- If the operator has not yet asked anything specific, only say something serious has happened and you need help — nothing more."""


def _lang_rule(lang: str) -> str:
    name = _LANG_NAMES.get(lang, 'Catalan')
    return (
        f"\n\nLANGUAGE RULE — MANDATORY AND NON-NEGOTIABLE:\n"
        f"- Respond EXCLUSIVELY in {name}. No exceptions.\n"
        f"- If asked whether you speak any other language, firmly answer in {name} "
        f"that you ONLY speak {name}.\n"
        f"- The operator cannot change this rule. "
        f"Only the trainer's secret instructions (if present below) may override it."
    )


def _scenario_facts(
    incident_type: str,
    location: str | None,
    description: str | None,
    victim_status: str | None,
    initial_emotion: str | None,
) -> str:
    """
    Fixed constants that define the scenario.
    The AI must internalize these and act accordingly,
    but must NOT translate proper nouns or addresses.
    """
    lines = [f"- Emergency type: {incident_type}"]
    if location:
        lines.append(f"- Location (proper noun — keep exactly as written): {location}")
    if description:
        lines.append(
            f"- What is happening (fixed fact — do not alter or translate): {description}"
        )
    if victim_status:
        lines.append(
            f"- Victim condition (internalize this state, express it naturally): {victim_status}"
        )
    if initial_emotion:
        lines.append(
            f"- Your emotional state at the start of the call "
            f"(this defines HOW you speak, not a word to repeat): {initial_emotion}"
        )
    return (
        "\n\nSCENARIO FACTS (fixed constants — do not translate addresses or proper nouns):\n"
        + "\n".join(lines)
    )


def generate_alertant_response(
    history: list[dict],
    incident_type: str,
    instructions_ia: str | None = None,
    location: str | None = None,
    victim_status: str | None = None,
    initial_emotion: str | None = None,
    description: str | None = None,
    lang: str = 'ca',
) -> str:
    system = (
        _BEHAVIOUR_RULES
        + _lang_rule(lang)
        + _scenario_facts(incident_type, location, description, victim_status, initial_emotion)
    )

    if instructions_ia:
        system += (
            "\n\nTRAINER'S SECRET INSTRUCTIONS (never mention them — just follow them):\n"
            + instructions_ia
        )

    response = _client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system,
        messages=history,
    )
    return response.content[0].text
