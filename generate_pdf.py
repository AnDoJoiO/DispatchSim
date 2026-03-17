#!/usr/bin/env python3
"""Generate DispatchSim Product Brief PDF using ReportLab."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from datetime import date

# ── Colors (DispatchSim palette) ──────────────────────────
SLATE_900 = HexColor("#0f172a")
SLATE_700 = HexColor("#334155")
SLATE_500 = HexColor("#64748b")
SLATE_300 = HexColor("#cbd5e1")
SLATE_100 = HexColor("#f1f5f9")
BLUE_600  = HexColor("#2563eb")
BLUE_100  = HexColor("#dbeafe")
RED_600   = HexColor("#dc2626")
GREEN_600 = HexColor("#059669")
WHITE     = HexColor("#ffffff")

# ── Styles ────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

S_TITLE = make_style("S_TITLE", fontSize=28, leading=34, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)
S_SUBTITLE = make_style("S_SUBTITLE", fontSize=13, leading=18, textColor=SLATE_300, alignment=TA_CENTER)
S_H1 = make_style("S_H1", fontSize=18, leading=24, textColor=SLATE_900, fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=8)
S_H2 = make_style("S_H2", fontSize=13, leading=17, textColor=BLUE_600, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4)
S_BODY = make_style("S_BODY", fontSize=10, leading=15, textColor=SLATE_700, alignment=TA_JUSTIFY, spaceAfter=6)
S_BODY_BOLD = make_style("S_BODY_BOLD", fontSize=10, leading=15, textColor=SLATE_900, fontName="Helvetica-Bold", spaceAfter=4)
S_BULLET = make_style("S_BULLET", fontSize=10, leading=14, textColor=SLATE_700, leftIndent=16, bulletIndent=6, spaceAfter=3)
S_SMALL = make_style("S_SMALL", fontSize=8, leading=11, textColor=SLATE_500, alignment=TA_CENTER)
S_TABLE_H = make_style("S_TABLE_H", fontSize=9, leading=12, textColor=WHITE, fontName="Helvetica-Bold")
S_TABLE_C = make_style("S_TABLE_C", fontSize=9, leading=12, textColor=SLATE_700)
S_TABLE_C_BOLD = make_style("S_TABLE_C_BOLD", fontSize=9, leading=12, textColor=SLATE_900, fontName="Helvetica-Bold")

# ── Cover page background ────────────────────────────────
class CoverBackground(Flowable):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
    def draw(self):
        self.canv.setFillColor(SLATE_900)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=SLATE_300, spaceAfter=10, spaceBefore=6)

def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", S_BULLET)

def section_title(text):
    return Paragraph(text, S_H1)

def sub_title(text):
    return Paragraph(text, S_H2)

def body(text):
    return Paragraph(text, S_BODY)

def body_bold(text):
    return Paragraph(text, S_BODY_BOLD)

def make_table(headers, rows, col_widths=None):
    """Create a styled table."""
    header_row = [Paragraph(h, S_TABLE_H) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), S_TABLE_C) for c in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_600),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SLATE_100]),
        ("GRID", (0, 0), (-1, -1), 0.5, SLATE_300),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t

# ── Build PDF ─────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        "dispatchsim_product_brief.pdf",
        pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
    )

    W = doc.width
    story = []

    # ═══════════════════════════════════════════════════════
    # 1. COVER PAGE
    # ═══════════════════════════════════════════════════════
    story.append(Spacer(1, 6*cm))

    # Red dot + DISPATCH
    story.append(Paragraph(
        '<font color="#dc2626">&bull;</font>&nbsp;&nbsp;'
        '<font size="32" color="#0f172a"><b>DISPATCH</b></font>',
        make_style("cover_logo", alignment=TA_CENTER, fontSize=32, leading=40)
    ))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "Plataforma de simulació d'emergències amb IA",
        make_style("cover_tag", fontSize=14, leading=18, textColor=SLATE_500, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 4*cm))
    story.append(HRFlowable(width="40%", thickness=1, color=BLUE_600, spaceAfter=12))
    story.append(Paragraph("Product Brief", make_style("cover_type", fontSize=16, textColor=BLUE_600, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(f"Versió 1.0 &middot; {date.today().strftime('%B %Y')}", make_style("cover_date", fontSize=10, textColor=SLATE_500, alignment=TA_CENTER)))
    story.append(Paragraph("Document confidencial", make_style("cover_conf", fontSize=9, textColor=SLATE_500, alignment=TA_CENTER, spaceBefore=4)))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 2. RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Resumen ejecutivo"))
    story.append(hr())

    story.append(body(
        "<b>DispatchSim</b> es una plataforma web que simula llamadas de emergencia con inteligencia artificial "
        "para formar operadores de centrales de coordinación (112, policía, bomberos, protección civil)."
    ))
    story.append(body(
        "El operador recibe una llamada simulada de un alertante generado por IA que describe una emergencia, "
        "responde preguntas, se altera si no recibe ayuda y reacciona a cada decisión. No hay guion: cada llamada es diferente."
    ))
    story.append(body(
        "El formador controla el nivel de dificultad, el tipo de emergencia y las instrucciones que recibe la IA. "
        "Al finalizar la simulación, la plataforma genera un informe de debriefing con tiempos de respuesta, "
        "datos recogidos y transcripción completa."
    ))
    story.append(Spacer(1, 4*mm))

    story.append(body_bold("Para quién:"))
    story.append(bullet("Servicios de emergencias que necesitan formar nuevos operadores"))
    story.append(bullet("Equipos en activo que requieren reciclaje y actualización de protocolos"))
    story.append(bullet("Responsables de formación que necesitan evaluar competencias de forma objetiva"))

    story.append(Spacer(1, 4*mm))
    story.append(body_bold("Por qué existe:"))
    story.append(body(
        "Formar operadores con manuales no prepara para la presión de una llamada real. "
        "Los simulacros presenciales son caros y difíciles de organizar. "
        "DispatchSim permite practicar de forma ilimitada, desde cualquier ordenador, con evaluación automática."
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 3. FUNCIONALIDADES ACTUALES
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Funcionalidades en producción"))
    story.append(hr())

    features = [
        ("Simulación por IA", "Alertante generado por Claude (Anthropic) que responde en tiempo real. "
         "Comportamiento emocional configurable: calma, pánico o agresión. Reacciona al silencio del operador. "
         "Cierre automático cuando el operador da permiso para colgar."),
        ("Voz bidireccional", "El operador habla por micrófono (reconocimiento de voz con OpenAI Whisper). "
         "El alertante responde por voz (ElevenLabs con fallback a OpenAI TTS). "
         "Detección automática de actividad vocal (VAD)."),
        ("Mapa de localización CAD", "Mapa OpenStreetMap con marcador en las coordenadas reales del incidente. "
         "Geocodificación via Nominatim. Simula la latencia de localización de un CAD real. "
         "Indicador de estado: localizando → GPS fijo."),
        ("Ficha de intervención", "Formulario que el operador rellena durante la llamada: dirección, teléfono, "
         "heridos, riesgos y notas. Se guarda asociada al incidente."),
        ("Debriefing automático", "Informe generado al finalizar: tiempo de respuesta, tiempo hasta primera pregunta, "
         "transcripción completa [OPR]/[ALT] y ficha de intervención."),
        ("Escenarios configurables", "El formador crea escenarios: tipo de emergencia, ubicación, estado de la víctima, "
         "emoción del alertante e instrucciones secretas para la IA."),
        ("Gestión de usuarios", "Tres roles: administrador, formador, operador. Cuentas con caducidad configurable. "
         "Limpieza automática de cuentas expiradas."),
        ("Multiidioma", "Interfaz y simulación en catalán, español, francés e inglés. "
         "El alertante responde en el idioma seleccionado por el operador."),
        ("Historial completo", "Todas las simulaciones quedan registradas: transcripción, ficha, métricas y debriefing. "
         "Filtros por prioridad, búsqueda y eliminación por lotes."),
    ]

    for title, desc in features:
        story.append(KeepTogether([
            sub_title(title),
            body(desc),
        ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 4. ROADMAP
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Roadmap de funcionalidades"))
    story.append(hr())
    story.append(body("Funcionalidades planificadas para las próximas iteraciones, ordenadas por impacto."))
    story.append(Spacer(1, 4*mm))

    roadmap = [
        ["TTS emocional (ElevenLabs)", "Alta", "Q2 2026",
         "Voces con emociones realistas via ElevenLabs eleven_turbo_v2_5. "
         "Reemplaza el TTS actual con soporte de tonos emocionales configurables por escenario."],
        ["Dashboard de analíticas", "Alta", "Q3 2026",
         "Panel para formadores con KPIs por operador: nº simulaciones, puntuación media, evolución temporal. "
         "Comparativa entre operadores. Exportación PDF/CSV."],
        ["Replay de audio", "Media", "Q3 2026",
         "Escuchar el audio completo de una simulación pasada, sincronizado con la transcripción en pantalla. "
         "Almacenamiento en S3 con retención configurable."],
        ["Auto-relleno de ficha por IA", "Media", "Q2 2026",
         "La IA rellena automáticamente la ficha de intervención con los datos mencionados durante la conversación "
         "(dirección, heridos, tipo de emergencia) via Tool Use."],
    ]

    story.append(make_table(
        ["Funcionalidad", "Prioridad", "Estimación", "Descripción"],
        roadmap,
        col_widths=[3.5*cm, 1.8*cm, 2*cm, 9*cm],
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 5. ARQUITECTURA TÉCNICA
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Arquitectura técnica"))
    story.append(hr())

    story.append(sub_title("Stack tecnológico"))
    stack = [
        ["Backend", "FastAPI + SQLModel + Alembic (Python 3.12)"],
        ["Frontend", "Vue 3 + TypeScript + Pinia + Vite + Tailwind CSS"],
        ["IA conversacional", "Anthropic Claude (claude-sonnet-4-6)"],
        ["Speech-to-Text", "OpenAI Whisper"],
        ["Text-to-Speech", "ElevenLabs (primario) + OpenAI TTS (fallback)"],
        ["Geocodificación", "Nominatim (OpenStreetMap) — gratuito"],
        ["Mapas", "Leaflet.js + OpenStreetMap tiles — gratuito"],
        ["Base de datos", "SQLite (desarrollo) / PostgreSQL (producción)"],
        ["Deploy", "Railway (Nixpacks + Procfile)"],
        ["CI/CD", "GitHub Actions (pytest + vitest + build)"],
    ]
    story.append(make_table(["Capa", "Tecnología"], stack, col_widths=[3.5*cm, 13*cm]))

    story.append(Spacer(1, 6*mm))
    story.append(sub_title("Diagrama de componentes"))

    # ASCII diagram as formatted text
    diagram = """
    ┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
    │  OPERADOR    │────▷│   Vue 3 + TS     │────▷│  FastAPI      │
    │  (navegador) │◁────│   Pinia stores   │◁────│  REST API     │
    └─────────────┘     │   Leaflet map    │     │  8 routers    │
                        │   AudioContext   │     │  SQLModel ORM │
                        └──────────────────┘     └──────┬───────┘
                                                        │
                              ┌──────────────────────────┼──────────┐
                              │                          │          │
                        ┌─────▷─────┐  ┌────────▷──────┐│┌────────▷──────┐
                        │ Claude AI │  │ Whisper (STT) │││ ElevenLabs    │
                        │ Anthropic │  │ OpenAI        │││ TTS           │
                        └───────────┘  └───────────────┘│└───────────────┘
                                                        │
                                                  ┌─────▷─────┐
                                                  │ PostgreSQL│
                                                  │ (Railway) │
                                                  └───────────┘
    """
    story.append(Paragraph(f"<pre>{diagram}</pre>", make_style("diagram", fontSize=7, leading=9, textColor=SLATE_700, fontName="Courier")))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 6. SEGURIDAD Y CALIDAD
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Seguridad y calidad"))
    story.append(hr())

    story.append(sub_title("Auditoría de seguridad completada"))
    story.append(body("Se realizó una auditoría completa del código con los siguientes resultados:"))

    audit = [
        ["Vulnerabilidad crítica corregida", "Endpoint /auth/register permitía escalada de rol. Corregido: siempre fuerza rol OPERADOR."],
        ["Respuesta vacía de IA", "Si Claude devuelve respuesta vacía, se lanza ValueError en vez de persistir string vacío en BD."],
        ["Validación MIME audio", "Upload de audio valida magic bytes WebM (0x1A45DFA3) antes de enviar a Whisper."],
        ["AudioContext leak", "cleanup() cierra el AudioContext al desmontar el componente."],
        ["Rate limiting", "Login: 5/min por username. Chat: 10/min por usuario. Voz: 15/min por usuario."],
        ["SQL injection", "Protegido: todo via ORM (SQLModel/SQLAlchemy), sin SQL raw."],
        ["XSS", "CSP restrictivo + sanitización de HTML en mensajes de chat."],
        ["JWT", "HS256 con SECRET_KEY ≥32 chars, validación en producción."],
    ]
    story.append(make_table(["Hallazgo", "Resolución"], audit, col_widths=[5*cm, 11.5*cm]))

    story.append(Spacer(1, 6*mm))
    story.append(sub_title("Cobertura de tests"))
    story.append(body("<b>54 tests automatizados</b> ejecutados en cada push a main via GitHub Actions:"))
    story.append(bullet("33 tests backend (pytest): seguridad, rate limit, auth, incidents, cascade delete"))
    story.append(bullet("21 tests frontend (Vitest): API wrapper, stores Pinia, configuración"))

    story.append(Spacer(1, 4*mm))
    story.append(sub_title("Headers de seguridad HTTP"))
    story.append(bullet("Content-Security-Policy (CSP) restrictivo"))
    story.append(bullet("X-Frame-Options: DENY"))
    story.append(bullet("X-Content-Type-Options: nosniff"))
    story.append(bullet("Referrer-Policy: strict-origin-when-cross-origin"))
    story.append(bullet("Cache-Control: immutable para assets con hash, no-cache para HTML"))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 7. ANÁLISIS COMPETITIVO
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Análisis competitivo"))
    story.append(hr())

    comp_headers = ["Funcionalidad", "DispatchSim", "Sklls", "ThisGen 911", "AnthroPi"]
    comp_rows = [
        ["IA conversacional en tiempo real", "✓ Claude", "✓ GPT-4", "✓ (propio)", "✓ GPT-4"],
        ["Voz bidireccional (STT + TTS)", "✓", "✗", "✓", "✓"],
        ["TTS emocional", "Parcial (3 voces)", "✗", "✗", "✓"],
        ["Mapa CAD con geocodificación", "✓ (Nominatim)", "✗", "✗", "✗"],
        ["Multiidioma (4 idiomas)", "✓ CA/ES/FR/EN", "✗ (solo EN)", "✗ (solo EN)", "✓ (EN/ES)"],
        ["Debriefing automático", "✓", "✓", "Parcial", "✓"],
        ["Dashboard analíticas", "Roadmap", "✓", "✗", "✓"],
        ["Replay de audio", "Roadmap", "✗", "✗", "✓"],
        ["Auto-relleno ficha por IA", "Roadmap", "✗", "✗", "✗"],
        ["Self-hosted / on-premise", "✓ (Docker)", "✗ (SaaS)", "✗ (SaaS)", "✗ (SaaS)"],
        ["Código abierto", "✓", "✗", "✗", "✗"],
        ["Precio", "Coste infra", "$50-200/op/mes", "Consultar", "$75-150/op/mes"],
    ]
    story.append(make_table(comp_headers, comp_rows, col_widths=[4*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.8*cm]))

    story.append(Spacer(1, 6*mm))
    story.append(sub_title("Ventajas diferenciales de DispatchSim"))
    story.append(bullet("<b>Mapa CAD con geocodificación real</b> — ningún competidor documentado lo ofrece"))
    story.append(bullet("<b>Multiidioma nativo</b> (4 idiomas) — la mayoría solo ofrece inglés"))
    story.append(bullet("<b>Self-hosted</b> — puede desplegarse en infraestructura propia (Docker) o en cloud"))
    story.append(bullet("<b>Coste operativo mínimo</b> — sin licencias por operador; solo coste de infraestructura y APIs"))
    story.append(bullet("<b>Código propio</b> — personalizable y extensible sin depender de un proveedor"))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 8. CASOS DE USO
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Casos de uso"))
    story.append(hr())

    story.append(sub_title("1. Formación inicial de nuevos operadores"))
    story.append(body(
        "Un operador recién incorporado necesita practicar la gestión de llamadas antes de atender emergencias reales. "
        "El formador le asigna escenarios de dificultad progresiva: primero una caída leve, después un accidente de tráfico, "
        "finalmente un incendio con múltiples víctimas. Después de cada simulación, revisan juntos el debriefing."
    ))
    story.append(Spacer(1, 3*mm))

    story.append(sub_title("2. Reciclaje del personal en activo"))
    story.append(body(
        "Operadores con experiencia practican situaciones poco frecuentes: avalanchas, incidentes con materias peligrosas, "
        "emergencias médicas con paciente agresivo. El formador puede forzar que la IA hable en un idioma específico "
        "para entrenar la gestión multilingüe."
    ))
    story.append(Spacer(1, 3*mm))

    story.append(sub_title("3. Evaluación objetiva de competencias"))
    story.append(body(
        "El responsable de formación accede al historial de simulaciones de cada operador: tiempo de respuesta medio, "
        "datos recogidos por llamada, escenarios completados. Puede comparar operadores del mismo turno y detectar "
        "necesidades formativas individuales."
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════
    # 9. PRECIOS DE REFERENCIA
    # ═══════════════════════════════════════════════════════
    story.append(section_title("Precios de referencia del mercado"))
    story.append(hr())

    story.append(body(
        "Los competidores directos facturan por operador/mes o por simulación. "
        "DispatchSim no tiene licencia por operador — el coste es solo infraestructura y APIs."
    ))
    story.append(Spacer(1, 4*mm))

    pricing = [
        ["Sklls", "$50-200/operador/mes", "SaaS, sin self-hosting. Dashboard incluido."],
        ["AnthroPi", "$75-150/operador/mes", "SaaS. Replay de audio como premium."],
        ["ThisGen 911", "Precio bajo consulta", "Orientado a grandes departamentos USA."],
        ["DispatchSim", "Coste de infraestructura", "Sin licencia por operador. Detalle abajo."],
    ]
    story.append(make_table(["Plataforma", "Precio", "Notas"], pricing, col_widths=[3.5*cm, 4.5*cm, 8.5*cm]))

    story.append(Spacer(1, 6*mm))
    story.append(sub_title("Coste operativo estimado de DispatchSim"))

    costs = [
        ["Railway (hosting)", "$5-20/mes", "Según uso. Plan Starter suficiente para equipos pequeños."],
        ["Anthropic Claude API", "~$0.01-0.03/simulación", "claude-sonnet-4-6. Depende de la duración de la conversación."],
        ["OpenAI Whisper API", "~$0.006/minuto de audio", "Reconocimiento de voz."],
        ["ElevenLabs TTS", "$5/mes (plan Starter)", "Voces emocionales. Fallback gratuito a OpenAI TTS."],
        ["Nominatim + OSM", "Gratuito", "Geocodificación y mapas sin límite."],
    ]
    story.append(make_table(["Servicio", "Coste", "Detalle"], costs, col_widths=[4*cm, 4*cm, 8.5*cm]))

    story.append(Spacer(1, 6*mm))
    story.append(body(
        "<b>Coste estimado total para un equipo de 10 operadores con uso moderado (100 simulaciones/mes):</b> "
        "entre $15 y $40/mes. Esto representa un 90-95% de ahorro respecto a las alternativas SaaS del mercado."
    ))

    # ── Footer note ───────────────────────────────────────
    story.append(Spacer(1, 2*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SLATE_300, spaceAfter=8))
    story.append(Paragraph(
        f"DispatchSim Product Brief &middot; v1.0 &middot; {date.today().strftime('%d/%m/%Y')} &middot; Documento confidencial",
        S_SMALL
    ))

    # ── Build ─────────────────────────────────────────────
    doc.build(story)
    print("✓ PDF generado: dispatchsim_product_brief.pdf")

if __name__ == "__main__":
    build()
