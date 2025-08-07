from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from langchain_core.documents import Document

from models.llm import get_chat_model


def get_rag_response(query, vectorstore, model_provider="openai"):
    if not vectorstore:
        return "⚠️ No document found. Please upload a file first."

    try:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        llm = get_chat_model(provider="groq", temperature=0.3)



        # Prompt for financial analysis (you can customize more)
        prompt_template = """
You are a helpful AI assistant specialized in financial documents.
Use the following context to answer the question.
If the answer is not in the document, respond with "not found".

Context:
{context}

Question:
{question}
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False
        )

        response = qa_chain.run(query)

        # Catch low-confidence generic answers
        if response.strip().lower() in ["i don't know.", "not found", "i don't know"]:
            return "🤔 I couldn't find a clear answer in the document. Try rephrasing or asking a different question."

        return response.strip()

    except OutputParserException:
        return "⚠️ Something went wrong while parsing the response. Try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"
