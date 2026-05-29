import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

FAQ = {
    "hours": "We are open Mon-Fri 9am-5pm.",
    "refund": "Refunds are accepted within 30 days.",
    "shipping": "Free shipping on orders over $50.",
}


def answer(question):
    q = question.lower()
    for key in FAQ:
        if key in q:
            return FAQ[key]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful FAQ assistant. Answer concisely.",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        if q.lower() in ("quit", "exit"):
            break
        print(answer(q))
