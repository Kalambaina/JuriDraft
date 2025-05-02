import gradio as gr
import requests
import re
import os
from docx import Document

import uvicorn

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))  # 7860 is default for Gradio, Render may override
    uvicorn.run("lexidraft_integration:lexidraft_ui", host="0.0.0.0", port=port)


# ========== API Configuration ==========
API_KEY = "AIzaSyALyNrInhxAQ9kbr8XbxpXiA6gDCsQUYXc"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# ========== Ensure output directory exists ==========
os.makedirs("outputs", exist_ok=True)

# ========== Output Cleaner ==========
def clean_output(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    disclaimer_patterns = [
        r"This is not (a substitute for|legal) advice.*",
        r"I am not a lawyer.*",
        r"As an AI language model.*",
        r"The model's responses.*",
        r"Please consult.*(a licensed attorney|legal professional).*",
        r"The information provided.*(general informational|not constitute).*",
        r"Always seek professional legal advice.*",
        r"Note:.*legal.*",
        r"This response is for informational purposes.*",
        r"Disclaimer*",
        r"Recommendation*",
        r"This analysis is based on my understanding*",
        r"Okay, let's provide a legal opinion*",
        r"Important Notes*",
    ]
    for pattern in disclaimer_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return re.sub(r"\n{2,}", "\n\n", text).strip()

# ========== Core Gemini Request Function ==========
def ask_gemini(prompt):
    payload = { "contents": [{"parts": [{"text": prompt}]}] }
    response = requests.post(ENDPOINT, json=payload)
    result = response.json()
    try:
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return clean_output(raw_text)
    except:
        return "Error: Unable to fetch response. Please check the prompt or API."

# ========== Feature Functions ==========
def draft_document(document_type, facts):
    prompt = f"Draft a {document_type} based on the following facts:\n\n{facts}"
    return ask_gemini(prompt)

def save_to_docx(text, filename="generated_draft.docx"):
    file_path = os.path.join("outputs", filename)
    doc = Document()
    doc.add_paragraph(text)
    doc.save(file_path)
    return file_path

def legal_research(query):
    prompt = f"What is the position of Nigerian law on: {query}?"
    return ask_gemini(prompt)

def generate_case_brief(case_summary):
    prompt = f"Using IRAC format, generate a case brief from the following judgment summary:\n\n{case_summary}"
    return ask_gemini(prompt)

def cite_with_statute(context):
    prompt = f"Provide a legal opinion on the following matter, and include relevant Nigerian statutes:\n\n{context}"
    return ask_gemini(prompt)

def generate_citation(case_title):
    prompt = f"Generate the proper Nigerian legal citation for: {case_title}\nFormat it in N.W.L.R. or All N.L.R. style."
    return ask_gemini(prompt)

# ========== Gradio UI ==========
with gr.Blocks() as lexidraft_ui:
    gr.Markdown("## ⚖️ JuriDraft - AI Legal Assistant (By LegalTech Innovators)")

    with gr.Tab("📄 Legal Drafting"):
        doc_type = gr.Textbox(label="Document Type (e.g., Affidavit, Motion, Writ, Agreement)")
        doc_facts = gr.Textbox(label="Key Facts", lines=4)
        draft_btn = gr.Button("Generate Document")
        draft_output = gr.Textbox(label="Generated Draft")
        download_output = gr.File(label="📥 Download .docx")

        def generate_and_download(t, f):
            draft = draft_document(t, f)
            file_path = save_to_docx(draft)
            return draft, file_path

        draft_btn.click(
            fn=generate_and_download,
            inputs=[doc_type, doc_facts],
            outputs=[draft_output, download_output]
        )

    with gr.Tab("🔎 Legal Research"):
        query_input = gr.Textbox(label="Research Query")
        research_btn = gr.Button("Run Research")
        research_output = gr.Textbox(label="Research Result")
        research_download = gr.File(label="📥 Download Research .docx")

        def research_and_download(query):
            result = legal_research(query)
            file_path = save_to_docx(result, "legal_research_result.docx")
            return result, file_path

        research_btn.click(
            fn=research_and_download,
            inputs=query_input,
            outputs=[research_output, research_download]
        )

    with gr.Tab("📚 Case Brief Generator"):
        case_summary = gr.Textbox(label="Judgment Summary", lines=6)
        case_btn = gr.Button("Generate Case Brief")
        case_output = gr.Textbox(label="Case Brief Output")
        case_download = gr.File(label="📥 Download Case Brief .docx")

        def case_and_download(summary):
            case_brief = generate_case_brief(summary)
            file_path = save_to_docx(case_brief, "case_brief.docx")
            return case_brief, file_path

        case_btn.click(
            fn=case_and_download,
            inputs=case_summary,
            outputs=[case_output, case_download]
        )

    with gr.Tab("⚖️ Statute Integration"):
        statute_context = gr.Textbox(label="Legal Context", lines=4)
        statute_btn = gr.Button("Generate with Statute Reference")
        statute_output = gr.Textbox(label="Draft with Statutes")
        statute_download = gr.File(label="📥 Download Statute Draft .docx")

        def statute_and_download(context):
            result = cite_with_statute(context)
            file_path = save_to_docx(result, "statute_draft.docx")
            return result, file_path

        statute_btn.click(
            fn=statute_and_download,
            inputs=statute_context,
            outputs=[statute_output, statute_download]
        )

    with gr.Tab("📖 Legal Citation Tool"):
        citation_case = gr.Textbox(label="Case Title or Name")
        citation_btn = gr.Button("Generate Citation")
        citation_output = gr.Textbox(label="Formatted Citation")
        citation_download = gr.File(label="📥 Download Citation .docx")

        def citation_and_download(case_title):
            citation = generate_citation(case_title)
            file_path = save_to_docx(citation, "citation_result.docx")
            return citation, file_path

        citation_btn.click(
            fn=citation_and_download,
            inputs=citation_case,
            outputs=[citation_output, citation_download]
        )

lexidraft_ui.launch(share=True)
