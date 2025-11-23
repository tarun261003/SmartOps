import json
import os
from pathlib import Path
from email import message_from_string
from email.utils import parsedate_to_datetime

# 👇 YOUR USER MAIL FOLDER (use raw string for Windows path)
BASE = Path(r"C:\Users\Asus\Desktop\SmartopsAI\mails\allen-p")

# 👇 Output JSON inside your agent project
OUTPUT = Path(r"C:\Users\Asus\Desktop\SmartopsAI\smartops_agent\data\sample_emails.json")

emails = []


def extract_email(path: Path):
    raw = path.read_text(errors="ignore")
    msg = message_from_string(raw)

    subject = msg.get("Subject", "")
    sender = msg.get("From", "")
    date = msg.get("Date", "")
    body = ""

    # Get plain text body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode(
                        "utf-8", errors="ignore"
                    )
                except Exception:
                    pass
    else:
        body = msg.get_payload()

    # Parse date safely
    try:
        dt = parsedate_to_datetime(date)
        received_at = dt.isoformat()
    except Exception:
        received_at = ""

    return {
        "id": str(len(emails) + 1),
        "thread_id": "t" + str((len(emails) // 10) + 1),  # fake threads of 10
        "from": sender,
        "subject": subject,
        "body": str(body)[:2000],  # trim to keep size reasonable
        "received_at": received_at,
    }


# Walk ALL subfolders and ALL files under allen-p
for root, dirs, files in os.walk(BASE):
    for fname in files:
        full_path = Path(root) / fname
        try:
            email_data = extract_email(full_path)
            emails.append(email_data)
        except Exception as e:
            # You can print errors if you want to debug:
            # print("Error on", full_path, "=>", e)
            pass

# Limit to first N emails so file isn't huge
MAX_EMAILS = 300
emails = emails[:MAX_EMAILS]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(emails, indent=2), encoding="utf-8")

print("Saved:", OUTPUT)
print("Total emails:", len(emails))