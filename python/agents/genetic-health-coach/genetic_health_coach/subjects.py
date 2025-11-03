"""Common subject metadata and helpers."""

from __future__ import annotations

from typing import Iterable, List

AVAILABLE_SUBJECTS: dict[str, str] = {
    "sport": "Sport",
    "nutriție": "Nutriție",
    "terapii": "Terapii",
}

SUBJECT_SYNONYMS: dict[str, str] = {
    "nutritie": "nutriție",
    "terapie": "terapii",
}


def normalise_subjects(subjects: Iterable[str] | None) -> List[str]:
    """Return a canonical list of requested subjects."""

    if not subjects:
        return list(AVAILABLE_SUBJECTS.keys())

    normalised: List[str] = []
    for subject in subjects:
        if not subject:
            continue
        key = subject.strip().lower()
        if key in AVAILABLE_SUBJECTS:
            canonical = key
        else:
            canonical = SUBJECT_SYNONYMS.get(key, key)
        if canonical not in AVAILABLE_SUBJECTS:
            continue
        if canonical not in normalised:
            normalised.append(canonical)
    return normalised or list(AVAILABLE_SUBJECTS.keys())


__all__ = ["AVAILABLE_SUBJECTS", "SUBJECT_SYNONYMS", "normalise_subjects"]

