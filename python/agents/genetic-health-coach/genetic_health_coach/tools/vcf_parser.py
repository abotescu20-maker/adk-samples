"""Utility functions for parsing annotated VCF files."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional

ANN_FIELDS = [
    "allele",
    "effect",
    "impact",
    "gene",
    "gene_id",
    "feature_type",
    "feature_id",
    "transcript_biotype",
    "rank",
    "hgvs_c",
    "hgvs_p",
    "cdna_pos",
    "cdna_len",
    "cds_pos",
    "cds_len",
    "aa_pos",
    "aa_len",
    "distance",
    "errors",
]


@dataclass
class Variant:
    """Internal representation of a variant."""

    chrom: str
    position: int
    ref: str
    alt: str
    vid: Optional[str]
    genotype: Optional[str]
    annotations: List[Dict[str, Optional[str]]]
    effects: List[str]
    impact: Optional[str]
    clinical_significance: Optional[str]

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        return data


def _parse_info_field(info_value: str) -> Dict[str, str]:
    info: Dict[str, str] = {}
    if not info_value:
        return info
    for item in info_value.split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            info[key] = value
        else:
            info[item] = "true"
    return info


def _parse_ann_field(ann_value: str | None) -> List[Dict[str, Optional[str]]]:
    if not ann_value:
        return []
    annotations: List[Dict[str, Optional[str]]] = []
    for ann_record in ann_value.split(","):
        parts = ann_record.split("|")
        padded = parts + [None] * (len(ANN_FIELDS) - len(parts))
        annotations.append({field: padded[idx] for idx, field in enumerate(ANN_FIELDS)})
    return annotations


def _extract_gene_symbols(info: Dict[str, str], annotations: Iterable[Dict[str, Optional[str]]]) -> List[str]:
    gene_candidates: set[str] = set()
    gene_regex = re.compile(r"[^A-Za-z0-9_-]+")

    for key, value in info.items():
        lowered = key.lower()
        if any(marker in lowered for marker in ("gene", "symbol", "hgnc")):
            for token in re.split(r"[|,/&]", value):
                cleaned = gene_regex.sub("", token.strip())
                if cleaned:
                    if ":" in cleaned:
                        cleaned = cleaned.split(":")[-1]
                    gene_candidates.add(cleaned.upper())
        if lowered == "geneinfo":
            for pair in value.split("|"):
                if ":" in pair:
                    _, symbol = pair.split(":", 1)
                    cleaned = gene_regex.sub("", symbol.strip())
                    if cleaned:
                        gene_candidates.add(cleaned.upper())
    for annotation in annotations:
        gene = annotation.get("gene")
        if gene:
            gene_candidates.add(gene.upper())
    return sorted(gene_candidates)


def _build_variant(
    chrom: str,
    pos: str,
    vid: str,
    ref: str,
    alt: str,
    info: Dict[str, str],
    sample_format: List[str],
    sample_values: List[str],
    annotations: List[Dict[str, Optional[str]]],
) -> Variant:
    genotype = None
    if sample_format and sample_values:
        format_map = dict(zip(sample_format, sample_values))
        genotype = format_map.get("GT")

    gene_annotations = [
        {
            "gene": ann.get("gene"),
            "effect": ann.get("effect"),
            "impact": ann.get("impact"),
            "hgvs_c": ann.get("hgvs_c"),
            "hgvs_p": ann.get("hgvs_p"),
            "transcript": ann.get("feature_id"),
        }
        for ann in annotations
    ]
    effects = sorted({ann.get("effect") for ann in annotations if ann.get("effect")})
    impact = None
    for ann in annotations:
        candidate = ann.get("impact")
        if candidate:
            impact = candidate
            break

    return Variant(
        chrom=chrom,
        position=int(pos),
        ref=ref,
        alt=alt,
        vid=None if vid in {".", ""} else vid,
        genotype=genotype,
        annotations=gene_annotations,
        effects=effects,
        impact=impact,
        clinical_significance=info.get("CLNSIG"),
    )


def extract_gene_variants(vcf_path: str) -> Dict[str, object]:
    """Parse a VCF file and return gene-to-variant mappings.

    Args:
        vcf_path: Path to the annotated VCF file.

    Returns:
        Dictionary containing the discovered genes and their associated variants.
    """

    if not vcf_path:
        raise ValueError("Trebuie să specifici calea către fișierul VCF.")
    resolved_path = os.path.expanduser(vcf_path)
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Fișierul VCF nu a fost găsit: {vcf_path}")

    genes: Dict[str, List[Dict[str, object]]] = {}
    total_variants = 0

    with open(resolved_path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            if len(fields) < 8:
                continue
            chrom, pos, vid, ref, alt, _qual, _filter, info_field = fields[:8]
            sample_format: List[str] = []
            sample_values: List[str] = []
            if len(fields) >= 10:
                sample_format = fields[8].split(":") if fields[8] else []
                sample_values = fields[9].split(":") if fields[9] else []

            info_map = _parse_info_field(info_field)
            annotations = _parse_ann_field(info_map.get("ANN"))
            variant = _build_variant(
                chrom=chrom,
                pos=pos,
                vid=vid,
                ref=ref,
                alt=alt,
                info=info_map,
                sample_format=sample_format,
                sample_values=sample_values,
                annotations=annotations,
            )
            gene_symbols = _extract_gene_symbols(info_map, annotations)
            if not gene_symbols:
                gene_symbols = ["NECUNOSCUT"]

            for gene in gene_symbols:
                gene_annotations = [
                    ann for ann in variant.annotations if ann.get("gene", "").upper() == gene
                ]
                gene_variant = variant.to_dict()
                if gene_annotations:
                    gene_variant["annotations"] = gene_annotations
                genes.setdefault(gene, []).append(gene_variant)
                total_variants += 1

    return {
        "vcf_path": vcf_path,
        "total_variants": total_variants,
        "genes": [
            {
                "gene": gene,
                "variant_count": len(variants),
                "variants": variants,
            }
            for gene, variants in sorted(genes.items())
        ],
        "summary": f"Identificate {len(genes)} gene cu mutații raportate.",
    }


def main() -> None:
    """Helper for manual testing from the command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Extrage genele dintr-un VCF adnotat.")
    parser.add_argument("vcf_path", help="Calea către fișierul VCF")
    args = parser.parse_args()
    result = extract_gene_variants(args.vcf_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
