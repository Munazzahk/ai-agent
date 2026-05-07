# ai-agent

## Overview

This project is an AI-powered research assistant built using AutoGen and the OpenAlex API.  
It retrieves academic papers and filters them based on user constraints such as topic, publication year, and citation count.

## Features

- AutoGen-based LLM agent
- External tool: OpenAlex API for real research papers
- Filtering (year + citation constraints)
- LLM-based explanation generation
- Evaluation with test queries

## System Architecture

1. User inputs a query
2. LLM extracts constraints (topic, year, citations)
3. OpenAlex API retrieves candidate papers
4. Python filters invalid results
5. Best paper selected by citation count
6. LLM explains why it matches

## Installation and setup

# 1. Clone the repository
bash
git clone https://github.com/munazzahk/ai-agent.git
cd ai-agent

# 2. Create a virtual enviorement and activate it (windows)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add .env file and Mistral key
Create an `.env` file in root
Add: MISTRAL_API_KEY=your_api_key_here
Save changes

# 5. Run the AI agent
python main.py 

# 6. Evaluate
python evaluate.py

## Evaluation Method

The agent was evaluated using a scripted test suite of 10 prompts:

- topic-specific queries
- citation constraints
- year-based constraints (before/after/year)
- ambiguous queries
- cases where no valid paper exists

For each test case, the system checks:

- whether a paper was found
- whether year constraints were implemented
- whether citation thresholds were implemented
- whether output is based on real API data (OpenAlex)
- whether hallucinated metadata is avoided

## Results 

The system performs well when:
- keywords in the query match OpenAlex
- constraints are clearly defined

It struggles when:
- queries are abstract (fx. "AI planning")
- same words are used in different contexts
