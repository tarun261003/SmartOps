# smartops_agent/email_tools.py
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_PATH = Path(__file__).parent / "data" / "sample_emails.json"


def _load_emails() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def summarize_inbox() -> Dict[str, Any]:
    """
    Returns a structured overview of the inbox that the LLM can verbalize.

    Output shape:
    {
      "total_emails": int,
      "by_sender": { "alice@x.com": 3, ... },
      "latest_subjects": [
         {"from": "...", "subject": "...", "received_at": "..."},
         ...
      ]
    }
    """
    emails = _load_emails()
    by_sender = {}
    latest = []

    for e in sorted(emails, key=lambda x: x.get("received_at", ""), reverse=True):
        sender = e.get("from", "unknown")
        by_sender[sender] = by_sender.get(sender, 0) + 1
        if len(latest) < 10:
            latest.append(
                {
                    "from": sender,
                    "subject": e.get("subject", ""),
                    "received_at": e.get("received_at", ""),
                    "thread_id": e.get("thread_id", ""),
                }
            )

    return {
        "total_emails": len(emails),
        "by_sender": by_sender,
        "latest_subjects": latest,
    }


def draft_reply(
    thread_id: Optional[str],
    user_note: str = "",
) -> Dict[str, Any]:
    """
    Returns context for a reply the LLM can turn into natural language.

    Output:
    {
      "thread_id": "...",
      "last_message": "text of last email in thread",
      "user_note": "...",
    }
    """
    emails = _load_emails()
    thread_emails = [e for e in emails if e.get("thread_id") == thread_id] if thread_id else emails
    if not thread_emails:
        return {
            "thread_id": thread_id,
            "error": "No emails found for this thread_id",
            "user_note": user_note,
        }

    # sort by time and pick latest
    last_email = sorted(
        thread_emails, key=lambda x: x.get("received_at", "")
    )[-1]

    return {
        "thread_id": thread_id,
        "last_from": last_email.get("from"),
        "last_subject": last_email.get("subject"),
        "last_snippet": last_email.get("body", "")[:500],
        "user_note": user_note,
    }
def search_email_by_body_keyword(keyword: str) -> List[Dict[str, Any]]:
    """
    Search emails whose body contains the keyword.
    Returns a list of matching emails (up to 5).
    """
    emails = _load_emails()
    keyword_lower = keyword.lower()

    matches = []
    for e in emails:
        body = e.get("body", "").lower()
        subject = e.get("subject", "").lower()

        if keyword_lower in body or keyword_lower in subject:
            matches.append({
                "id": e.get("id"),
                "thread_id": e.get("thread_id"),
                "from": e.get("from"),
                "subject": e.get("subject"),
                "snippet": e.get("body", "")[:400],
                "received_at": e.get("received_at")
            })

        if len(matches) >= 5:
            break

    return matches
