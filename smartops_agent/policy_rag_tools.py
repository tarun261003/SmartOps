# smartops_agent/policy_rag_tools.py
from pathlib import Path
from typing import Dict, Any, List


POLICY_DIR = Path(__file__).parent / "data" / "policies"


def _load_policy_files() -> List[Path]:
    if not POLICY_DIR.exists():
        return []
    return list(POLICY_DIR.glob("*.md"))


def answer_policy_question(question: str) -> Dict[str, Any]:
    """
    Naive file-based RAG:
      - scans .md policy files
      - picks lines that contain any keyword from the question
    Returns raw snippets + file names; LLM converts to a nice answer.
    """
    if not question.strip():
        return {"error": "Empty question"}

    keywords = [w.lower() for w in question.split() if len(w) > 3]
    matches: List[Dict[str, str]] = []

    for f in _load_policy_files():
        text = f.read_text(encoding="utf-8")
        for line in text.splitlines():
            lower = line.lower()
            if any(k in lower for k in keywords):
                matches.append(
                    {
                        "file": f.name,
                        "line": line.strip(),
                    }
                )

    return {
        "question": question,
        "matches": matches[:20],
        "file_count_scanned": len(_load_policy_files()),
    }