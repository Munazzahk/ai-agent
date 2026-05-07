from agent import run_agent

tests = [
    "LLM agents after 2022 with 100 citations",
    "RAG before 2021 with 500 citations",
    "AI planning papers",
    "Transformer models before 2020 with 1000 citations",
    "Tool-using AI agents recent papers",
    "NLP high citation papers",
    "Autonomous software agents after 2023",
    "Deep learning optimization before 2021",
    "Multi-agent systems recent",
    "Neural networks before 2010 with 5000 citations"
]

results = []

for t in tests:
    print("\n---")
    print("TEST:", t)

    result = run_agent(t)

    # simple evaluation signals
    eval_entry = {
        "query": t,
        "found": "error" not in result,
        "title": result.get("title"),
        "year": result.get("year"),
        "citations": result.get("citations")
    }

    results.append(eval_entry)

    print(eval_entry)