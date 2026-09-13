#!/usr/bin/env python3
"""Convert a reviewed daily report into safe, public GitHub Pages data.

The input is the private/local reviewed_articles.json produced by the
research-paper-daily-push skill. This script deliberately copies only the
fields needed by the public radar and never copies PDFs, local paths, or
research-profile configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INSPIRATION_KEYS = (
    "experimental_design",
    "methods",
    "key_entities_mechanisms",
    "target_system",
    "future_direction",
    "paper_potential",
    "limitations_validation",
)


def as_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def as_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def safe_url(value: Any) -> str:
    value = as_text(value)
    if value.startswith("https://") or value.startswith("http://"):
        return value
    return ""


def score_map(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for key, raw in value.items():
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            result[str(key)] = max(0, min(100, int(raw)))
    return result


def public_terms(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if not isinstance(item, dict):
            continue
        term = as_text(item.get("term"))
        academic = as_text(item.get("academic_explanation"))
        plain = as_text(item.get("plain_explanation"))
        if term and (academic or plain):
            result.append(
                {
                    "term": term,
                    "academic_explanation": academic,
                    "plain_explanation": plain,
                }
            )
    return result


def public_inspiration(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    return {key: as_text_list(value.get(key)) for key in INSPIRATION_KEYS if as_text_list(value.get(key))}


def public_article(article: Any) -> dict[str, Any]:
    if not isinstance(article, dict):
        return {}
    doi = as_text(article.get("doi"))
    url = safe_url(article.get("url"))
    if not url and doi:
        url = f"https://doi.org/{doi}"
    return {
        "title": as_text(article.get("title")),
        "chinese_title": as_text(article.get("chinese_title")),
        "journal": as_text(article.get("journal")),
        "publication_date": as_text(article.get("publication_date")),
        "doi": doi,
        "url": url,
        "article_type": as_text(article.get("article_type")),
        "recommendation_score": article.get("recommendation_score", 0),
        "score_status": as_text(article.get("score_status")),
        "component_scores": score_map(article.get("component_scores")),
        "why_worth_reading": as_text(article.get("why_worth_reading")),
        "core_findings": as_text_list(article.get("core_findings")),
        "term_explanations": public_terms(article.get("term_explanations")),
        "research_inspiration": public_inspiration(article.get("research_inspiration")),
        "top3_reason": as_text(article.get("top3_reason")),
        "tags": as_text_list(article.get("tags")),
        "strong_recommendation": bool(article.get("strong_recommendation", False)),
        "strong_recommendation_reasons": as_text_list(article.get("strong_recommendation_reasons")),
        "needs_verification": as_text_list(article.get("needs_verification")),
    }


def atomic_json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build(input_path: Path, site_root: Path) -> tuple[Path, Path]:
    with input_path.open("r", encoding="utf-8") as handle:
        source = json.load(handle)
    if not isinstance(source, dict):
        raise ValueError("reviewed report root must be an object")

    date = as_text(source.get("date"))
    if not DATE_RE.fullmatch(date):
        raise ValueError(f"invalid report date: {date!r}")

    metadata = source.get("metadata") if isinstance(source.get("metadata"), dict) else {}
    articles = [public_article(item) for item in source.get("articles", [])]
    articles = [item for item in articles if item.get("title") or item.get("chinese_title")]
    public_metadata = {
        "window": as_text(metadata.get("window")),
        "retrieved_count": metadata.get("retrieved_count", 0),
        "screened_count": metadata.get("screened_count", 0),
        "preliminary_recommended_count": metadata.get("preliminary_recommended_count", 0),
        "final_recommended_count": len(articles),
        "threshold": metadata.get("threshold", 70),
        "source_counts": metadata.get("source_counts", {}) if isinstance(metadata.get("source_counts"), dict) else {},
        "warnings": as_text_list(metadata.get("warnings")),
    }
    report = {
        "schema_version": 1,
        "title": "辐射探测论文雷达",
        "date": date,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "term_explanation_mode": "dual",
        "metadata": public_metadata,
        "articles": articles,
        "research_ideas": as_text_list(source.get("research_ideas")),
    }

    data_root = site_root / "data"
    report_path = data_root / "reports" / f"{date}.json"
    atomic_json_write(report_path, report)

    index_path = data_root / "index.json"
    old_index = load_json(index_path, {})
    old_reports = old_index.get("reports", []) if isinstance(old_index, dict) else []
    by_date: dict[str, dict[str, Any]] = {}
    if isinstance(old_reports, list):
        for item in old_reports:
            if isinstance(item, dict) and DATE_RE.fullmatch(as_text(item.get("date"))):
                by_date[as_text(item.get("date"))] = item
    top_score = max(
        [int(item.get("recommendation_score", 0)) for item in articles if isinstance(item.get("recommendation_score"), (int, float))]
        or [0]
    )
    by_date[date] = {
        "date": date,
        "path": f"reports/{date}.json",
        "article_count": len(articles),
        "top_score": top_score,
        "window": public_metadata["window"],
    }
    reports = [by_date[key] for key in sorted(by_date, reverse=True)]
    index = {
        "schema_version": 1,
        "title": "辐射探测论文雷达",
        "description": "面向辐射探测、闪烁体、能谱、成像与信号读出的精选科研文献雷达。",
        "updated_at": report["published_at"],
        "latest_date": reports[0]["date"] if reports else date,
        "reports": reports,
    }
    atomic_json_write(index_path, index)
    return report_path, index_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="reviewed_articles.json")
    parser.add_argument("--site-root", default=Path.cwd(), type=Path, help="GitHub Pages repository root")
    args = parser.parse_args()
    report_path, index_path = build(args.input.resolve(), args.site_root.resolve())
    print(f"public report: {report_path}")
    print(f"public index:  {index_path}")


if __name__ == "__main__":
    main()
