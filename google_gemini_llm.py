import google.generativeai as genai
import os


def talk_to_gemini(message_to_llm, model="gemini-1.5-flash"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel(model)
    response = model.generate_content(message_to_llm)
    return response.text
