import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


class QAChain:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(
            "Answer the question using only the provided context.\n\n"
            "Context:\n{context}\n\nQuestion: {question}"
        )

    def invoke(self, question):
        docs = self.retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        response = self.llm.invoke(
            self.prompt.format(context=context, question=question)
        )
        return {
            "result": response.content
            if hasattr(response, "content")
            else str(response),
            "source_documents": docs,
        }


def build_qa_chain(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(chunks, embedding=embeddings)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    return QAChain(vectorstore.as_retriever(), llm)


if __name__ == "__main__":
    from langchain_core.documents import Document

    docs = [Document(page_content="AI is transforming every industry.")]
    qa = build_qa_chain(docs)
    print(qa.invoke("What is AI transforming?"))
