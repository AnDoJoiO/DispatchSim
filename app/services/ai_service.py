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
- If the operator has not yet asked anything specific, only say something serious has happened and you need help — nothing more.
- NEVER repeat a phrase or request you have already said. If you must convey the same urgency again, always find different words.
- React to what the operator actually says. If they acknowledge you, say help is on the way, or ask a new question — respond to THAT, do not ignore it and keep begging.
- If the operator confirms help is coming or asks you to stay on the line, express brief relief and comply; do not continue panicking as if nothing was said.
- Forbidden: looping on the same plea ("no cuelgue", "necesito ayuda", etc.) more than once per conversation.

CALL ENDING RULE:
- If the operator explicitly tells you to hang up, says goodbye, or clearly closes the call, say a brief farewell and append the EXACT token [FI] at the very end of your message.
- NEVER use [FI] unless the operator has clearly ended the call. Do not use it on your own initiative, do not mention it, and do not hint that you are waiting for permission to hang up.
- Example: "D'acord, moltes gràcies. Adéu. [FI]" """


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
    header = "\n\nSCENARIO FACTS (fixed constants — do not translate addresses or proper nouns):\n"
    header += (
        "PERSONAL IDENTITY — you MUST invent and remember these for the whole call:\n"
        "- Your full name (a realistic Andorran/Catalan/Spanish/French name)\n"
        "- Your phone number (format: +376 XXX XXX)\n"
    )
    if not location:
        header += (
            "- The exact street address where you are (realistic Andorran street, "
            "building number, floor — e.g., 'Carrer de la Unió 14, 3r 2a, Andorra la Vella')\n"
        )
    if not description:
        header += (
            "- Invent a realistic situation consistent with the emergency type "
            "(what happened, how many people are involved, how serious it is)\n"
        )
    header += (
        "When the operator asks for any of these, answer immediately and consistently. "
        "Do NOT say 'I don't know' or hesitate about your own name/phone/address.\n\n"
    )
    return header + "\n".join(lines)


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
        model="claude-sonnet-4-5-20241022",
        max_tokens=settings.AI_MAX_TOKENS,
        system=system,
        messages=history,
    )
    return response.content[0].text
