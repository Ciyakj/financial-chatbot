import streamlit as st
import base64
import random
import string
from models.llm import get_chat_model
from models.embeddings import create_vectorstore
from utils.rag_utils import get_rag_response_with_sources
from utils.web_search import search_web
from utils.document_loader import load_document
from utils.insight_utils import generate_summary, extract_financial_metrics
from utils.question_refiner import is_response_poor, get_refinement_suggestions
import requests
from io import BytesIO

# 🌟 Set up the Streamlit page
st.markdown("""
### 📊 Financial Document Chatbot  
*Ask about financial reports or general finance topics*
""")

# 🌙 Theme toggle logic
with st.sidebar:
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    theme = st.radio("Toggle Theme", ["light", "dark"], index=0 if st.session_state.theme == "light" else 1)
    st.session_state.theme = theme

# 🖍️ Apply dynamic theme
if st.session_state.theme == "dark":
    st.markdown("""
        <style>
        .block-container { background-color: #0e1117; color: white; }
        .sidebar .sidebar-content { background-color: #1c1f26; color: white; }
        .stChatMessage.user { background-color: #223; color: #fff; }
        .stChatMessage.assistant { background-color: #334; color: #fff; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .block-container { background-color: #f9f9f9; color: black; }
        .sidebar .sidebar-content { background-color: #f1f3f6; color: black; }
        .stChatMessage.user { background-color: #e0f7ff; color: black; }
        .stChatMessage.assistant { background-color: #fff7e6; color: black; }
        </style>
    """, unsafe_allow_html=True)

# --- Session Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "upload_key" not in st.session_state:
    st.session_state.upload_key = ''.join(random.choices(string.ascii_letters, k=10))

# --- Sidebar Settings ---
with st.sidebar:
    st.header(":wrench: Settings")

    model_option = st.selectbox("Choose LLM Provider", ["groq", "google"], help="Pick the backend model.")
    response_mode = st.radio("Response Mode", ["Concise", "Detailed"], help="Choose how detailed the response should be.")
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1, help="Higher = more creative, lower = more factual.")

    if st.button("🗑️ Reset / Upload New File"):
        for key in list(st.session_state.keys()):
            if key not in ["theme"]:
                del st.session_state[key]
        st.session_state.upload_key = ''.join(random.choices(string.ascii_letters, k=10))
        st.cache_data.clear()
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

# --- Combined Upload Section ---
st.markdown("---")
st.subheader("📂 Upload Financial Document")
st.caption("Upload a file or paste a document URL below to begin.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload from File",
        type=["pdf", "docx", "xlsx", "txt"],
        key=st.session_state.upload_key,
        help="Upload PDFs, Word, Excel, or text financial reports."
    )

with col2:
    doc_url = st.text_input("Or paste a direct document URL")
    if st.button("📥 Fetch Document") and doc_url:
        try:
            with st.spinner("Fetching document from URL..."):
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(doc_url, headers=headers)

                if response.status_code != 200:
                    st.error("❌ Failed to fetch the document. Check the URL.")
                    st.stop()

                content_type = response.headers.get("content-type", "").lower()
                suffix = ".pdf"
                if "docx" in content_type:
                    suffix = ".docx"
                elif "xlsx" in content_type or "excel" in content_type:
                    suffix = ".xlsx"
                elif "text" in content_type or "plain" in content_type:
                    suffix = ".txt"

                uploaded_file = BytesIO(response.content)
                uploaded_file.name = f"fetched{suffix}"
                st.session_state.uploaded_file = uploaded_file
                st.success("✅ Document fetched and ready for processing!")

        except Exception as e:
            st.error(f"❌ Error fetching file: {e}")
            st.stop()

# --- Document Handling ---
if uploaded_file or "uploaded_file" in st.session_state:
    if not uploaded_file:
        uploaded_file = st.session_state["uploaded_file"]

    st.success("✅ Document uploaded successfully!")
    with st.spinner("🔀 Processing document..."):
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

    with st.expander("📈 Show Financial Chart", expanded=False):
        from utils.insight_utils import generate_financial_chart
        chart_buf = generate_financial_chart(st.session_state["insights"])
        if chart_buf:
            st.image(chart_buf, caption="📊 Financial Metrics", use_container_width=True)
        else:
            st.info("Chart not available for this document.")

# --- Welcome Message ---
if not st.session_state.messages:
    st.chat_message("assistant").markdown(
        "👋 Hello! I'm your AI-powered financial assistant.\n\n"
        "You can:\n"
        "- Ask general questions about finance (e.g., investing, saving, equity, etc.)\n"
        "- Or upload a financial document (PDF, DOCX, XLSX) to analyze and explore insights like:\n"
        "  • Revenue breakdowns\n"
        "  • Net profit margins\n"
        "  • Key financial risks\n\n"
        "Let's get started! 📁"
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

            try:
                if st.session_state.vectorstore:
                    answer, sources = get_rag_response_with_sources(
                        f"{system_prefix}\n{prompt}", st.session_state.vectorstore, model
                    )
                    response = answer
                else:
                    system_message = "You are a helpful financial assistant. Provide clear and accurate answers to financial questions."
                    response = model.invoke(f"{system_message}\n{prompt}").content
                    sources = []

            except Exception as e:
                response = f"❗ Sorry, I couldn't process your question.\n\n**Error:** {str(e)}"
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
