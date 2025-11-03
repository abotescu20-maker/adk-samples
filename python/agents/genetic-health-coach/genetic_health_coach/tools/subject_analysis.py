"""Domain knowledge helpers for subject specific recommendations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SubjectKnowledge:
    """Static domain guidance for a gene and subject combination."""

    argument: str
    recommendations: List[str]
    risk_notes: Optional[str] = None
    benefit_notes: Optional[str] = None


SUBJECT_KNOWLEDGE: Dict[str, Dict[str, SubjectKnowledge]] = {
    "nutriție": {
        "MTHFR": SubjectKnowledge(
            argument=(
                "{gene} cu variante precum {mutations} indică o activitate redusă a enzimei "
                "metilentetrahidrofolat reductază; impact raportat: {impact}. Aceasta poate "
                "încetini conversia folatului în forma sa metilată, crescând homocisteina și "
                "necesarul de vitamine B metilate."
            ),
            risk_notes=(
                "Riscurile includ deficite de metilare, oboseală și sensibilitate crescută la "
                "toxine dacă nu este optimizat aportul de folat/B12."
            ),
            benefit_notes=(
                "Intervențiile nutriționale adecvate pot susține sinteza neurotransmițătorilor și "
                "protejarea cardiovasculară."
            ),
            recommendations=[
                "Suplimentați cu 400-800 mcg 5-MTHF sau acid folic metilat, monitorizat medical.",
                "Includeți surse bogate în folat natural: legume verzi, sparanghel, avocado.",
                "Asociați cu vitaminele B2, B6 și B12 metilate pentru a susține ciclul metilării.",
                "Monitorizați periodic nivelul homocisteinei și ajustați intervențiile în funcție de rezultate.",
            ],
        ),
        "FTO": SubjectKnowledge(
            argument=(
                "{gene} cu variante {mutations} este asociat cu reglarea apetitului și a stocării "
                "de lipide. Impactul observat ({impact}) sugerează un risc mai mare de creștere în "
                "greutate dacă aportul caloric și calitatea macronutrienților nu sunt controlate."
            ),
            risk_notes=(
                "Poate apărea rezistență la insulină și dificultăți în menținerea greutății în lipsa "
                "unei diete bogate în fibre și proteine."
            ),
            benefit_notes=(
                "Structurarea meselor și reglarea aportului de carbohidrați contribuie la controlul apetitului."
            ),
            recommendations=[
                "Adoptați un plan alimentar cu indice glicemic moderat, bogat în proteine magre și fibre.",
                "Structurați mesele cu un mic dejun bogat în proteine pentru a reduce poftele din a doua parte a zilei.",
                "Monitorizați aportul total de calorii și utilizați jurnal alimentar pentru conștientizare.",
                "Prioritizați grăsimile nesaturate (ulei de măsline, nuci) și limitați zaharurile rafinate.",
            ],
        ),
        "VDR": SubjectKnowledge(
            argument=(
                "{gene} afectat de {mutations} influențează răspunsul la vitamina D. Impactul {impact} "
                "poate reduce eficiența absorbției și semnalizării, necesitând un aport mai atent de vitamina D și calciu."
            ),
            risk_notes=(
                "Poate exista un risc crescut de densitate minerală osoasă scăzută și răspuns imun suboptimal fără optimizare."
            ),
            benefit_notes=(
                "Corectarea statusului vitaminei D sprijină metabolismul calciului și funcția musculară."
            ),
            recommendations=[
                "Verificați nivelul seric 25(OH)D și suplimentați pentru a menține valori între 40-60 ng/mL.",
                "Includeți surse de vitamina D (pește gras, ouă) și calciu (legume verzi, semințe de susan).",
                "Asigurați expunere moderată la soare și activitate fizică cu impact pentru sănătatea oaselor.",
            ],
        ),
    },
    "sport": {
        "ACTN3": SubjectKnowledge(
            argument=(
                "Varianta {mutations} în {gene} este asociată cu fibre musculare lente și adaptări "
                "pentru eforturi de anduranță; impactul menționat ({impact}) sugerează mai puțină "
                "activitate alfa-actinină-3 pentru explozii de putere."
            ),
            risk_notes=(
                "Sporturile exclusiv de forță pot duce la suprasolicitare și recuperare lentă."
            ),
            benefit_notes=(
                "Antrenamentul de rezistență și periodizarea volumului cresc eficiența oxidativă."
            ),
            recommendations=[
                "Prioritizați activități de anduranță: alergare ușoară, ciclism, înot în ritm constant.",
                "Introduceți antrenamente de forță cu greutăți moderate pentru stabilitate, evitând volume explozive excesive.",
                "Utilizați strategii de recuperare (stretching, masaj, somn >7h) pentru a preveni accidentările."
            ],
        ),
        "IL6": SubjectKnowledge(
            argument=(
                "{gene} cu variante {mutations} influențează răspunsul inflamator post-exercițiu; impactul {impact} poate prelungi "
                "timpul de recuperare și necesarul de antioxidanți."
            ),
            risk_notes="Inflamația persistentă poate afecta adaptările musculare și sistemul imunitar.",
            benefit_notes="Gestionarea inflamației susține progresul și reduce riscul de supraantrenament.",
            recommendations=[
                "Planificați zile de recuperare activă și monitorizați semnele de inflamație (durere persistentă, CRP).",
                "Includeți alimente antiinflamatorii (pește gras, turmeric, ghimbir) și omega-3 (1-2 g EPA/DHA).",
                "Mențineți hidratarea și folosiți monitorizarea ritmului cardiac pentru a ajusta intensitatea.",
            ],
        ),
        "VDR": SubjectKnowledge(
            argument=(
                "{gene} cu {mutations} poate reduce sensibilitatea receptorilor la vitamina D; impactul {impact} afectează forța "
                "musculară și contracția eficientă, mai ales în sporturile care necesită coordonare fină."
            ),
            risk_notes="Deficiențele de vitamina D pot crește riscul de fracturi și slăbiciune musculară.",
            benefit_notes="Optimizarea vitaminei D îmbunătățește funcția neuromusculară și recuperarea.",
            recommendations=[
                "Integrați exerciții pliometrice ușoare și antrenamente de echilibru pentru a stimula recrutarea neuromusculară.",
                "Asigurați aport suficient de vitamina D și calciu pentru susținerea contracțiilor musculare.",
                "Monitorizați forța de prindere sau săritura verticală pentru a evalua adaptările.",
            ],
        ),
    },
    "terapii": {
        "COMT": SubjectKnowledge(
            argument=(
                "{gene} cu variante {mutations} sugerează o activitate modificată a catecol-O-metiltransferazei; impactul {impact} "
                "poate încetini degradarea dopaminei și adrenalinei, influențând toleranța la stres și răspunsul la terapii."
            ),
            risk_notes="Nivelurile crescute de catecolamine pot crește anxietatea sau sensibilitatea la durere.",
            benefit_notes="Intervențiile de reglare a stresului pot echilibra neurotransmițătorii și sistemul autonom.",
            recommendations=[
                "Utilizați terapii de gestionare a stresului (respirație coerentă, mindfulness) pentru a stabiliza nivelul catecolaminelor.",
                "Luați în considerare suplimentarea cu magneziu glicinat (200-400 mg) pentru relaxare neuromusculară.",
                "Sprijiniți metilarea cu forme active de vitamine B (B6, B12, folat) și cofactori (SAMe) sub supraveghere medicală.",
            ],
        ),
        "MTHFR": SubjectKnowledge(
            argument=(
                "{gene} cu {mutations} relevă o capacitate scăzută de metilare; impactul {impact} poate influența răspunsul la "
                "terapii hormonale, detoxifiere și regenerare celulară."
            ),
            risk_notes="Suplimentele cu acid folic simplu pot fi mai puțin eficiente; monitorizați reacțiile la terapii intensive.",
            benefit_notes="Personalizarea terapiilor cu suport de metilare crește toleranța și rezultatele clinice.",
            recommendations=[
                "Înainte de terapii solicitante (chelație, detoxifiere), susțineți metilarea cu 5-MTHF și vitamina B12 metilată.",
                "Adăugați NAC și glutation lipozomal pentru a sprijini fazele II de detoxifiere dacă este indicat medical.",
                "Consultați un specialist pentru ajustarea dozelor de hormoni bioidentici în funcție de statusul de metilare.",
            ],
        ),
        "SOD2": SubjectKnowledge(
            argument=(
                "{gene} cu {mutations} afectează enzima superoxid dismutază mitocondrială; impactul {impact} poate diminua "
                "capacitatea antioxidativă, necesitând suport în terapiile oxidative sau radiante."
            ),
            risk_notes="Stresul oxidativ crescut poate agrava oboseala și inflamația în timpul terapiilor intensive.",
            benefit_notes="Suportul antioxidant țintit crește reziliența mitocondrială și calitatea vieții.",
            recommendations=[
                "Introduceți suplimentare cu coenzima Q10, N-acetilcisteină și vitamina C în protocolul terapeutic.",
                "Folosiți terapii cu lumină roșie sau saună infraroșie cu monitorizare pentru a stimula mitocondriile.",
                "Evaluați markerii de stres oxidativ (8-OHdG, F2-isoprostani) pentru a ajusta intervențiile.",
            ],
        ),
    },
}


def _normalise_gene_payload(gene_payload: Any) -> List[Dict[str, Any]]:
    if gene_payload is None:
        return []
    if isinstance(gene_payload, str):
        try:
            data = json.loads(gene_payload)
        except json.JSONDecodeError:
            return []
        return _normalise_gene_payload(data)
    if isinstance(gene_payload, dict):
        if "genes" in gene_payload:
            return _normalise_gene_payload(gene_payload["genes"])
        return [gene_payload]
    if isinstance(gene_payload, list):
        normalised: List[Dict[str, Any]] = []
        for item in gene_payload:
            if isinstance(item, dict):
                normalised.append(item)
        return normalised
    return []


def _summarise_variant(variant: Dict[str, Any]) -> str:
    components: List[str] = []
    if variant.get("vid"):
        components.append(str(variant["vid"]))
    position = variant.get("position")
    if variant.get("chrom") and position:
        components.append(f"{variant['chrom']}:{position}")
    if variant.get("ref") and variant.get("alt"):
        components.append(f"{variant['ref']}>{variant['alt']}")
    if variant.get("genotype"):
        components.append(f"genotip {variant['genotype']}")
    if variant.get("impact"):
        components.append(f"impact {variant['impact'].lower()}")
    effects = variant.get("effects") or []
    if effects:
        components.append("/".join(effects))
    annotations = variant.get("annotations") or []
    hgvs_entries = {
        ann.get("hgvs_p") or ann.get("hgvs_c")
        for ann in annotations
        if ann.get("hgvs_p") or ann.get("hgvs_c")
    }
    hgvs_entries.discard(None)
    if hgvs_entries:
        components.append("; ".join(sorted(hgvs_entries)))
    return ", ".join(components)


def build_subject_report(subject: str, gene_payload: Any) -> Dict[str, Any]:
    """Return structured guidance for a subject based on gene variants."""

    if not subject:
        raise ValueError("Subiectul analizat trebuie specificat.")
    subject_key = subject.strip().lower()
    knowledge = SUBJECT_KNOWLEDGE.get(subject_key)
    if not knowledge:
        raise ValueError(
            "Subiect neacoperit. Folosește doar 'sport', 'nutriție' sau 'terapii'."
        )

    genes = _normalise_gene_payload(gene_payload)
    gene_map: Dict[str, Dict[str, Any]] = {}
    for item in genes:
        gene_name = item.get("gene") or item.get("symbol")
        if not gene_name:
            continue
        gene_map[gene_name.upper()] = item

    entries: List[Dict[str, Any]] = []
    argument_parts: List[str] = []
    all_recommendations: List[str] = []
    irrelevant_genes: List[str] = []

    for gene_name, data in gene_map.items():
        guidance = knowledge.get(gene_name)
        variants = data.get("variants", [])
        variant_summaries = [
            _summarise_variant(variant)
            for variant in variants
            if isinstance(variant, dict)
        ]
        mutation_text = "; ".join([v for v in variant_summaries if v]) or "varianta raportată"
        impacts = [
            ann.get("impact")
            for variant in variants
            for ann in variant.get("annotations", [])
            if ann.get("impact")
        ]
        if not impacts:
            impacts = [variant.get("impact") for variant in variants if variant.get("impact")]
        impact_text = ", ".join(dict.fromkeys(i for i in impacts if i)) or "nespecificat"

        if guidance:
            argument = guidance.argument.format(
                gene=gene_name,
                mutations=mutation_text,
                impact=impact_text,
            )
            if guidance.risk_notes:
                argument += f" {guidance.risk_notes}"
            if guidance.benefit_notes:
                argument += f" {guidance.benefit_notes}"
            argument_parts.append(argument)

            entries.append(
                {
                    "gene": gene_name,
                    "mutations": variant_summaries,
                    "argument": argument,
                    "recommendations": guidance.recommendations,
                }
            )
            for rec in guidance.recommendations:
                if rec not in all_recommendations:
                    all_recommendations.append(rec)
        else:
            irrelevant_genes.append(gene_name)

    summary_argument = " ".join(argument_parts)
    return {
        "subject": subject_key,
        "entries": entries,
        "summary_argument": summary_argument,
        "recommendations": all_recommendations,
        "irrelevant_genes": sorted(irrelevant_genes),
    }


__all__ = ["build_subject_report"]
