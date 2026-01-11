from langchain_google_genai import ChatGoogleGenerativeAI


class JudgeAgent:
    def __init__(self):
        # self.llm=ChatGoogleGenerativeAI(
        #     model="Gemini_2.5_flash",
        #     api_key=os.getenv("GOOGLE_API_KEY"),
        # )
        pass
    def judge(self):
        prompt=""
        judge_decision=self.llm.invoke()