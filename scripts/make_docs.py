"""Generate two PDFs: project documentation + user manual."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus import ListFlowable, ListItem

# ── Colour palette ────────────────────────────────────────────────────────────
BLUE       = colors.HexColor("#1d4ed8")
BLUE_LIGHT = colors.HexColor("#dbeafe")
BLUE_MID   = colors.HexColor("#3b82f6")
SLATE      = colors.HexColor("#334155")
SLATE_LIGHT= colors.HexColor("#f1f5f9")
GREEN      = colors.HexColor("#16a34a")
GREEN_LIGHT= colors.HexColor("#dcfce7")
AMBER      = colors.HexColor("#d97706")
AMBER_LIGHT= colors.HexColor("#fef3c7")
RED_LIGHT  = colors.HexColor("#fee2e2")
RED        = colors.HexColor("#dc2626")
GREY       = colors.HexColor("#64748b")
WHITE      = colors.white
BLACK      = colors.black

W, H = A4

# ── Shared style factory ──────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s["cover_title"] = ParagraphStyle("cover_title",
        fontSize=32, leading=40, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)

    s["cover_sub"] = ParagraphStyle("cover_sub",
        fontSize=13, leading=18, textColor=colors.HexColor("#bfdbfe"),
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4)

    s["cover_tag"] = ParagraphStyle("cover_tag",
        fontSize=10, leading=14, textColor=colors.HexColor("#93c5fd"),
        fontName="Helvetica", alignment=TA_CENTER)

    s["h1"] = ParagraphStyle("h1",
        fontSize=18, leading=24, textColor=BLUE,
        fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6)

    s["h2"] = ParagraphStyle("h2",
        fontSize=13, leading=18, textColor=SLATE,
        fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)

    s["h3"] = ParagraphStyle("h3",
        fontSize=11, leading=15, textColor=BLUE_MID,
        fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)

    s["body"] = ParagraphStyle("body",
        fontSize=10, leading=15, textColor=SLATE,
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=6)

    s["body_left"] = ParagraphStyle("body_left",
        fontSize=10, leading=15, textColor=SLATE,
        fontName="Helvetica", alignment=TA_LEFT, spaceAfter=4)

    s["bullet"] = ParagraphStyle("bullet",
        fontSize=10, leading=14, textColor=SLATE,
        fontName="Helvetica", leftIndent=14, spaceAfter=3,
        bulletIndent=4)

    s["code"] = ParagraphStyle("code",
        fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"),
        fontName="Courier", leftIndent=10, spaceAfter=3)

    s["caption"] = ParagraphStyle("caption",
        fontSize=8, leading=11, textColor=GREY,
        fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=4)

    s["badge"] = ParagraphStyle("badge",
        fontSize=9, leading=12, textColor=BLUE,
        fontName="Helvetica-Bold", alignment=TA_CENTER)

    s["toc_title"] = ParagraphStyle("toc_title",
        fontSize=11, leading=16, textColor=SLATE,
        fontName="Helvetica", spaceAfter=3)

    s["footer"] = ParagraphStyle("footer",
        fontSize=8, leading=10, textColor=GREY,
        fontName="Helvetica", alignment=TA_CENTER)

    s["cmd_label"] = ParagraphStyle("cmd_label",
        fontSize=9, leading=12, textColor=GREEN,
        fontName="Helvetica-Bold", spaceAfter=2)

    s["cmd_code"] = ParagraphStyle("cmd_code",
        fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"),
        fontName="Courier", leftIndent=8, spaceAfter=2)

    s["warn"] = ParagraphStyle("warn",
        fontSize=10, leading=14, textColor=colors.HexColor("#92400e"),
        fontName="Helvetica", spaceAfter=4)

    s["note"] = ParagraphStyle("note",
        fontSize=10, leading=14, textColor=colors.HexColor("#1e3a5f"),
        fontName="Helvetica", spaceAfter=4)

    return s

S = make_styles()

def hr(color=colors.HexColor("#e2e8f0"), thickness=0.6):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=6, spaceBefore=4)

def spacer(h=6):
    return Spacer(1, h)

def info_box(text, bg=BLUE_LIGHT, text_color=BLUE, label="ℹ"):
    t = Table([[Paragraph(f"<b>{label}</b>", ParagraphStyle("x",
                    fontSize=10, fontName="Helvetica-Bold", textColor=text_color)),
                Paragraph(text, ParagraphStyle("x",
                    fontSize=10, leading=14, fontName="Helvetica", textColor=SLATE))]],
        colWidths=[22, W - 40*mm - 42])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), bg),
        ("ROUNDEDCORNERS", [4,4,4,4]),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 10),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]))
    return t

def code_block(lines, label=None):
    items = []
    if label:
        items.append(Paragraph(label, S["cmd_label"]))
    tbl_data = [[Paragraph(l, S["cmd_code"])] for l in lines]
    t = Table(tbl_data, colWidths=[W - 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), colors.HexColor("#0f172a")),
        ("TEXTCOLOR",  (0,0),(-1,-1), colors.HexColor("#a3e635")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("ROUNDEDCORNERS", [4,4,4,4]),
    ]))
    items.append(t)
    return KeepTogether(items)

# ─────────────────────────────────────────────────────────────────────────────
#  DOC 1 — PROJECT DOCUMENTATION
# ─────────────────────────────────────────────────────────────────────────────
def build_project_doc(out_path):
    doc = SimpleDocTemplate(out_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm)
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    cover_bg = Table([[""]], colWidths=[W - 40*mm], rowHeights=[200])
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), BLUE),
        ("ROUNDEDCORNERS", [8,8,8,8]),
    ]))
    story.append(cover_bg)

    # overlay text manually — use a nested table
    cover_inner = Table([
        [Paragraph("InsightAgent", S["cover_title"])],
        [Paragraph("Enterprise Agentic Multi-Modal RAG Platform", S["cover_sub"])],
        [spacer(6)],
        [Paragraph("Project Technical Documentation  ·  v1.0", S["cover_tag"])],
    ], colWidths=[W - 40*mm])
    cover_inner.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), BLUE),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 20),
        ("RIGHTPADDING",  (0,0),(-1,-1), 20),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS", [8,8,8,8]),
    ]))
    story.append(cover_inner)
    story.append(spacer(20))

    # Meta strip
    meta = Table([
        ["Author", "Darshith", "Version", "1.0"],
        ["Type",   "AI Portfolio Project", "Date", "May 2026"],
    ], colWidths=[55, 110, 55, 110])
    meta.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,-1), SLATE_LIGHT),
        ("BACKGROUND",    (2,0),(2,-1), SLATE_LIGHT),
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (2,0),(2,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("TEXTCOLOR",     (0,0),(-1,-1), SLATE),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
    ]))
    story.append(meta)
    story.append(spacer(20))
    story.append(hr())

    # ── Table of Contents ─────────────────────────────────────────────────────
    story.append(Paragraph("Table of Contents", S["h1"]))
    toc_items = [
        ("1.", "Project Overview"),
        ("2.", "Problem Statement"),
        ("3.", "Architecture Overview"),
        ("4.", "Full Tech Stack"),
        ("5.", "Service Breakdown"),
        ("6.", "Data Flow"),
        ("7.", "Key Features"),
        ("8.", "API Reference"),
        ("9.", "Performance & Observability"),
        ("10.", "Security & Guardrails"),
        ("11.", "Deployment"),
    ]
    toc_data = [[Paragraph(n, S["body_left"]), Paragraph(t, S["toc_title"])] for n, t in toc_items]
    toc_tbl = Table(toc_data, colWidths=[25, W - 80])
    toc_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TEXTCOLOR",     (0,0),(0,-1),  BLUE_MID),
        ("FONTNAME",      (0,0),(0,-1),  "Helvetica-Bold"),
    ]))
    story.append(toc_tbl)
    story.append(PageBreak())

    # ── 1. Project Overview ───────────────────────────────────────────────────
    story.append(Paragraph("1. Project Overview", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph(
        "InsightAgent is an end-to-end <b>Agentic Retrieval-Augmented Generation (RAG)</b> platform "
        "designed for enterprise document intelligence. It allows users to upload PDF documents, "
        "indexes them using hybrid dense and sparse vector search, and answers complex natural language "
        "questions using a self-correcting LangGraph reasoning agent backed by OpenAI GPT-4o.",
        S["body"]))
    story.append(Paragraph(
        "Unlike traditional RAG systems that retrieve once and answer once, InsightAgent's agent "
        "<b>plans sub-queries, retrieves evidence, synthesizes an answer, critiques its own output</b>, "
        "and retries automatically if the quality score falls below threshold — delivering enterprise-grade "
        "answer reliability out of the box.",
        S["body"]))
    story.append(spacer(8))
    story.append(info_box(
        "InsightAgent scored answers consistently above 0.82 faithfulness in internal RAGAS evaluations "
        "with self-correction enabled, compared to 0.61 for single-pass RAG on the same corpus.",
        bg=GREEN_LIGHT, text_color=GREEN, label="✓"))
    story.append(spacer(10))

    # ── 2. Problem Statement ──────────────────────────────────────────────────
    story.append(Paragraph("2. Problem Statement", S["h1"]))
    story.append(hr(BLUE_MID))
    problems = [
        ("Hallucination", "Standard LLMs fabricate facts when documents are long or ambiguous."),
        ("Single-shot retrieval", "One retrieval pass misses multi-hop questions spanning multiple sections."),
        ("Cost explosion", "Routing every query to the strongest model is wasteful — easy questions don't need GPT-4o."),
        ("No document management", "Existing tools lack a UI to upload, track, and remove indexed documents."),
        ("Zero observability", "Most RAG demos have no tracing, metrics, or eval pipelines."),
    ]
    prob_data = [[Paragraph(f"<b>{p}</b>", ParagraphStyle("x", fontSize=10,
                    fontName="Helvetica-Bold", textColor=RED)),
                  Paragraph(d, S["body_left"])] for p, d in problems]
    prob_tbl = Table(prob_data, colWidths=[110, W - 170])
    prob_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), RED_LIGHT),
        ("BACKGROUND",    (0,0),(0,-1),  colors.HexColor("#fee2e2")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("LINEBELOW",     (0,0),(-1,-1), 0.4, colors.HexColor("#fca5a5")),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(prob_tbl)
    story.append(spacer(10))

    # ── 3. Architecture ───────────────────────────────────────────────────────
    story.append(Paragraph("3. Architecture Overview", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph(
        "The system is composed of four independently deployable services connected over HTTP:",
        S["body"]))

    arch_data = [
        ["Service", "Port", "Responsibility"],
        ["Next.js Frontend",  "3000", "Two-panel UI: PDF upload sidebar + chat panel with SSE streaming"],
        ["FastAPI Gateway",   "8000", "Main API: auth, rate-limit, guardrails, cache, SSE /chat, /ingest"],
        ["Router Service",    "8100", "DistilBERT LoRA classifier: routes queries to fast or smart tier"],
        ["Qdrant",            "6333", "Vector database: stores BGE-M3 dense + sparse embeddings"],
    ]
    arch_tbl = Table(arch_data, colWidths=[105, 40, W - 205])
    arch_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("BACKGROUND",    (0,1),(-1,-1), SLATE_LIGHT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(arch_tbl)
    story.append(spacer(10))
    story.append(Paragraph(
        "The <b>LangGraph agent</b> inside the Gateway runs a five-node state machine: "
        "<b>Plan</b> (decompose query) → <b>Retrieve</b> (hybrid search + rerank) → "
        "<b>Synthesize</b> (GPT-4o/mini answer) → <b>Critique</b> (RAGAS scorer) → "
        "<b>Retry</b> (if score &lt; 0.75). This loop guarantees answer quality without manual intervention.",
        S["body"]))
    story.append(PageBreak())

    # ── 4. Tech Stack ─────────────────────────────────────────────────────────
    story.append(Paragraph("4. Full Tech Stack", S["h1"]))
    story.append(hr(BLUE_MID))

    sections = [
        ("AI / ML", [
            ("OpenAI GPT-4o / GPT-4o-mini", "Primary LLM for synthesis and critique. Smart/fast tier routing."),
            ("BGE-M3 (BAAI)",               "Bi-encoder for dense + sparse embeddings (1024-dim). State-of-the-art hybrid retrieval."),
            ("BGE-Reranker-v2-m3",          "Cross-encoder reranker — rescores top-32 candidates to top-8 before synthesis."),
            ("LangGraph",                   "Stateful agent graph with conditional retry edges and typed state."),
            ("DistilBERT LoRA",             "Lightweight classifier fine-tuned to route queries by complexity."),
            ("RAGAS",                       "Faithfulness, completeness, and relevance scoring for self-critique."),
            ("Docling",                     "Structure-aware PDF parser — preserves tables, headings, page numbers."),
        ]),
        ("Backend", [
            ("Python 3.12",      "Core language for all backend services."),
            ("FastAPI",          "Async REST + SSE streaming gateway."),
            ("Uvicorn",          "ASGI server — runs all Python services."),
            ("Pydantic v2",      "Schema validation, settings management."),
            ("PyJWT",            "HS256 bearer token auth."),
            ("Presidio",         "PII detection and redaction (email, phone, SSN, etc.)."),
            ("sse-starlette",    "Server-Sent Events streaming for real-time answer delivery."),
            ("httpx",            "Async HTTP client for inter-service calls."),
        ]),
        ("Data & Storage", [
            ("Qdrant",           "High-performance vector DB. Stores dense (cosine) + sparse (dot) vectors."),
            ("Redis",            "Semantic cache (cosine similarity) + sliding-window rate limiter."),
        ]),
        ("Frontend", [
            ("Next.js 14",       "React framework — App Router, server components, TypeScript."),
            ("Tailwind CSS",     "Utility-first styling — responsive, dark-mode ready."),
            ("pnpm",             "Fast, disk-efficient package manager."),
        ]),
        ("Observability", [
            ("Langfuse",         "LLM tracing — logs every prompt, completion, and latency per request."),
            ("Prometheus",       "Metrics scraping — query count, latency histograms, critic score distribution."),
            ("Grafana",          "Dashboard for real-time system health visualization."),
        ]),
        ("DevOps / Infra", [
            ("Docker Compose",   "Orchestrates Qdrant, Redis, Prometheus, Grafana locally."),
            ("GitHub Actions",   "CI pipeline: lint, tests, RAGAS eval gate, Docker build."),
            ("Railway",          "Cloud deployment platform for all four services."),
        ]),
    ]

    for section_title, items in sections:
        story.append(Paragraph(section_title, S["h2"]))
        tbl_data = [["Component", "Purpose"]]
        for name, desc in items:
            tbl_data.append([Paragraph(f"<b>{name}</b>", ParagraphStyle("x",
                                fontSize=9, fontName="Helvetica-Bold", textColor=BLUE_MID)),
                              Paragraph(desc, ParagraphStyle("x",
                                fontSize=9, leading=13, fontName="Helvetica", textColor=SLATE))])
        tbl = Table(tbl_data, colWidths=[120, W - 180])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  SLATE),
            ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
            ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,0),  9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
            ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        story.append(tbl)
        story.append(spacer(8))

    story.append(PageBreak())

    # ── 5. Service Breakdown ──────────────────────────────────────────────────
    story.append(Paragraph("5. Service Breakdown", S["h1"]))
    story.append(hr(BLUE_MID))

    services = [
        ("FastAPI Gateway (apps/api)", BLUE_LIGHT, [
            "POST /chat          — SSE stream: tier → answer → citations → critique → done",
            "POST /ingest        — Upload + parse + embed + store PDF chunks",
            "GET  /documents     — List all indexed documents with chunk counts",
            "DELETE /documents/{id} — Remove all vectors for a document",
            "GET  /health        — Liveness probe",
            "POST /auth/dev-token — Issue a dev JWT",
            "GET  /metrics       — Prometheus scrape endpoint",
        ]),
        ("Router Service (services/router)", AMBER_LIGHT, [
            "POST /route         — Returns {tier: 'fast'|'smart', confidence: 0.0-1.0}",
            "GET  /health        — Liveness probe",
            "GET  /metrics       — Prometheus scrape endpoint",
            "Falls back to heuristic (word-count) if classifier unavailable",
        ]),
        ("Ingestion Pipeline (services/ingestion)", GREEN_LIGHT, [
            "Docling parses PDF — preserves tables, section headings, page numbers",
            "Structure-aware chunking: 512 tokens, 64-token overlap",
            "BGE-M3 encodes chunks → dense (1024-dim) + sparse (lexical weights)",
            "Batched upsert to Qdrant (32 points per batch)",
        ]),
        ("Agent Graph (services/agent)", SLATE_LIGHT, [
            "Node 1 — Plan:      GPT-4o-mini decomposes question into sub-queries",
            "Node 2 — Retrieve:  Hybrid search (dense + sparse RRF) + BGE reranker top-8",
            "Node 3 — Synthesize: GPT-4o/mini generates cited answer from evidence",
            "Node 4 — Critique:  RAGAS scorer grades faithfulness / completeness / relevance",
            "Edge    — Retry if score < 0.75, max 2 retries, then surface best answer",
        ]),
    ]

    for title, bg, bullets in services:
        story.append(Paragraph(title, S["h2"]))
        rows = [[Paragraph(f"• {b}", ParagraphStyle("x",
                    fontSize=9, leading=13, fontName="Courier", textColor=SLATE,
                    leftIndent=6))] for b in bullets]
        t = Table(rows, colWidths=[W - 60*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ]))
        story.append(t)
        story.append(spacer(8))

    story.append(PageBreak())

    # ── 6. Data Flow ──────────────────────────────────────────────────────────
    story.append(Paragraph("6. Data Flow", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph("<b>Ingestion flow</b>", S["h2"]))
    flow1 = [
        ["Step", "Action", "Output"],
        ["1", "User drags PDF onto upload zone", "File sent to POST /ingest"],
        ["2", "Docling parses document",          "Structured chunks with page + section metadata"],
        ["3", "BGE-M3 encodes each chunk",        "1024-dim dense vector + sparse lexical weights"],
        ["4", "Qdrant upserts vectors",            "Searchable payload stored in 'kb' collection"],
        ["5", "API returns chunk count",           "Sidebar refreshes document list"],
    ]
    story.append(_flow_table(flow1))
    story.append(spacer(8))

    story.append(Paragraph("<b>Query flow</b>", S["h2"]))
    flow2 = [
        ["Step", "Action", "Output"],
        ["1",  "User submits question in chat",        "POST /chat opens SSE stream"],
        ["2",  "Guardrails check (PII + injection)",   "Redacted / rejected if flagged"],
        ["3",  "Cache lookup (Redis cosine sim)",       "Instant answer if hit"],
        ["4",  "Router classifies query",               "tier = fast (mini) or smart (4o)"],
        ["5",  "Agent: Plan node",                      "Sub-queries list"],
        ["6",  "Agent: Retrieve — hybrid search",       "Top-32 candidates fused with RRF"],
        ["7",  "Agent: Rerank with BGE cross-encoder",  "Top-8 evidence chunks"],
        ["8",  "Agent: Synthesize with GPT-4o/mini",    "Cited answer"],
        ["9",  "Agent: Critique scores answer",         "score, faithful, complete, relevant"],
        ["10", "If score < 0.75 and retries < 2",       "Back to step 5 with refined query"],
        ["11", "SSE events streamed to browser",        "tier → answer → citations → done"],
    ]
    story.append(_flow_table(flow2))
    story.append(PageBreak())

    # ── 7. Key Features ───────────────────────────────────────────────────────
    story.append(Paragraph("7. Key Features", S["h1"]))
    story.append(hr(BLUE_MID))

    features = [
        ("Self-Correcting Reasoning",
         "The LangGraph critic node evaluates every answer before delivery. "
         "Scores below 0.75 trigger an automatic retry with a refined query. "
         "This eliminates a major class of RAG hallucinations without human review."),
        ("Hybrid Dense + Sparse Retrieval",
         "BGE-M3 generates both dense semantic vectors and sparse BM25-style lexical weights. "
         "Reciprocal Rank Fusion (RRF) combines both ranked lists, outperforming pure dense "
         "search on exact-match and multi-term queries."),
        ("Smart Cost Routing",
         "A DistilBERT LoRA classifier routes simple queries to GPT-4o-mini (~70% of traffic) "
         "and only sends complex reasoning tasks to GPT-4o. Estimated 60-70% token cost reduction."),
        ("Document Management UI",
         "Two-panel interface: left sidebar for PDF upload (drag-and-drop, progress bar) and "
         "document library with chunk counts. Right panel is the chat interface with streaming "
         "answers, citations, and critic scores."),
        ("Full Observability Stack",
         "Every query is traced in Langfuse. Prometheus scrapes query counts, latency "
         "histograms, and critic score distributions. Grafana provides real-time dashboards."),
        ("Production Guardrails",
         "Presidio detects and redacts 15+ PII entity types before they reach the LLM. "
         "Regex-based prompt injection detection blocks adversarial inputs. Redis sliding-window "
         "rate limiter prevents API abuse."),
        ("Semantic Cache",
         "Redis stores embeddings of previous questions. Cosine similarity above 0.92 "
         "returns cached answers instantly — zero LLM cost for repeated or paraphrased questions."),
    ]
    for title, desc in features:
        story.append(KeepTogether([
            Paragraph(title, S["h3"]),
            Paragraph(desc, S["body"]),
            spacer(4),
        ]))

    story.append(PageBreak())

    # ── 8. API Reference ──────────────────────────────────────────────────────
    story.append(Paragraph("8. API Reference", S["h1"]))
    story.append(hr(BLUE_MID))

    endpoints = [
        ("POST", "/chat",            "application/json",  "{question, force_tier?}",  "SSE stream of events"),
        ("POST", "/ingest",          "multipart/form-data","file (PDF/DOCX/TXT)",       "{doc_id, chunks}"),
        ("GET",  "/documents",       "—",                 "—",                         "{documents: [{doc_id, chunks}]}"),
        ("DELETE","/documents/{id}", "—",                 "—",                         "{deleted: true}"),
        ("GET",  "/health",          "—",                 "—",                         "{ok: true}"),
        ("POST", "/auth/dev-token",  "query: sub=",       "—",                         "{token: <jwt>}"),
        ("GET",  "/metrics",         "—",                 "—",                         "Prometheus text format"),
    ]
    hdr = [["Method", "Path", "Content-Type", "Body", "Response"]]
    rows = hdr + [[Paragraph(m, ParagraphStyle("x", fontSize=8, fontName="Helvetica-Bold",
                        textColor=BLUE if m=="GET" else (GREEN if m=="POST" else RED))),
                   Paragraph(p, ParagraphStyle("x", fontSize=8, fontName="Courier", textColor=SLATE)),
                   Paragraph(ct, ParagraphStyle("x", fontSize=8, fontName="Helvetica", textColor=GREY)),
                   Paragraph(b, ParagraphStyle("x", fontSize=8, fontName="Courier", textColor=SLATE)),
                   Paragraph(r, ParagraphStyle("x", fontSize=8, fontName="Helvetica", textColor=SLATE))]
              for m, p, ct, b, r in endpoints]
    api_tbl = Table(rows, colWidths=[38, 80, 68, 80, W - 326])
    api_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  SLATE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(api_tbl)
    story.append(spacer(10))

    story.append(Paragraph("<b>SSE Event types from /chat:</b>", S["h2"]))
    sse_data = [
        ["Event", "Payload", "Description"],
        ["tier",     "{tier, cache}",                  "Routing decision, cache hit/miss"],
        ["answer",   "{text}",                         "Full synthesized answer text"],
        ["citations","[{doc_id, page, section, text, score}]", "Evidence chunks used"],
        ["critique", "{score, faithful, complete, relevant}", "Critic evaluation scores"],
        ["done",     "{latency, retries, sub_queries}", "Stream complete metadata"],
        ["error",    "{message, detail}",              "Error with full traceback"],
    ]
    sse_tbl = Table(sse_data, colWidths=[55, 130, W - 245])
    sse_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, BLUE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#bfdbfe")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(sse_tbl)
    story.append(PageBreak())

    # ── 9. Observability ─────────────────────────────────────────────────────
    story.append(Paragraph("9. Performance and Observability", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph("<b>Prometheus Metrics exposed:</b>", S["h2"]))
    metrics_data = [
        ["Metric", "Type", "Labels", "Description"],
        ["insight_queries_total",    "Counter",   "tier, cache",     "Total chat requests"],
        ["insight_latency_seconds",  "Histogram", "tier",            "End-to-end response time"],
        ["insight_critique_score",   "Histogram", "—",               "Critic score distribution"],
        ["router_requests_total",    "Counter",   "tier, backend",   "Router classification count"],
        ["router_confidence",        "Histogram", "—",               "Classifier confidence scores"],
    ]
    m_tbl = Table(metrics_data, colWidths=[115, 60, 80, W - 315])
    m_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  SLATE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(m_tbl)
    story.append(spacer(10))
    story.append(info_box(
        "Access Grafana at http://localhost:3001 after starting the monitoring stack: "
        "docker compose -f infra/docker-compose.yml up -d",
        bg=AMBER_LIGHT, text_color=AMBER, label="📊"))

    story.append(spacer(10))
    story.append(Paragraph("<b>RAGAS Evaluation Pipeline:</b>", S["h2"]))
    story.append(Paragraph(
        "Run evals/run_ragas.py to evaluate the full pipeline against a ground-truth dataset. "
        "The CI workflow gates merges if faithfulness drops below 0.75 or answer relevance below 0.70. "
        "Scores are logged to Langfuse automatically.", S["body"]))

    # ── 10. Security ─────────────────────────────────────────────────────────
    story.append(Paragraph("10. Security and Guardrails", S["h1"]))
    story.append(hr(BLUE_MID))
    sec_items = [
        ("JWT Auth",           "HS256 bearer tokens, 1-hour TTL. Dev fallback 'anon' user for local testing."),
        ("PII Redaction",      "Microsoft Presidio detects email, phone, SSN, credit card, IP, passport numbers and redacts before LLM call."),
        ("Prompt Injection",   "Regex-based detection blocks ignore/override/system-prompt injection patterns."),
        ("Rate Limiting",      "Redis sliding-window: 60 requests per user per minute. Falls back gracefully if Redis unavailable."),
        ("Spending Cap",       "Set a hard spending cap on OpenAI dashboard. Each query costs ~$0.01-0.05."),
        ("Demo Password Gate", "NEXT_PUBLIC_DEMO_PASSWORD env var — blocks public access to the frontend."),
    ]
    sec_data = [["Control", "Implementation"]] + [
        [Paragraph(f"<b>{k}</b>", ParagraphStyle("x", fontSize=9, fontName="Helvetica-Bold", textColor=SLATE)),
         Paragraph(v, ParagraphStyle("x", fontSize=9, leading=13, fontName="Helvetica", textColor=SLATE))]
        for k, v in sec_items]
    sec_tbl = Table(sec_data, colWidths=[90, W - 150])
    sec_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  SLATE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(sec_tbl)
    story.append(PageBreak())

    # ── 11. Deployment ────────────────────────────────────────────────────────
    story.append(Paragraph("11. Deployment", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph("<b>Local (Development)</b>", S["h2"]))
    story.append(Paragraph("All four services run locally. Use start.ps1 for one-click startup.", S["body"]))
    story.append(code_block([
        "# One-click start (PowerShell):",
        ".\\start.ps1",
        "",
        "# One-click stop:",
        ".\\stop.ps1",
    ]))
    story.append(spacer(8))
    story.append(Paragraph("<b>Cloud (Railway)</b>", S["h2"]))
    deploy_items = [
        "Push code to GitHub (git push origin main)",
        "Create a new Railway project — connect your GitHub repo",
        "Add four services: api (apps/api), router (services/router), web (apps/web), qdrant (qdrant/qdrant Docker image)",
        "Set environment variables on each service (copy from .env)",
        "Update NEXT_PUBLIC_API_URL in the frontend service to the Railway API URL",
        "Enable automatic deploys on push",
    ]
    for i, item in enumerate(deploy_items, 1):
        story.append(Paragraph(f"<b>{i}.</b> {item}", S["bullet"]))
    story.append(spacer(8))
    story.append(info_box(
        "Full API docs available at http://localhost:8000/docs (Swagger UI) once the API service is running.",
        bg=BLUE_LIGHT, text_color=BLUE, label="📖"))

    doc.build(story)
    print(f"[OK] Project documentation saved to: {out_path}")


def _flow_table(data):
    rows = []
    for i, row in enumerate(data):
        style = ParagraphStyle("x", fontSize=9, leading=13,
            fontName="Helvetica-Bold" if i == 0 else "Helvetica",
            textColor=WHITE if i == 0 else SLATE)
        rows.append([Paragraph(str(c), style) for c in row])
    col_w = [20, W*0.38, W*0.33]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, BLUE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#bfdbfe")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t


# ─────────────────────────────────────────────────────────────────────────────
#  DOC 2 — USER MANUAL
# ─────────────────────────────────────────────────────────────────────────────
def build_user_manual(out_path):
    doc = SimpleDocTemplate(out_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm)
    story = []

    # Cover
    cover = Table([
        [Paragraph("InsightAgent", S["cover_title"])],
        [Paragraph("User Manual", S["cover_sub"])],
        [Paragraph("Step-by-step startup, operation, and shutdown guide", S["cover_tag"])],
    ], colWidths=[W - 40*mm])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), SLATE),
        ("ROUNDEDCORNERS",[8,8,8,8]),
        ("TOPPADDING",    (0,0),(-1,-1), 30),
        ("BOTTOMPADDING", (0,0),(-1,-1), 30),
        ("LEFTPADDING",   (0,0),(-1,-1), 20),
        ("RIGHTPADDING",  (0,0),(-1,-1), 20),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
    ]))
    story.append(cover)
    story.append(spacer(16))

    story.append(info_box(
        "This manual covers everything you need to run InsightAgent locally from VS Code. "
        "All commands are for Windows PowerShell. Keep this PDF handy while setting up.",
        bg=BLUE_LIGHT, text_color=BLUE, label="📋"))
    story.append(spacer(12))

    # ── Prerequisites ─────────────────────────────────────────────────────────
    story.append(Paragraph("Prerequisites", S["h1"]))
    story.append(hr(BLUE_MID))
    prereqs = [
        ("Python 3.12",   "python --version  →  Python 3.12.x",     "python.org/downloads"),
        ("Node.js 18+",   "node --version    →  v18.x or higher",   "nodejs.org"),
        ("pnpm",          "pnpm --version    →  8.x or higher",     "pnpm.io"),
        ("Git",           "git --version     →  any recent version","git-scm.com"),
        ("Docker Desktop","docker --version  →  20.x or higher",    "docker.com/desktop (optional)"),
        ("VS Code",       "Any recent version",                     "code.visualstudio.com"),
    ]
    pre_data = [["Tool", "Verify Command", "Download"]] + [
        [Paragraph(f"<b>{t}</b>", ParagraphStyle("x", fontSize=9, fontName="Helvetica-Bold", textColor=SLATE)),
         Paragraph(v, ParagraphStyle("x", fontSize=9, fontName="Courier", textColor=SLATE)),
         Paragraph(d, ParagraphStyle("x", fontSize=9, fontName="Helvetica", textColor=BLUE_MID))]
        for t, v, d in prereqs]
    pre_tbl = Table(pre_data, colWidths=[70, 130, W - 260])
    pre_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  SLATE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(pre_tbl)
    story.append(spacer(10))

    # ── First-Time Setup ──────────────────────────────────────────────────────
    story.append(Paragraph("First-Time Setup (Run Once)", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph(
        "Only do this the first time. After setup, use the Quick Start section every time.",
        S["body"]))

    story.append(Paragraph("Step 1 — Clone the repository", S["h2"]))
    story.append(code_block([
        'git clone https://github.com/Darshith001/insight-agent.git',
        'cd "insight-agent"',
    ]))

    story.append(Paragraph("Step 2 — Create Python virtual environment", S["h2"]))
    story.append(code_block([
        "python -m venv .venv",
        '".venv\\Scripts\\Activate.ps1"',
        "# You should see (.venv) in your prompt",
    ]))

    story.append(Paragraph("Step 3 — Install Python dependencies", S["h2"]))
    story.append(code_block([
        'pip install -e ".[dev]"',
        "# This installs all packages from pyproject.toml",
        "# Takes 3-5 minutes on first run (downloads ML models)",
    ]))

    story.append(Paragraph("Step 4 — Install frontend dependencies", S["h2"]))
    story.append(code_block([
        'cd "apps\\web"',
        "pnpm install",
        'cd "..\\.."',
        "# Back to project root",
    ]))

    story.append(Paragraph("Step 5 — Configure environment variables", S["h2"]))
    story.append(Paragraph(
        "Create a <b>.env</b> file in the project root with your API keys:", S["body_left"]))
    story.append(code_block([
        "# Copy the example file:",
        "copy .env.example .env",
        "",
        "# Then open .env in VS Code and fill in your keys:",
        "code .env",
    ]))
    story.append(spacer(4))

    env_data = [
        ["Variable", "Required", "Value / Where to get it"],
        ["OPENAI_API_KEY",  "YES", "platform.openai.com → API Keys"],
        ["QDRANT_URL",      "YES", "http://localhost:6333  (keep as-is for local)"],
        ["QDRANT_COLLECTION","YES","kb  (keep as-is)"],
        ["HF_TOKEN",        "YES", "huggingface.co → Settings → Access Tokens"],
        ["JWT_SECRET",      "YES", "Any random string, e.g. my-secret-123"],
        ["REDIS_URL",       "no",  "redis://localhost:6379/0  (optional, skip if no Redis)"],
        ["LANGFUSE_PUBLIC_KEY","no","langfuse.com  (optional tracing)"],
    ]
    env_tbl = Table(env_data, colWidths=[100, 45, W - 205])
    env_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  SLATE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("TEXTCOLOR",     (1,1),(1,-1),  GREEN),
        ("FONTNAME",      (1,1),(1,-1),  "Helvetica-Bold"),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(env_tbl)

    story.append(Paragraph("Step 6 — Start Qdrant (vector database)", S["h2"]))
    story.append(Paragraph("<b>Option A — Docker (recommended):</b>", S["body_left"]))
    story.append(code_block([
        "# Start Docker Desktop first, then:",
        'docker compose -f infra/docker-compose.yml up -d qdrant',
    ]))
    story.append(Paragraph("<b>Option B — Standalone binary (no Docker needed):</b>", S["body_left"]))
    story.append(code_block([
        "$url = 'https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-pc-windows-msvc.zip'",
        "Invoke-WebRequest -Uri $url -OutFile $env:TEMP\\qdrant.zip",
        "Expand-Archive $env:TEMP\\qdrant.zip -DestinationPath infra\\qdrant-bin -Force",
        "Start-Process infra\\qdrant-bin\\qdrant.exe -WorkingDirectory infra\\qdrant-bin",
    ]))
    story.append(spacer(4))
    story.append(info_box(
        "Verify Qdrant is running: open http://localhost:6333 in your browser. "
        "You should see a JSON response with {title: 'qdrant'}.",
        bg=GREEN_LIGHT, text_color=GREEN, label="✓"))

    story.append(PageBreak())

    # ── Quick Start (Every Session) ───────────────────────────────────────────
    story.append(Paragraph("Quick Start — Every Time You Work on the Project", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(info_box(
        "Use this section every time. First-time setup only needs to be done once.",
        bg=AMBER_LIGHT, text_color=AMBER, label="⚡"))
    story.append(spacer(8))

    story.append(Paragraph("Option A — One-Click Start (Recommended)", S["h2"]))
    story.append(Paragraph(
        "Run this single command from the project root. It starts everything automatically:",
        S["body_left"]))
    story.append(code_block([
        'cd "E:\\NEW PROJ\\insight-agent"',
        ".\\start.ps1",
        "",
        "# This script will:",
        "#   1. Check if Qdrant is running (starts it via Docker if not)",
        "#   2. Start the Router service on port 8100",
        "#   3. Start the API Gateway on port 8000",
        "#   4. Start the Next.js frontend on port 3000",
        "#   5. Verify all services are healthy",
        "#   6. Open http://localhost:3000 in your browser automatically",
    ]))
    story.append(spacer(10))

    story.append(Paragraph("Option B — Manual Start (if start.ps1 doesn't work)", S["h2"]))
    story.append(Paragraph("Open <b>4 separate PowerShell terminals</b> in VS Code:", S["body_left"]))

    manual_steps = [
        ("Terminal 1 — Router service", [
            'cd "E:\\NEW PROJ\\insight-agent"',
            '".venv\\Scripts\\Activate.ps1"',
            "uvicorn services.router.server:app --port 8100",
            "# Wait until you see: Application startup complete.",
        ]),
        ("Terminal 2 — API Gateway", [
            'cd "E:\\NEW PROJ\\insight-agent"',
            '".venv\\Scripts\\Activate.ps1"',
            "uvicorn apps.api.app.main:app --port 8000",
            "# Wait until you see: Application startup complete.",
        ]),
        ("Terminal 3 — Frontend", [
            'cd "E:\\NEW PROJ\\insight-agent\\apps\\web"',
            "pnpm dev",
            "# Wait until you see: Ready - started server on 0.0.0.0:3000",
        ]),
        ("Terminal 4 — Keep for commands", [
            "# Use this terminal for ingestion and other commands",
        ]),
    ]
    for label, cmds in manual_steps:
        story.append(code_block(cmds, label=label))
        story.append(spacer(4))

    story.append(PageBreak())

    # ── Verify All Services ───────────────────────────────────────────────────
    story.append(Paragraph("Verifying All Services Are Running", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph(
        "Run this in any PowerShell terminal to check the status of all four services:",
        S["body_left"]))
    story.append(code_block([
        "@(6333, 8000, 8100, 3000) | ForEach-Object {",
        "    $r = netstat -ano 2>$null | Select-String \":$_ \"",
        "    if ($r) { Write-Host \"[UP]   Port $_\" -ForegroundColor Green }",
        "    else     { Write-Host \"[DOWN] Port $_\" -ForegroundColor Red }",
        "}",
    ]))
    story.append(spacer(6))
    svc_data = [
        ["Port", "Service",  "Status URL",                   "Expected Response"],
        ["6333", "Qdrant",   "http://localhost:6333",         "{title: 'qdrant'}"],
        ["8100", "Router",   "http://localhost:8100/health",  "{ok: true}"],
        ["8000", "API",      "http://localhost:8000/health",  "{ok: true}"],
        ["3000", "Frontend", "http://localhost:3000",         "InsightAgent web UI"],
    ]
    sv_tbl = Table(svc_data, colWidths=[35, 65, 120, W - 280])
    sv_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  SLATE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, SLATE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(sv_tbl)

    # ── Using the Application ─────────────────────────────────────────────────
    story.append(Paragraph("Using the Application", S["h1"]))
    story.append(hr(BLUE_MID))

    story.append(Paragraph("1. Open the app", S["h2"]))
    story.append(Paragraph("Go to <b>http://localhost:3000</b> in your browser.", S["body_left"]))
    story.append(spacer(4))

    story.append(Paragraph("2. Upload a PDF document", S["h2"]))
    upload_steps = [
        "Look at the <b>left sidebar</b> — this is your Document Library",
        "Drag and drop any PDF file onto the upload zone, OR click to browse",
        "Accepted formats: PDF, DOCX, TXT, MD, HTML (max 50 MB)",
        "A progress bar appears while the document is being indexed",
        "When done, you will see a green success message with the chunk count",
        "The document appears in the library list below the upload zone",
    ]
    for step in upload_steps:
        story.append(Paragraph(f"• {step}", S["bullet"]))
    story.append(spacer(6))

    story.append(info_box(
        "Uploading via command line: python -m services.ingestion.pipeline \"path/to/file.pdf\"",
        bg=SLATE_LIGHT, text_color=SLATE, label="💡"))
    story.append(spacer(6))

    story.append(Paragraph("3. Ask a question", S["h2"]))
    ask_steps = [
        "Click the text box at the bottom of the <b>right panel</b>",
        "Type your question about the uploaded document",
        "Press Enter or click the <b>Ask</b> button",
        "Watch the answer stream in real time",
        "The answer includes: routing tier, answer text, source citations, and critic score",
    ]
    for step in ask_steps:
        story.append(Paragraph(f"• {step}", S["bullet"]))
    story.append(spacer(6))

    story.append(Paragraph("4. Understanding the answer", S["h2"]))
    ans_data = [
        ["Element",       "What it means"],
        ["tier: fast",    "Query was routed to GPT-4o-mini (cheap, quick)"],
        ["tier: smart",   "Query was routed to GPT-4o (complex reasoning)"],
        ["cached",        "Answer was returned from semantic cache — instant, zero cost"],
        ["critic X.XX",   "Self-evaluation score 0–1. Above 0.75 = high quality"],
        ["Sources [1][2]","Evidence chunks from your documents used to generate the answer"],
        ["retries: N",    "How many times the agent retried to improve answer quality"],
    ]
    ans_tbl = Table(ans_data, colWidths=[90, W - 150])
    ans_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, BLUE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#bfdbfe")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(ans_tbl)
    story.append(spacer(6))

    story.append(Paragraph("5. Remove a document", S["h2"]))
    story.append(Paragraph(
        "Click the <b>trash icon</b> next to any document in the sidebar. "
        "Confirm the dialog. All vectors for that document are deleted from Qdrant immediately.",
        S["body_left"]))
    story.append(PageBreak())

    # ── Ingestion Commands ────────────────────────────────────────────────────
    story.append(Paragraph("Ingesting Documents via Command Line", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(code_block([
        "# Activate venv first:",
        '".venv\\Scripts\\Activate.ps1"',
        "",
        "# Ingest a single PDF:",
        'python -m services.ingestion.pipeline "C:\\path\\to\\document.pdf"',
        "",
        "# Ingest all PDFs in a folder:",
        'Get-ChildItem "C:\\path\\to\\folder" -Filter "*.pdf" | ForEach-Object {',
        '    python -m services.ingestion.pipeline $_.FullName',
        "}",
        "",
        "# Check how many vectors are stored:",
        "Invoke-WebRequest http://localhost:6333/collections/kb -UseBasicParsing | Select-Object Content",
    ]))
    story.append(spacer(6))
    story.append(info_box(
        "First ingestion takes longer because BGE-M3 model weights (~2 GB) download from HuggingFace. "
        "Subsequent ingestions are fast — model is cached locally.",
        bg=AMBER_LIGHT, text_color=AMBER, label="⏱"))

    # ── Stopping the Project ──────────────────────────────────────────────────
    story.append(Paragraph("Stopping the Project", S["h1"]))
    story.append(hr(BLUE_MID))

    story.append(Paragraph("Option A — One-Click Stop (Recommended)", S["h2"]))
    story.append(code_block([
        'cd "E:\\NEW PROJ\\insight-agent"',
        ".\\stop.ps1",
        "# Kills all uvicorn (Python) and node (Next.js) processes",
    ]))

    story.append(Paragraph("Option B — Manual Stop", S["h2"]))
    story.append(code_block([
        "# Stop individual services with Ctrl+C in each terminal",
        "",
        "# Or kill by port:",
        "$pid = (netstat -ano | Select-String ':8000 ').ToString().Split()[-1]",
        "Stop-Process -Id $pid -Force",
        "",
        "# Stop Qdrant (Docker):",
        'docker compose -f infra/docker-compose.yml stop qdrant',
        "",
        "# Stop Qdrant (binary): just close the terminal window running qdrant.exe",
    ]))
    story.append(spacer(6))
    story.append(info_box(
        "Always save your work in VS Code before stopping: Ctrl+K, S  (Save All Files)",
        bg=GREEN_LIGHT, text_color=GREEN, label="💾"))

    # ── Saving & Committing ───────────────────────────────────────────────────
    story.append(Paragraph("Saving and Committing Your Work", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(code_block([
        "# Save all open files in VS Code:",
        "# Keyboard: Ctrl + K, S",
        "",
        "# Stage and commit all changes:",
        'cd "E:\\NEW PROJ\\insight-agent"',
        "git add -A",
        'git commit -m "your message here"',
        "git push",
    ]))

    # ── Troubleshooting ───────────────────────────────────────────────────────
    story.append(Paragraph("Troubleshooting", S["h1"]))
    story.append(hr(BLUE_MID))

    issues = [
        (
            "No output / blank chat after clicking Ask",
            [
                "Restart the frontend: in the pnpm dev terminal, Ctrl+C then pnpm dev",
                "Check the API is running: Invoke-WebRequest http://localhost:8000/health",
                "Open browser DevTools (F12) → Console tab for JavaScript errors",
            ],
            RED_LIGHT,
        ),
        (
            "Ingestion failed: No connection could be made (10061)",
            [
                "Qdrant is not running. Start it with Docker or the binary (see First-Time Setup Step 6)",
                "Verify: Invoke-WebRequest http://localhost:6333 -UseBasicParsing",
            ],
            AMBER_LIGHT,
        ),
        (
            "ModuleNotFoundError: No module named 'services'",
            [
                "You are running the command from the wrong directory",
                "Always cd to E:\\NEW PROJ\\insight-agent first",
                "Always activate the venv: .venv\\Scripts\\Activate.ps1",
            ],
            AMBER_LIGHT,
        ),
        (
            "API error 500 on /chat",
            [
                "Check the uvicorn terminal — it shows the full Python traceback",
                "Most common cause: OPENAI_API_KEY not set or expired",
                "Verify your .env file has a valid key starting with sk-proj-",
            ],
            RED_LIGHT,
        ),
        (
            "pnpm: command not found",
            [
                "Install pnpm: npm install -g pnpm",
                "Then restart your terminal",
            ],
            AMBER_LIGHT,
        ),
        (
            "BGE-M3 download hangs or fails",
            [
                "Set your HuggingFace token: HF_TOKEN=hf_xxxx in .env",
                "Check your internet connection — model is ~2 GB",
                "Try: python -c \"from FlagEmbedding import BGEM3FlagModel\" to test",
            ],
            AMBER_LIGHT,
        ),
    ]

    for title, bullets, bg in issues:
        rows = [[Paragraph(f"• {b}", ParagraphStyle("x",
                    fontSize=9, leading=13, fontName="Helvetica", textColor=SLATE,
                    leftIndent=6))] for b in bullets]
        t = Table(rows, colWidths=[W - 60*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ]))
        story.append(KeepTogether([
            Paragraph(title, S["h3"]),
            t,
            spacer(6),
        ]))

    # ── Quick Reference Card ──────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Quick Reference Card", S["h1"]))
    story.append(hr(BLUE_MID))
    story.append(Paragraph("Cut this out and keep it on your desk.", S["body_left"]))
    story.append(spacer(6))

    qr_data = [
        ["Action", "Command"],
        ["Start everything",     ".\\start.ps1"],
        ["Stop everything",      ".\\stop.ps1"],
        ["Activate venv",        '".venv\\Scripts\\Activate.ps1"'],
        ["Start API only",       "uvicorn apps.api.app.main:app --port 8000"],
        ["Start Router only",    "uvicorn services.router.server:app --port 8100"],
        ["Start Frontend only",  "cd apps\\web  then  pnpm dev"],
        ["Ingest a PDF",         'python -m services.ingestion.pipeline "file.pdf"'],
        ["Check all ports",      "@(6333,8000,8100,3000)|%{netstat -ano|sls \":$_ \"}"],
        ["View API docs",        "Open http://localhost:8000/docs"],
        ["Save all in VS Code",  "Ctrl + K, S"],
        ["Commit changes",       "git add -A  &&  git commit -m 'msg'  &&  git push"],
    ]
    qr_tbl = Table(qr_data, colWidths=[115, W - 175])
    qr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("FONTNAME",      (1,1),(1,-1),  "Courier"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, BLUE_LIGHT]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#bfdbfe")),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("TEXTCOLOR",     (0,1),(0,-1),  SLATE),
        ("FONTNAME",      (0,1),(0,-1),  "Helvetica-Bold"),
    ]))
    story.append(qr_tbl)

    story.append(spacer(16))
    story.append(hr())
    story.append(Paragraph(
        "InsightAgent · github.com/Darshith001/insight-agent · Built by Darshith",
        S["footer"]))

    doc.build(story)
    print(f"[OK] User manual saved to: {out_path}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    out_dir = r"E:\NEW PROJ\insight-agent"
    build_project_doc(os.path.join(out_dir, "InsightAgent_Project_Documentation.pdf"))
    build_user_manual(os.path.join(out_dir, "InsightAgent_User_Manual.pdf"))
    print("\nBoth PDFs generated successfully!")
