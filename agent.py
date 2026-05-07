import os
import json
import re
from dotenv import load_dotenv
from autogen import AssistantAgent
from tools import search_papers

load_dotenv()

# =========================
# LLM CONFIG (Mistral)
# =========================
LLM_CONFIG = {
    "config_list": [
        {
            "model": "open-mistral-nemo",
            "api_key": os.getenv("MISTRAL_API_KEY"),
            "api_type": "mistral",
            "api_rate_limit": 0.25,
            "repeat_penalty": 1.1,
            "temperature": 0.0,
            "seed": 42,
            "stream": False,
            "native_tool_calls": False,
            "cache_seed": None,
        }
    ]
}

# =========================
# CREATE AGENT
# =========================
agent = AssistantAgent(
    name="research_agent",
    llm_config=LLM_CONFIG
)

# =========================
# STEP 1: EXTRACT CONSTRAINTS
# =========================
def extract_constraints(query: str):

    prompt = f"""
Extract structured constraints from the research request.

Return ONLY valid JSON.

Format:
{{
    "topic": "string",
    "year_operator": "before/after/in/none",
    "year": integer or null,
    "min_citations": integer or null
}}

User request:
{query}
"""

    response = agent.generate_reply(
        messages=[{"role": "user", "content": prompt}]
    )

    # AutoGen may return dict
    if isinstance(response, dict):
        content = response.get("content", "")
    else:
        content = str(response)

    content = content.strip()

    # Remove markdown
    content = re.sub(r"```json", "", content)
    content = re.sub(r"```", "", content)

    # -------------------------
    # EXTRACT ONLY FIRST JSON
    # -------------------------
    json_match = re.search(r"\{.*?\}", content, re.DOTALL)

    if json_match:

        json_text = json_match.group(0)

        try:
            parsed = json.loads(json_text)

            return {
                "topic": parsed.get("topic", query),
                "year_operator": parsed.get(
                    "year_operator",
                    "none"
                ),
                "year": parsed.get("year"),
                "min_citations": parsed.get(
                    "min_citations"
                )
            }

        except Exception as e:
            print("\nJSON parsing failed:")
            print(json_text)
            print(e)

    # -------------------------
    # FALLBACK
    # -------------------------
    return {
        "topic": query,
        "year_operator": "none",
        "year": None,
        "min_citations": None
    }

# =========================
# STEP 2: DETERMINISTIC FILTERS
# =========================
def matches_constraints(paper, constraints):

    year = paper.get("year") or 0
    citations = paper.get("citations") or 0

    year_operator = constraints.get("year_operator")
    target_year = constraints.get("year")
    min_citations = constraints.get("min_citations")

    # Year filtering
    if target_year is not None:

        if year_operator == "after":
            if year <= target_year:
                return False

        elif year_operator == "before":
            if year >= target_year:
                return False

        elif year_operator == "in":
            if year != target_year:
                return False

    # Citation filtering
    if min_citations is not None:
        if citations < min_citations:
            return False

    return True

# =========================
# STEP 3: TOPIC RELEVANCE FILTER
# =========================
def is_topic_relevant(paper, topic):
    text = (
        (paper.get("title") or "") + " " +
        (paper.get("abstract") or "")
    ).lower()

    topic = topic.lower()

    keywords = topic.replace("-", " ").split()

    score = sum(1 for k in keywords if k in text)

    # stricter rule
    return score >= max(2, len(keywords) // 2)

# =========================
# STEP 4: GENERATE EXPLANATION
# =========================
def explain_paper(paper, query: str):

    prompt = f"""
You are a strict research assistant.

ONLY use the provided paper information.
DO NOT hallucinate.
DO NOT invent facts.
DO NOT mention tools or APIs.

User request:
{query}

Paper Information:
Title: {paper.get("title")}
Authors: {", ".join(paper.get("authors", []))}
Year: {paper.get("year")}
Citations: {paper.get("citations")}
Abstract: {paper.get("abstract")}
URL: {paper.get("url")}

Write:
1. Why the paper matches the request
2. 3 bullet points summarizing the contribution
3. A short conclusion (max 2 sentences)

Keep the response concise and factual.
"""

    response = agent.generate_reply(
        messages=[{"role": "user", "content": prompt}]
    )

    if isinstance(response, dict):
        return response.get("content", "")

    return str(response)

# =========================
# MAIN AGENT PIPELINE
# =========================
def run_agent(user_query: str):

    print("\nSTEP 1: Extracting constraints...\n")

    constraints = extract_constraints(user_query)

    print("Extracted Constraints:")
    print(json.dumps(constraints, indent=2))

    # Search topic only
    topic = constraints.get("topic", user_query)

    print("\nSTEP 2: Searching OpenAlex...\n")

    papers = search_papers(topic)

    if not papers:
        return {
            "error": "No papers found from OpenAlex."
        }

    print(f"Found {len(papers)} candidate papers.\n")

    # Debug preview
    for p in papers[:5]:
        print(
            f"- {p['title']} "
            f"({p['year']}) "
            f"[citations: {p['citations']}]"
        )

    print("\nSTEP 3: Filtering papers...\n")

    filtered = [
        paper for paper in papers
        if matches_constraints(paper, constraints)
        and is_topic_relevant(
            paper,
            constraints.get("topic", "")
        )
    ]

    if not filtered:
        return {
            "error": "No papers matched constraints.",
            "constraints": constraints
        }

    print(f"{len(filtered)} papers matched constraints.\n")

    # Pick highest cited relevant paper
    best = max(
        filtered,
        key=lambda p: p.get("citations", 0)
    )

    print("STEP 4: Generating explanation...\n")

    explanation = explain_paper(best, user_query)

    # Final structured response
    result = {
        "title": best.get("title"),
        "authors": best.get("authors"),
        "year": best.get("year"),
        "citations": best.get("citations"),
        "citation_source": "OpenAlex API",
        "url": best.get("url"),
        "constraints_used": constraints,
        "explanation": explanation
    }

    return result
