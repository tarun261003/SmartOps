# smartops_agent/agent.py
from typing import Literal, Dict, Any

from google.adk.agents.llm_agent import Agent

from .email_tools import (
    summarize_inbox, draft_reply, search_email_by_body_keyword
)

from .analytics_tools import analyze_sales_csv
from .policy_rag_tools import answer_policy_question


def route_request(
    task_type: Literal["email", "analytics", "policy"],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Router tool that delegates to capability-specific functions.

    task_type:
      - "email"
      - "analytics"
      - "policy"

    payload:
      - for email: {
          "action": "summary" | "draft",
          "thread_id": "optional",
          "user_note": "optional"
        }
      - for analytics: {
          "file_path": "smartops_agent\data\sample_sales.csv"
        }
      - for policy: {
          "question": "What is the leave policy for sick leave?"
        }
    """
    if task_type == "email":
        action = payload.get("action", "summary")
        if action == "summary":
            summary = summarize_inbox()
            return {
                "channel": "email",
                "action": "summary",
                "result": summary,
            }
        elif action == "draft":
            thread_id = payload.get("thread_id")
            user_note = payload.get("user_note", "")
            draft = draft_reply(thread_id=thread_id, user_note=user_note)
            return {
                "channel": "email",
                "action": "draft",
                "result": draft,
            }
        else:
            return {"error": f"Unknown email action: {action}"}

    if task_type == "analytics":
        file_path = payload.get("file_path", "smartops_agent\data\sample_sales.csv")
        report = analyze_sales_csv(file_path)
        return {
            "channel": "analytics",
            "action": "analysis",
            "result": report,
        }

    if task_type == "policy":
        question = payload.get("question", "")
        answer = answer_policy_question(question)
        return {
            "channel": "policy",
            "action": "qa",
            "result": answer,
        }

    return {"error": f"Unknown task_type: {task_type}"}

    if task_type == "email_search":
        keyword = payload.get("keyword", "")
        return {
            "channel": "email_search",
            "result": search_email_by_body_keyword(keyword)
        }

root_agent = Agent(
    model="gemini-2.5-flash",
    name="smartops_supervisor",
    description=(
        "SmartOps AI: an enterprise workflow assistant that can summarize emails, "
        "analyze business data, and answer policy questions using tools."
    ),
    instruction=(
        "You are SmartOps AI, an enterprise workflow assistant.\n"
        "Your capabilities:\n"
        "  - Email: summarize the inbox or draft replies based on structured data.\n"
        "  - Analytics: analyze CSV business data files and extract insights.\n"
        "  - Policy: answer policy questions by searching local policy documents.\n\n"
        "Steps:\n"
        "1) Understand the user's intent.\n"
        "2) Decide whether the request is about EMAIL, ANALYTICS, or POLICY.\n"
        "3) Call the 'route_request' tool with the appropriate task_type and payload.\n"
        "   - For email summary, use task_type='email' and action='summary'.\n"
        "   - For email draft, use task_type='email', action='draft', and pass a short user_note.\n"
        "   - For analytics, use task_type='analytics' and pass the file_path if given.\n"
        "   - For policy Q&A, use task_type='policy' and pass the question.\n"
        "4) Take the tool output and convert it into a clear, business-friendly response.\n"
        "5) If the user is vague, ask a short clarification question before calling a tool.\n\n"
        "Special rule for email search based on body keywords:\n"
        "If the user asks about an email 'about' some topic (for example: the email about the meeting, "
        "the message regarding the deadline, or 'help me reply to the email about X'):\n"
        "  - Infer the key topic word or short phrase X from the user's request.\n"
        "  - Call the 'route_request' tool with task_type='email_search' and payload {'keyword': X}.\n"
        "  - If the tool returns one or more matches, choose the best matching email and either summarize it "
        "    or draft a reply, depending on what the user requested.\n"
        "  - If the tool returns no matches, ask the user for an additional keyword, sender, or approximate date "
        "    before trying again.\n"
    ),
    tools=[route_request],
)