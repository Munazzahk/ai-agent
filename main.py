from agent import run_agent

query = input("Enter research request: ")

result = run_agent(query)

print("\nRESULT:\n")
print(result)