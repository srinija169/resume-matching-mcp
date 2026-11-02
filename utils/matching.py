"""Transparent baseline resume/job-description scoring.

This is a deterministic keyword-overlap baseline, not a hiring decision.
Review candidate information and validate the scoring approach before production use.
"""
import re
from collections import Counter

STOPWORDS = {
    "and", "the", "for", "with", "from", "that", "this", "you", "your",
    "are", "was", "were", "will", "our", "their", "have", "has", "not",
    "but", "all", "any", "into", "using", "use", "work", "years", "year",
    "job", "role", "candidate", "experience", "skills", "skill",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text.lower())
    return [word for word in words if word not in STOPWORDS and len(word) > 1]


def score_resume(job_description: str, resume_text: str) -> dict:
    job_terms = set(tokenize(job_description))
    resume_terms = set(tokenize(resume_text))
    if not job_terms:
        score = 0.0
        matched = []
    else:
        matched = sorted(job_terms & resume_terms)
        score = round(100 * len(matched) / len(job_terms), 2)

    return {
        "score": score,
        "matched_keywords": matched,
        "matched_keyword_count": len(matched),
        "job_keyword_count": len(job_terms),
    }


def rank_candidates(job_description: str, resumes: list[dict]) -> list[dict]:
    ranked = []
    for resume in resumes:
        if resume.get("status") != "success":
            ranked.append({
                "filename": resume.get("filename", "unknown"),
                "status": "error",
                "error": resume.get("error", "Could not process resume"),
            })
            continue
        result = score_resume(job_description, resume.get("text", ""))
        ranked.append({
            "filename": resume["filename"],
            "status": "success",
            **result,
        })

    return sorted(
        ranked,
        key=lambda item: (item.get("status") == "success", item.get("score", -1)),
        reverse=True,
    )
