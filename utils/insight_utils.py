from models.llm import get_chat_model

def generate_summary(text, model_provider="openai"):
    llm = get_chat_model(provider="groq", temperature=0.3)



    system_prompt = (
        "You are a financial analyst. Your task is to summarize company documents "
        "such as annual reports, profit/loss statements, balance sheets, or cash flow summaries. "
        "Provide a clear, concise summary in plain English using bullet points or paragraphs."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Summarize the following financial report:\n\n{text[:3000]}"}  # Limit to 3000 chars
    ]

    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        return f"⚠️ Failed to generate summary: {e}"

def extract_financial_metrics(text, model_provider="openai"):
    llm = get_chat_model(provider=model_provider, temperature=0.3)
    prompt = (
        "You are a financial analyst. Extract the following from the document:\n"
        "- Revenue\n- Net Profit\n- EBITDA\n- ROE\n- ROCE\n"
        "- YoY Growth or Decline (if available)\n\n"
        "Return in key-value pairs in plain text format (e.g., Revenue: ₹150 Cr)."
    )
    try:
        response = llm.invoke(prompt + "\n\n" + text[:3000])
        return response.content if hasattr(response, "content") else str(response)

    except Exception as e:
        return f"❌ Metric Extraction Error: {str(e)}"


import matplotlib.pyplot as plt
import re
from io import BytesIO

def generate_financial_chart(insights_text):
    numeric_metrics = {}

    for line in insights_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Extract number (supports ₹, commas, decimals)
            match = re.search(r"([\d,.]+)", value.replace(",", ""))
            if match:
                try:
                    numeric_value = float(match.group(1))
                    numeric_metrics[key] = numeric_value
                except:
                    pass

    if not numeric_metrics:
        return None

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(numeric_metrics.keys(), numeric_metrics.values(), color="teal")
    ax.set_ylabel("Value")
    ax.set_title("📊 Financial Insights (Chart)")
    plt.xticks(rotation=45, ha="right")

    # Save to buffer and return
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf
