# 📊 Financial Document Chatbot

An AI-powered Streamlit chatbot that helps users analyze financial documents (PDF, DOCX, XLSX, TXT) and answer general finance-related questions.

---

## 🚀 Deployment

**Live App:** [Click here to try it out]([https://your-username-your-repo-name.streamlit.app](https://financial-chatbot-fscidhbxdgbfgkwycrfcsj.streamlit.app/))  

---

## 🎯 Use Case Objective

Help users explore and understand financial documents through natural language queries using LLMs and document-based Q&A (RAG).

---

## 🛠️ Features Implemented

- 🧠 **LLM Integration**: Supports Groq (LLaMA 3) and Google (Gemini)
- 📁 **Multi-format File Upload**: PDF, DOCX, XLSX, TXT
- 🌐 **Document URL Fetching**
- 🧾 **Financial Summary Extraction**
- 📊 **Chart Generation from Key Metrics**
- 🗨️ **RAG + General Chat Handling**
- 🎨 **Dark/Light Theme Toggle**
- 📥 **Download Chat & Insights**
- 🖼️ (Optional) Image & Audio Upload (Phase 3 enhancement)
  
---

## 🔍 How It Works

1. Upload a financial document (or paste a URL)
2. The chatbot extracts insights and builds a vectorstore
3. You can ask:
   - Document-specific questions like "What is the net profit?"
   - General financial queries like "What is equity?"
4. Get answers with optional source references and charts

---

## 🧩 Tech Stack

- **Streamlit**
- **LangChain**
- **Groq (LLaMA3)** / **Gemini (Google AI Studio)**
- **FAISS Vectorstore**
- **Matplotlib** (for charting)
- **pytesseract / Whisper** *(for optional multimodal features)*

---

## 🚧 Challenges Faced

- Handling vague or unsupported queries elegantly
- Balancing RAG vs general finance chat with fallback logic
- Streamlit UI alignment (upload via file & URL)
- Chart accuracy for unstructured financial texts

---

## 📂 Run Locally

```bash
git clone https://github.com/Ciyakj/financial-chatbot.git
cd financial-chatbot
pip install -r requirements.txt
streamlit run app.py
