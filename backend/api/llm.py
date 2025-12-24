from groq import Groq
import os

def generate_answer(prompt: str) -> str:
    try:
        print("DEBUG — Entered generate_answer()")
        print("DEBUG — Prompt:", prompt[:80], "...")

        api_key = os.getenv("GROQ_API_KEY")
        print("DEBUG — Loaded API Key:", api_key)

        if not api_key:
            return "AI Error: GROQ_API_KEY is missing."

        client = Groq(api_key=api_key)
        print("DEBUG — Groq client created")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        print("DEBUG — Raw Response:", response)

        answer = response.choices[0].message.content
        print("DEBUG — Extracted Answer:", answer)

        return answer

    except Exception as e:
        print("DEBUG — ERROR IN generate_answer():", str(e))
        return f"AI Error: {str(e)}"
