# import os
# import google.generativeai as genai
# genai.configure(api_key="AIzaSyDUA2CJuMdQLIvjfNwbaPJVHIUq-is3zSU")
# model=genai.GenerativeModel("gen-lang-client-0227990973")
# def send(content,filename):
#     prompt=f"""You are a code correction agent. Your goals:

# 1. Fix syntax errors.
# 2. Fix logical errors based on intent inferred from the code.
# 3. Preserve coding style and variable names unless incorrect.
# 4. Do not add commentary, explanation, or markdown formatting.
# 5. Return corrected code only.

# Here is the file to correct: \n \n {content}"""
#     print("after prompt")
#     response = model.generate_content(prompt)
#     print(response.text.strip())

#     return response.text.strip()

# def process_files(path):
#     print("process_files")
#     # for root, dirs, files in os.walk(path):
#     #     for f in files:
#     #         path = os.path.join(root, f)
#     with open(path, "r", encoding="utf-8") as fh:
#                 content = fh.read()
#     print("sending content")    
#     new_content = send(content, "file.py")
#     with open(path, "w", encoding="utf-8") as fh:
#                 fh.write(new_content)
#     print(f"Processed {path}")
# import google.generativeai as genai

# # The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client()

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)
import os
from dotenv import load_dotenv
# import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env so we get GEMINI_API_KEY
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Missing GOOGLE_API_KEY in .env")

# Configure Gemini client
genai.configure(api_key=api_key)

# Instantiate model
# model = genai.GenerativeModel("gemini-2.5-flash")

# Send a test prompt
# response = model.generate_content("heloo gemini introduce ai briefly")



llm=ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
response =llm.invoke("Hey can u explain how to use ur Api")
print("=== MODEL RESPONSE ===")
print(response.content)