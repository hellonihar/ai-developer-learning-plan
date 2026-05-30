from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableLambda
from few_shot_examples import FEW_SHOT_EXAMPLES

SYSTEM_PROMPT = """You are a senior policy compliance analyst. Your job is to analyze policy
clauses and explain them in plain language, assess risk, and synthesize implications.

Use the retrieved policy document chunks below to answer the user's question.

{examples}

Follow this chain-of-thought for EACH clause you analyze:

1. **Explanation** — Restate the clause in plain language. Define any legal or technical terms.
2. **Risk Assessment** — Rate the risk as LOW / MEDIUM / HIGH and explain why.
3. **Implication** — What does this mean for the policyholder in practical terms?

After analyzing individual clauses, synthesize:
- **Overall Assessment** — A summary of the policy's key risks and protections.
- **Recommended Actions** — 2-3 concrete steps the policyholder should take.
"""

HUMAN_PROMPT = """Retrieved policy excerpts:
{context}

User question: {question}

Analyze the relevant clauses and provide a chain-of-thought response."""


def format_examples() -> str:
    parts = []
    for i, ex in enumerate(FEW_SHOT_EXAMPLES, 1):
        parts.append(
            f"Example {i}:\n"
            f"Clause: {ex['clause']}\n"
            f"Explanation: {ex['explanation']}\n"
            f"Risk Assessment: {ex['risk_assessment']}\n"
            f"Implication: {ex['implication']}\n"
        )
    return "\n---\n".join(parts)


def format_docs(docs: list[str]) -> str:
    return "\n\n---\n\n".join(docs)


def build_chain(model: str = "local-model"):
    llm = ChatOpenAI(
        model=model,
        temperature=0.2,
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    chain = (
        RunnablePassthrough.assign(
            examples=RunnableLambda(lambda _: format_examples()),
            context=RunnableLambda(lambda x: format_docs(x["context"])),
        )
        | prompt
        | llm
    )
    return chain
