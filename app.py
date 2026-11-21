import io
import json
import os
import re
import textwrap
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

st.set_page_config(
    page_title="Viva Question Generator",
    page_icon="🎓",
    layout="wide",
)


def apply_custom_style():
    st.markdown(
        """
        <style>
            .main {
                background: linear-gradient(180deg, #f7f9fc 0%, #eef4ff 100%);
            }
            .hero-box {
                background: linear-gradient(135deg, #0f172a, #1d4ed8);
                color: white;
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
                margin-bottom: 1.25rem;
            }
            .hero-box h1 {
                margin-bottom: 0.5rem;
            }
            .info-card {
                background: white;
                padding: 1rem 1.2rem;
                border-radius: 16px;
                border: 1px solid #dbe7ff;
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
                margin-bottom: 1rem;
            }
            .category-title {
                padding: 0.6rem 1rem;
                border-radius: 12px;
                font-weight: 700;
                margin: 0.6rem 0 0.8rem 0;
                display: inline-block;
            }
            .easy-tag {
                background: #dcfce7;
                color: #166534;
            }
            .medium-tag {
                background: #fef3c7;
                color: #92400e;
            }
            .hard-tag {
                background: #fee2e2;
                color: #991b1b;
            }
            .stDownloadButton > button, .stButton > button {
                border-radius: 10px;
                padding: 0.6rem 1rem;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def extract_text_from_pdf(uploaded_file):
    try:
        uploaded_file.seek(0)
        reader = PdfReader(uploaded_file)

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:
                raise ValueError(
                    "This PDF is encrypted and cannot be read. Please upload an unlocked PDF."
                ) from exc

        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text.strip())

        full_text = "\n".join(pages_text).strip()
        if not full_text:
            raise ValueError(
                "No readable text was found in the PDF. Try another PDF or use a text-based report."
            )

        cleaned_text = re.sub(r"\s+", " ", full_text)
        return cleaned_text[:18000]
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "The PDF could not be read. Please upload a valid and readable PDF file."
        ) from exc


def extract_json_from_response(raw_text):
    raw_text = raw_text.strip()

    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```(?:json)?", "", raw_text).strip()
        raw_text = re.sub(r"```$", "", raw_text).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("The AI response could not be converted into JSON.")


def validate_questions(data):
    required_categories = ["easy", "medium", "hard"]

    for category in required_categories:
        if category not in data or not isinstance(data[category], list):
            raise ValueError(f"Missing or invalid category: {category}")
        if len(data[category]) != 5:
            raise ValueError(f"The category '{category}' must contain exactly 5 questions.")

        for item in data[category]:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid item format in category: {category}")
            if "question" not in item or "answer" not in item:
                raise ValueError(f"Each item in '{category}' must have question and answer.")

    return data


def generate_viva_questions(extracted_text, api_key):
    client = genai.Client(api_key=api_key)
    model_names = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.6-flash",
        "gemini-3.8-flash",
    ]

    prompt = f"""
You are an academic viva assistant.
Based on the following project report text, generate exactly 15 likely viva questions with short answers.

Rules:
1. Create exactly 5 easy questions, 5 medium questions, and 5 hard questions.
2. Keep answers short, clear, and student-friendly.
3. Make questions relevant to the uploaded report only.
4. Do not repeat questions.
5. Return only valid JSON in this exact format:

{{
  "easy": [
    {{"question": "Question 1", "answer": "Short answer 1"}}
  ],
  "medium": [
    {{"question": "Question 1", "answer": "Short answer 1"}}
  ],
  "hard": [
    {{"question": "Question 1", "answer": "Short answer 1"}}
  ]
}}

Project report text:
{extracted_text}
"""

    last_error = None
    response = None
    for model_name in model_names:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"temperature": 0.4, "response_mime_type": "application/json"},
            )
            if response:
                break
        except Exception as exc:
            last_error = exc
            continue

    if response is None:
        raise RuntimeError(
            f"Gemini API request failed. Check your API key, internet connection, usage limits, or model availability. Details: {last_error}"
        )

    if not hasattr(response, "text") or not response.text:
        raise RuntimeError("Gemini returned an empty response. Please try again.")

    try:
        data = extract_json_from_response(response.text)
        return validate_questions(data)
    except Exception as exc:
        raise RuntimeError(
            "The generated response was not in the expected format. Please try again."
        ) from exc


def build_pdf_bytes(questions_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("Viva Question Generator Report", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 12))

    for category in ["easy", "medium", "hard"]:
        heading = Paragraph(category.capitalize(), styles["Heading2"])
        story.append(heading)
        story.append(Spacer(1, 8))

        for index, item in enumerate(questions_data[category], start=1):
            question_text = f"<b>Q{index}:</b> {item['question']}"
            answer_text = f"<b>Answer:</b> {item['answer']}"
            story.append(Paragraph(question_text, styles["BodyText"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph(answer_text, styles["BodyText"]))
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def render_category(title, items, css_class):
    st.markdown(
        f"<div class='category-title {css_class}'>{title}</div>",
        unsafe_allow_html=True,
    )
    for index, item in enumerate(items, start=1):
        with st.expander(f"{index}. {item['question']}"):
            st.write(item["answer"])


def main():
    apply_custom_style()

    if "questions_data" not in st.session_state:
        st.session_state.questions_data = None
    if "source_file_name" not in st.session_state:
        st.session_state.source_file_name = ""

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    st.markdown(
        """
        <div class="hero-box">
            <h1>Viva Question Generator</h1>
            <p>
                Upload your project report PDF and generate likely viva questions with short answers
                using Google Gemini AI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            <div class="info-card">
                <b>How it works:</b><br>
                1. Upload a project report PDF.<br>
                2. Extract readable text using PyPDF2.<br>
                3. Send the content to Gemini AI.<br>
                4. Get 15 viva questions divided into Easy, Medium, and Hard.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="info-card">
                <b>Output format:</b><br>
                Easy: 5 questions<br>
                Medium: 5 questions<br>
                Hard: 5 questions
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not api_key:
        st.warning(
            "Gemini API key not found. Open the `.env` file and paste your key after `GEMINI_API_KEY=`."
        )

    uploaded_file = st.file_uploader("Upload your project report PDF", type=["pdf"])

    if st.button("Generate Viva Questions", use_container_width=True):
        if not api_key:
            st.error("Gemini API key is missing. Add it to the `.env` file and try again.")
        elif uploaded_file is None:
            st.error("Please upload a PDF file before generating questions.")
        else:
            with st.spinner("Reading your PDF and generating viva questions..."):
                try:
                    extracted_text = extract_text_from_pdf(uploaded_file)
                    questions_data = generate_viva_questions(extracted_text, api_key)
                    st.session_state.questions_data = questions_data
                    st.session_state.source_file_name = uploaded_file.name
                    st.success("Viva questions generated successfully.")
                except Exception as exc:
                    st.session_state.questions_data = None
                    st.error(str(exc))

    if st.session_state.questions_data:
        st.subheader("Generated Viva Questions")
        st.caption(f"Source PDF: {st.session_state.source_file_name}")

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Easy", len(st.session_state.questions_data["easy"]))
        metric_col2.metric("Medium", len(st.session_state.questions_data["medium"]))
        metric_col3.metric("Hard", len(st.session_state.questions_data["hard"]))

        render_category("Easy Questions", st.session_state.questions_data["easy"], "easy-tag")
        render_category("Medium Questions", st.session_state.questions_data["medium"], "medium-tag")
        render_category("Hard Questions", st.session_state.questions_data["hard"], "hard-tag")

        pdf_data = build_pdf_bytes(st.session_state.questions_data)
        st.download_button(
            label="Download Questions as PDF",
            data=pdf_data,
            file_name="viva_questions.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        with st.expander("Tips for viva preparation"):
            st.write(
                textwrap.dedent(
                    """
                    - Read each answer aloud once or twice.
                    - Practice explaining the project objective in simple language.
                    - Be ready to justify your methodology, tools, and results.
                    - Revise limitations and future improvements before the viva.
                    """
                ).strip()
            )


if __name__ == "__main__":
    main()
