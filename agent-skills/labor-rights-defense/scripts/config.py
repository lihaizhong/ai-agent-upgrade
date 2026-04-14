from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProcedureSeeds:
    version: int
    seeds: list[dict]


def load_procedure_seeds(skill_dir: Path) -> ProcedureSeeds:
    path = skill_dir / "reference" / "procedure-seeds.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = int(payload.get("version", 0))
    seeds = payload.get("seeds", [])
    if not isinstance(seeds, list):
        raise ValueError("procedure seeds: seeds must be a list")
    return ProcedureSeeds(version=version, seeds=seeds)


def find_province_seeds(seeds: ProcedureSeeds, province: str) -> dict | None:
    for item in seeds.seeds:
        if item.get("province") == province:
            return item
    return None

