import os
import uuid
import streamlit as st

from services.extract_text import extract_text_from_file
from services.llm_extract import extract_resume_json
from services.render_docx import render_company_docx

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
OPENAI_MODEL = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")

# Optionally set as environment variables for downstream libraries
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
if OPENAI_MODEL:
    os.environ["OPENAI_MODEL"] = OPENAI_MODEL

st.set_page_config(page_title="CV Converter", layout="centered")
st.title("External CV → Company CV Converter")

uploaded = st.file_uploader("Upload external CV (DOCX only)", type=["docx"])

candidate_id = st.text_input("Candidate ID (optional, for file naming)", value="")

if uploaded:
    st.info(f"Uploaded: {uploaded.name}")

    if st.button("Generate Company CV"):
        with st.spinner("Generating company CV… Please wait."):
            # 1) Extract raw text from uploaded file
            raw_text = extract_text_from_file(uploaded)

            # 2) LLM: Convert raw text to structured JSON (Pydantic model)
            resume = extract_resume_json(raw_text)

            # 3) Render into company template docx
            job_id = str(uuid.uuid4())[:8]
            out_path = render_company_docx(
                resume=resume,
                candidate_id=candidate_id.strip() or None,
                job_id=job_id
            )

        st.success("Company CV generated successfully ✅")

        # Optional preview
        with st.expander("Preview extracted details"):
            st.write({
                "name": resume.name,
                "email": resume.email,
                "phone": resume.phone,
                "location": resume.location,
                "projects_count": len(resume.projects),
                "roles_count": len(resume.roles)
            })

        with open(out_path, "rb") as f:
            st.download_button(
                label="Download Company CV (DOCX)",
                data=f,
                file_name=os.path.basename(out_path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
