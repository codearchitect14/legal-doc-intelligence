from sentence_transformers import SentenceTransformer, util

from app.core.config import get_settings

# Fixed category prototypes matching PROJECT_PLAN_v2.md Section 6's document
# categories. Escalation to the LLM router for genuinely ambiguous cases is
# Phase 4 scope (see PROJECT_PLAN_v2.md Section 10.1) — for now, anything
# below CONFIDENCE_THRESHOLD is returned as "uncertain".
CATEGORY_PROTOTYPES: dict[str, str] = {
    "medical_record": "Doctor's clinical notes, diagnosis, treatment history, patient visit summary, hospital discharge report",
    "bill": "Invoice or billing statement showing amount due, itemized charges, payment terms, provider or vendor name",
    "wage_record": "Pay stub or wage statement showing hours worked, hourly rate, gross and net pay, employer name",
    "correspondence": "Letter or email exchanged between parties, containing a date, sender, recipient, and a written message",
    "contract": "Signed agreement between two or more parties defining terms, obligations, effective date, and signatures",
    "filing": "Court filing such as a complaint, motion, or judgment, referencing case number, court name, and parties",
}
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


def classify(text: str) -> tuple[str, float]:
    """Classify text by cosine similarity to fixed category prototypes."""
    model = _get_model()
    if not text.strip():
        return UNCERTAIN_CATEGORY, 0.0

    text_embedding = model.encode(text, convert_to_tensor=True)
    scores = util.cos_sim(text_embedding, _prototype_embeddings)[0]
    best_index = int(scores.argmax())
    best_score = float(scores[best_index])

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
