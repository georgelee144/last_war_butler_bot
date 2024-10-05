import google.generativeai as genai
import os


def talk_to_gemini(message_to_llm, model_name="gemini-1.5-flash", temperature=0):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    generation_config = {"temperature": temperature}
    model = genai.GenerativeModel(
        model_name=model_name, generation_config=generation_config
    )
    try:
        response = model.generate_content(message_to_llm)
    except Exception as error:
        print(error)
        return (None,error)
    return response.text
