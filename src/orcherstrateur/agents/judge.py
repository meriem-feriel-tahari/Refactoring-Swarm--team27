import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json
load_dotenv()

class JudgeAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

    def judge(self):
        prompt = """You are an expert Python test generator.

Your task:
1. Analyze the function NAME and understand its INTENDED purpose
2. Generate pytest unit tests that validate FUNCTIONAL CORRECTNESS
3. Create assertions that check if the logic is CORRECT, not just if it runs

Rules:
- Infer intent from function name (e.g., "average" → calculate mean)
- Generate 3-5 test cases per function
- Include edge cases (empty list, single element, negative numbers)
- Use descriptive test names
- DO NOT just check "it doesn't crash" - validate LOGIC!

Return:
{
    "test_file_name": "test_filename.py",
    "test_code": "complete pytest code here",
    "functions_tested": ["function1"]
}
without writing json{} give the output directly as dict
Here is the function to test:
def add_numbers(num1: int, num2: int) -> int:
    \"\"\"
    Adds two integer numbers together.

    Args:
        num1: The first integer.
        num2: The second integer.

    Returns:
        The sum of the two integers.
    \"\"\"
    return num1 + num2
"""
        response = self.llm.invoke(prompt)
      
        return response
       

agent = JudgeAgent()
response=agent.judge()
print(f"{response.content} \n hello baby")


# response = LLM result
try:
    print("inside try \n")
    content = json.loads(response.content)
    print(content)
except json.JSONDecodeError as e:
    print("Failed to parse JSON:", e)
    print("Raw response:", response.content)
    content = None

if content:
    out_path = os.path.join("testing", content["test_file_name"])
    # create parent directories if needed
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content["test_code"])

    print(f"Wrote test code to {out_path}")


