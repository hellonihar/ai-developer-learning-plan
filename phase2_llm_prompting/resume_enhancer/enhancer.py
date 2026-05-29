import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a professional resume writer. Given a job description and a bullet point,
rewrite the bullet to be more impactful using action verbs and quantified results.
Keep it to one line.
"""

def enhance(bullet, job_description):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Job: {job_description}\nBullet: {bullet}"},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    jd = input("Paste job description: ")
    while True:
        b = input("Bullet point (or 'quit'): ")
        if b.lower() == "quit":
            break
        print(enhance(b, jd))
