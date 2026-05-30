import streamlit as st
import tempfile
from pathlib import Path

from pipeline.pdf_parser import extract_text
from pipeline.chunker import chunk_text
from pipeline.embeddings import EmbeddingStore
from pipeline.rag_chain import build_chain

st.set_page_config(page_title="Policy Analyzer", layout="wide")
st.title("Policy Analyzer")
st.markdown("Upload a policy document (PDF), then ask questions about its clauses.")

if "store" not in st.session_state:
    st.session_state.store = EmbeddingStore(persist_dir="./chroma_db")
if "chain" not in st.session_state:
    st.session_state.chain = None
if "processed" not in st.session_state:
    st.session_state.processed = False
if "model" not in st.session_state:
    st.session_state.model = "local-model"

with st.sidebar:
    st.header("1. Upload Policy")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file and not st.session_state.processed:
        with st.spinner("Processing PDF..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            raw_text = extract_text(tmp_path)
            chunks = chunk_text(raw_text)
            st.session_state.store.reset()
            st.session_state.store.add_chunks(chunks)
            st.session_state.chain = build_chain(model=st.session_state.model)
            st.session_state.processed = True
            Path(tmp_path).unlink(missing_ok=True)
        st.success(f"Indexed {len(chunks)} chunks from '{uploaded_file.name}'")

    if st.session_state.processed:
        st.info(f"{st.session_state.store.count()} chunks in vector store")
        if st.button("Clear & Upload New"):
            st.session_state.store.reset()
            st.session_state.processed = False
            st.session_state.chain = None
            st.rerun()

    st.header("2. LM Studio Setup")
    st.markdown(
        "Run a model in LM Studio (localhost:1234/v1). "
        "Enter the model name exactly as shown in LM Studio."
    )
    model_input = st.text_input("Model name", value=st.session_state.model)
    if model_input != st.session_state.model:
        st.session_state.model = model_input
        if st.session_state.processed:
            st.session_state.chain = build_chain(model=model_input)

    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown(
        "1. PDF → text → chunks → embeddings → vector store\n"
        "2. Your question retrieves relevant chunks\n"
        "3. LLM uses few‑shot CoT to explain clauses,\n"
        "   assess risk, and synthesize implications"
    )

st.header("3. Ask About the Policy")

if not st.session_state.processed:
    st.info("Upload a PDF in the sidebar to get started.")
else:
    query = st.text_input(
        "What would you like to know?",
        placeholder='e.g. "Explain the exclusion clauses and their risks"',
    )

    if query:
        with st.spinner("Analyzing..."):
            context_docs = st.session_state.store.search(query, k=5)
            if not context_docs:
                st.warning("No relevant clauses found in the document.")
            else:
                chain = st.session_state.chain
                with st.expander("View retrieved clauses", expanded=False):
                    for i, doc in enumerate(context_docs, 1):
                        st.markdown(f"**Chunk {i}:**")
                        st.text(doc[:500] + ("..." if len(doc) > 500 else ""))

                result = chain.invoke(
                    {
                        "context": context_docs,
                        "question": query,
                    }
                )
                st.markdown("### Analysis")
                st.markdown(result.content)
    else:
        st.info("Enter a question above to analyze the policy.")
