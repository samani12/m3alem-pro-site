"""Marrakech-focused SEO strategy engine.

Deterministic, explainable heuristics. Scores prioritize work; they are not ranking predictions.
"""
from __future__ import annotations
import re
import unicodedata
from collections import defaultdict

SERVICE_TERMS = {
    "climatisation": ("climatisation", "clim", "climatiseur", "air conditionne", "مكيف", "تكييف"),
    "electricite": ("electricien", "electricite", "panne electrique", "كهربائي", "كهرباء"),
    "plomberie": ("plombier", "plomberie", "fuite", "chauffe eau", "سباك", "تسرب"),
    "refrigeration": ("froid commercial", "refrigeration", "frigo", "chambre froide", "ثلاجة"),
    "electromenager": ("electromenager", "lave linge", "machine a laver", "refrigerateur"),
    "videosurveillance": ("camera", "videosurveillance", "camera surveillance", "كاميرات", "مراقبة"),
}
LOCAL_TERMS = ("marrakech", "marrakesh", "مراكش", "guéliz", "gueliz", "hivernage", "targa", "daoudiate", "massira", "safi")
BUY_INTENT = ("prix", "tarif", "devis", "installation", "reparation", "depannage", "urgence", "technicien", "service", "near me", "قريب", "ثمن", "إصلاح", "اصلاح", "تركيب", "تقني", "فني", "صيانة", "خدمة", "تصليح")
INFO_INTENT = ("comment", "pourquoi", "guide", "definition", "ما هو", "كيف")

PAGE_MAP = {
    "climatisation": "climatisation-marrakech.html",
    "electricite": "electricien-marrakech.html",
    "plomberie": "plombier-marrakech.html",
    "refrigeration": "refrigeration-marrakech.html",
    "electromenager": "electromenager-marrakech.html",
    "videosurveillance": "videosurveillance-marrakech.html",
}

def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "").lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    # Normalize common Arabic alef/ya variants before matching user queries.
    value = value.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()

def classify_query(query: str) -> dict:
    q = normalize_text(query)
    services = []
    for service, terms in SERVICE_TERMS.items():
        if any(normalize_text(term) in q for term in terms):
            services.append(service)
    local = any(normalize_text(term) in q for term in LOCAL_TERMS)
    transactional = any(normalize_text(term) in q for term in BUY_INTENT)
    informational = any(normalize_text(term) in q for term in INFO_INTENT)
    return {
        "query": query,
        "services": services,
        "local_intent": local,
        "transactional_intent": transactional,
        "informational_intent": informational,
        "intent": "transactional" if transactional else ("informational" if informational else ("local" if local else "general")),
    }

def opportunity_score(query: str, impressions=0, clicks=0, ctr=0, position=0) -> dict:
    """0-100 priority heuristic, with every factor exposed for auditability."""
    classified = classify_query(query)
    imp = max(0.0, float(impressions or 0))
    clk = max(0.0, float(clicks or 0))
    ctr = max(0.0, min(1.0, float(ctr or 0)))
    pos = max(0.0, float(position or 0))
    volume = min(25.0, 25 * (1 - 2.718281828 ** (-imp / 400)))
    local = 20.0 if classified["local_intent"] else 0.0
    service = 20.0 if classified["services"] else 0.0
    intent = 15.0 if classified["transactional_intent"] else (7.0 if classified["informational_intent"] else 0.0)
    ctr_gap = min(10.0, max(0.0, 0.06 - ctr) * 166.67)
    position_fit = 10.0 if 4 <= pos <= 20 else (5.0 if 1 <= pos < 4 else 0.0)
    click_signal = min(5.0, clk / 10)
    total = round(min(100.0, volume + local + service + intent + ctr_gap + position_fit + click_signal), 1)
    return {
        **classified,
        "score": total,
        "factors": {
            "search_demand": round(volume, 1),
            "marrakech_locality": local,
            "service_match": service,
            "commercial_intent": intent,
            "ctr_headroom": round(ctr_gap, 1),
            "ranking_opportunity": position_fit,
            "click_signal": round(click_signal, 1),
        },
        "recommended_page": PAGE_MAP.get(classified["services"][0]) if classified["services"] else None,
        "priority": "high" if total >= 65 else ("medium" if total >= 35 else "low"),
    }

def analyze_queries(rows):
    """Analyze GSC-like rows. Accepts query/clicks/impressions/ctr/position keys."""
    results = []
    for row in rows:
        result = opportunity_score(
            row.get("query", ""), row.get("impressions", 0), row.get("clicks", 0),
            row.get("ctr", 0), row.get("position", row.get("average_position", 0))
        )
        results.append(result)
    return sorted(results, key=lambda x: x["score"], reverse=True)

def build_service_keyword_map(queries):
    """Return one canonical target page per query and flag possible page overlap."""
    grouped = defaultdict(list)
    for item in analyze_queries(queries):
        if item["recommended_page"]:
            grouped[item["recommended_page"]].append(item["query"])
    return dict(grouped)

def generate_content_brief(service: str, area: str = "Marrakech") -> dict:
    if service not in PAGE_MAP:
        raise ValueError("Unknown service category")
    labels = {
        "climatisation": "Climatisation",
        "electricite": "Électricité",
        "plomberie": "Plomberie",
        "refrigeration": "Réfrigération",
        "electromenager": "Électroménager",
        "videosurveillance": "Vidéosurveillance",
    }
    name = labels[service]
    return {
        "target_page": PAGE_MAP[service],
        "primary_topic": f"{name} à {area}",
        "title_idea": f"{name} à {area} | Installation, dépannage et entretien",
        "sections": [
            f"Services de {name.lower()} proposés à {area}",
            "Pannes et problèmes traités",
            "Déroulement du diagnostic et de l'intervention",
            "Zones réellement desservies",
            "Tarifs: expliquer les facteurs, sans prix inventés",
            "Questions fréquentes basées sur les demandes clients",
        ],
        "conversion_elements": ["appel téléphonique", "WhatsApp", "zone desservie", "horaires réels", "garantie uniquement si applicable"],
        "guardrails": ["ne pas inventer d'avis, d'adresse, de prix ou de disponibilité", "ne pas créer de pages de quartier quasi-identiques", "faire valider le contenu avant publication"],
    }
