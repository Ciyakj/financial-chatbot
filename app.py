import streamlit as st
import base64
from models.llm import get_chat_model
from models.embeddings import create_vectorstore
from utils.rag_utils import get_rag_response_with_sources
from utils.web_search import search_web
from utils.document_loader import load_document
from utils.insight_utils import generate_summary, extract_financial_metrics
from utils.question_refiner import is_response_poor, get_refinement_suggestions

# 🌟 Set up the Streamlit page
st.set_page_config(page_title="📊 Financial Document Chatbot", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #f9f9f9;
    }
    .sidebar .sidebar-content {
        background-color: #f1f3f6;
        padding: 1rem;
        border-radius: 8px;
    }
    .stButton > button {
        background-color: #0057d8;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin-top: 0.5rem;
    }
    .stTextInput, .stSelectbox, .stRadio, .stFileUploader {
        border-radius: 8px;
    }
    .stChatMessage.user {
        background-color: #e0f7ff;
        color: #000;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stChatMessage.assistant {
        background-color: #fff7e6;
        color: #000;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title(":bar_chart: Financial Document Chatbot")
st.caption("Ask questions about your uploaded financial documents.")

# --- Session Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# --- Sidebar Settings ---
with st.sidebar:
    st.header(":wrench: Settings")

    model_option = st.selectbox("Choose LLM Provider", ["groq", "openai", "google"])
    response_mode = st.radio("Response Mode", ["Concise", "Detailed"])
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1)

    uploaded_file = st.file_uploader(
        "\U0001f4c1 Upload Financial Report",
        type=["pdf", "docx", "xlsx", "txt"],
        key="uploader"
    )

    if st.button("🗑️ Reset / Upload New File"):
        st.session_state.clear()
        st.rerun()

    def download_button(label, content, filename):
        b64 = base64.b64encode(content.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
        st.markdown(href, unsafe_allow_html=True)

    if st.session_state.messages:
        chat_text = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
        download_button("📅 Download Chat", chat_text, "chat_history.txt")

    if "insights" in st.session_state:
        insights_text = st.session_state["insights"]
        if isinstance(insights_text, list):
            insights_text = "\n".join(insights_text)
        download_button("📅 Download Insights", insights_text, "financial_insights.txt")

# --- Document Handling ---
if uploaded_file:
    st.success("✅ Document uploaded successfully!")
    with st.spinner("🔄 Processing document..."):
        raw_text = load_document(uploaded_file)

        if raw_text.startswith("❌"):
            st.error(raw_text)
            st.stop()

        vectorstore = create_vectorstore(uploaded_file)

        if isinstance(vectorstore, str) and vectorstore.startswith("❌"):
            st.error(vectorstore)
            st.stop()

        st.session_state.vectorstore = vectorstore
        st.session_state["doc_summary"] = str(generate_summary(raw_text, model_provider=model_option))
        st.session_state["insights"] = str(extract_financial_metrics(raw_text, model_provider=model_option))

# --- Display Key Financial Insights ---
if "insights" in st.session_state:
    st.subheader(":bar_chart: Key Financial Insights")
    insights_lines = st.session_state["insights"].split("\n")
    for line in insights_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            st.markdown(f"**{key.strip()}**: {value.strip()}")

# --- Welcome Message ---
if not st.session_state.messages:
    st.chat_message("assistant").markdown(
        "👋 Welcome! I’m your financial document assistant.\n\n"
        "Upload a financial PDF (like an income statement or annual report), and ask questions like:\n"
        "- What was the revenue in 2023?\n"
        "- What are the key expenses?\n"
        "- What is the net profit margin?\n\n"
        "I'm ready when you are! 📁"
    )

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Document Summary ---
if "doc_summary" in st.session_state:
    with st.expander("📄 Document Summary", expanded=True):
        st.markdown(st.session_state["doc_summary"])

# --- Chat Input ---
prompt = st.chat_input("Type your question here...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            model = get_chat_model(provider=model_option, temperature=temperature)
            system_prefix = "Answer concisely." if response_mode == "Concise" else "Provide a detailed and in-depth answer."

            if st.session_state.vectorstore:
                try:
                    answer, sources = get_rag_response_with_sources(
                        f"{system_prefix}\n{prompt}", st.session_state.vectorstore, model
                    )
                    response = answer
                except Exception as e:
                    response = f"❗ Sorry, I couldn't process your document query.\n\n**Error:** {str(e)}"
                    sources = []
            else:
                allowed_phrases = [
                    "what can you do", "who are you", "how to use", "help", "purpose",
                    "features", "upload", "start", "document", "instructions", "how"
                ]
                if any(phrase in prompt.lower() for phrase in allowed_phrases):
                    response = (
                        "👋 I’m a chatbot that helps analyze uploaded financial documents.\n\n"
                        "Please upload a PDF report such as an annual statement, income report, or balance sheet.\n"
                        "Then I can answer questions like:\n"
                        "- What is the revenue?\n"
                        "- What are the net profits?\n"
                        "- Are there any financial risks?\n\n"
                        "📁 Go ahead and upload a file to begin!"
                    )
                    sources = []
                else:
                    response = (
                        "⚠️ I can only respond to questions about uploaded financial documents.\n\n"
                        "Please upload a file to begin exploring financial data."
                    )
                    sources = []

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            if sources:
                with st.expander("🔍 Sources Used", expanded=False):
                    for i, chunk in enumerate(sources):
                        st.markdown(f"**Chunk {i+1}:**\n> {chunk}")

            if is_response_poor(response):
                st.warning("⚠️ The response was unclear or incomplete.")
                with st.expander("💡 Need help asking better questions?"):
                    for tip in get_refinement_suggestions():
                        st.markdown(f"- {tip}")
