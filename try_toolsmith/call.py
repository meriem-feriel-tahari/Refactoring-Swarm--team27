import os
import google.generativeai as genai
genai.configure(api_key="AIzaSyDUZURAf9CKSShPOrzyJBZ0r8epMatZWmU")
model=genai.GenerativeModel("gemini-1.5-flash")
def send(content,filename):
    prompt=f"""You are a code correction agent. Your goals:

1. Fix syntax errors.
2. Fix logical errors based on intent inferred from the code.
3. Preserve coding style and variable names unless incorrect.
4. Do not add commentary, explanation, or markdown formatting.
5. Return corrected code only.

Here is the file to correct: \n \n {content}"""
    print("after prompt")
    response = model.generate_content(prompt)
    print(response.text.strip())

    return response.text.strip()

def process_files(path):
    print("process_files")
    # for root, dirs, files in os.walk(path):
    #     for f in files:
    #         path = os.path.join(root, f)
    with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
    print("sending content")    
    new_content = send(content, "file.py")
    with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_content)
    print(f"Processed {path}")