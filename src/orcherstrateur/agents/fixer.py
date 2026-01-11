import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class FixerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

    def fix(self):
        prompt = (
            "You are the Fixer agent. I will provide a fix plan and a piece of code. "
            "Apply the plan and return ONLY the corrected code.\n\n"
            "Fix plan:\n"
            "- Correct function syntax\n"
            "- Add indentation\n"
            "- Fix variable names\n"
            "- Remove semicolons\n"
            "- Add docstring\n"
            "- Add type hints\n\n"
            "Code:\n"
            "def(A,b)return a+B"
        )

        resp = self.llm.invoke(prompt)

        print("\n===== FIXER OUTPUT =====\n")
        print(resp.content)

agent = FixerAgent()
agent.fix()
