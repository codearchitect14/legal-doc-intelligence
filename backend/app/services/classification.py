from sentence_transformers import SentenceTransformer, util

from app.core.config import get_settings

# Fixed category prototypes matching PROJECT_PLAN_v2.md Section 6's document
# categories. Escalation to the LLM router for genuinely ambiguous cases is
# Phase 4 scope (see PROJECT_PLAN_v2.md Section 10.1) - for now, anything
# below CONFIDENCE_THRESHOLD is returned as "uncertain".
CATEGORY_PROTOTYPES: dict[str, str] = {
    "medical_record": "Doctor's clinical notes, diagnosis, treatment history, patient visit summary, hospital discharge report",
    "bill": "Invoice or billing statement showing amount due, itemized charges, payment terms, provider or vendor name",
    "wage_record": "Pay stub or wage statement showing hours worked, hourly rate, gross and net pay, employer name",
    "correspondence": "Letter or email exchanged between parties, containing a date, sender, recipient, and a written message",
    "contract": "Signed agreement between two or more parties defining terms, obligations, effective date, and signatures",
    "filing": "Court filing such as a complaint, motion, or judgment, referencing case number, court name, and parties",
}

# Hybrid signal alongside the semantic prototypes above: on a real document
# (an insurance Explanation of Benefits), pure embedding similarity picked
# "wage_record" over "bill" by a razor-thin margin (0.523 vs 0.507) despite
# the document containing none of a pay stub's actual vocabulary and
# several unambiguous billing phrases. A small number of highly distinctive,
# category-specific phrases resolves exactly this kind of near-tie without
# touching the semantic model or its threshold. Validated against every
# real sample document in data/sample_case_folder before adding this: fixes
# the EOB misclassification, correctly promotes two other real documents
# (a blank W-2 - itself titled "Wage and Tax Statement" - and a real
# medical consult note) from "uncertain" into their actually-correct
# category, and changes nothing for the four categories that were already
# classifying correctly.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "medical_record": [
        "diagnosis",
        "patient",
        "clinical",
        "treatment history",
        "discharge summary",
        "physician",
        "prescribed",
        "symptoms",
    ],
    "bill": [
        "explanation of benefits",
        "itemized",
        "amount due",
        "invoice",
        "total charges",
        "billed amount",
        "balance due",
        "this is not a bill",
        "good faith estimate",
        "billed charges",
    ],
    "wage_record": [
        "pay stub",
        "gross pay",
        "net pay",
        "hourly rate",
        "hours worked",
        "overtime",
        "wage statement",
        "wage and tax statement",
        "employer name",
        "regular rate of pay",
        "back wages",
    ],
    "correspondence": ["dear ", "sincerely", "best regards", "yours truly"],
    "contract": [
        "this agreement",
        "the parties",
        "whereas",
        "hereby agree",
        "effective date",
        "terms and conditions",
        "witness whereof",
    ],
    "filing": [
        "plaintiff",
        "defendant",
        "docket no",
        "case no",
        "court of appeals",
        "motion to",
        "hereby ordered",
        "supreme court",
    ],
}
KEYWORD_BOOST_PER_MATCH = 0.08
MAX_KEYWORD_BOOST = 0.24

UNCERTAIN_CATEGORY = "uncertain"
CONFIDENCE_THRESHOLD = 0.35
CHUNK_SIZE_CHARS = 500
CHUNK_OVERLAP_CHARS = 50

_model: SentenceTransformer | None = None
_prototype_embeddings = None
_prototype_labels: list[str] = []


def _get_model() -> SentenceTransformer:
    global _model, _prototype_embeddings, _prototype_labels
    if _model is None:
        _model = SentenceTransformer(get_settings().embedding_model_name)
        _prototype_labels = list(CATEGORY_PROTOTYPES.keys())
        _prototype_embeddings = _model.encode(
            list(CATEGORY_PROTOTYPES.values()), convert_to_tensor=True
        )
    return _model


def _keyword_boost(text_lower: str, category: str) -> float:
    hits = sum(1 for keyword in CATEGORY_KEYWORDS.get(category, []) if keyword in text_lower)
    return min(hits * KEYWORD_BOOST_PER_MATCH, MAX_KEYWORD_BOOST)


def classify(text: str) -> tuple[str, float]:
    """Classify text by cosine similarity to fixed category prototypes,
    with a small keyword boost per category layered on top (see
    CATEGORY_KEYWORDS above for why)."""
    model = _get_model()
    if not text.strip():
        return UNCERTAIN_CATEGORY, 0.0

    text_embedding = model.encode(text, convert_to_tensor=True)
    semantic_scores = util.cos_sim(text_embedding, _prototype_embeddings)[0].tolist()
    text_lower = text.lower()
    combined_scores = [
        semantic_scores[i] + _keyword_boost(text_lower, label)
        for i, label in enumerate(_prototype_labels)
    ]

    best_index = max(range(len(combined_scores)), key=lambda i: combined_scores[i])
    best_score = combined_scores[best_index]

    if best_score < CONFIDENCE_THRESHOLD:
        return UNCERTAIN_CATEGORY, best_score
    return _prototype_labels[best_index], best_score


def _chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE_CHARS
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE_CHARS - CHUNK_OVERLAP_CHARS
    return chunks


def chunk_and_embed(text: str) -> list[tuple[str, list[float]]]:
    """Split text into overlapping chunks and embed each, for pgvector storage."""
    model = _get_model()
    chunks = _chunk_text(text)
    if not chunks:
        return []
    embeddings = model.encode(chunks, convert_to_tensor=False)
    return list(zip(chunks, [embedding.tolist() for embedding in embeddings]))
