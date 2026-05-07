from agent import run_agent

tests = [
    "LLM agents after 2022 with 100 citations",
    "RAG before 2021 with 500 citations",
    "AI planning papers",
    "Transformer models before 2020",
    "Tool-using AI agents recent papers",
    "NLP high citation papers",
    "Autonomous software agents",
    "Deep learning optimization",
    "Multi-agent systems recent",
    "No citation constraint test"
]

for t in tests:
    print("\n---")
    print("TEST:", t)
    print(run_agent(t))