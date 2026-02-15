Folder structure
cv_formatter/
  app.py
  services/
    extract_text.py
    llm_extract.py
    render_docx.py
    normalize.py
  models/
    resume_schema.py
  templates/
    COMPANY CV-Template.docx
  outputs/
  .env
  requirements.txt


Requirements Txt
streamlit==1.41.1
python-dotenv==1.0.1
pydantic==2.9.2
docxtpl==0.18.0
python-docx==1.1.2
pymupdf==1.24.10

langchain==0.2.16
langchain-openai==0.1.23
openai==1.45.0

Environment file
.env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

app.py (Streamlit UI with loading + download)
import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from services.extract_text import extract_text_from_file
from services.llm_extract import extract_resume_json
from services.render_docx import render_company_docx

load_dotenv()

st.set_page_config(page_title="CV Converter", layout="centered")
st.title("External CV → Company CV Converter")

uploaded = st.file_uploader("Upload external CV (PDF/DOCX)", type=["pdf", "docx"])

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


services/extract_text.py
import io
import fitz  # pymupdf
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    parts = []
    for p in doc.paragraphs:
        if p.text and p.text.strip():
            parts.append(p.text.strip())
    return "\n".join(parts).strip()

def extract_text_from_file(uploaded_file) -> str:
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)

    raise ValueError("Unsupported file type. Please upload PDF or DOCX.")


models/resume_schema.py (matches your template)
from pydantic import BaseModel, Field
from typing import List, Dict

class SkillsCategory(BaseModel):
    primary: str = ""
    secondary: str = ""

class Skills(BaseModel):
    domains: SkillsCategory = SkillsCategory()
    programming: SkillsCategory = SkillsCategory()
    frameworks: SkillsCategory = SkillsCategory()
    build_tools: SkillsCategory = SkillsCategory()
    testing: SkillsCategory = SkillsCategory()
    dev_tools: SkillsCategory = SkillsCategory()
    cicd: SkillsCategory = SkillsCategory()
    containerization: SkillsCategory = SkillsCategory()
    databases: SkillsCategory = SkillsCategory()
    issue_tracking: SkillsCategory = SkillsCategory()
    genai: SkillsCategory = SkillsCategory()

class Role(BaseModel):
    title: str = ""
    company: str = ""
    dates: str = ""
    description: str = ""

class Project(BaseModel):
    name: str = ""
    duration: str = ""
    role: str = ""
    description: str = ""
    key_activities: str = ""
    bullets: List[str] = Field(default_factory=list)
    tools: str = ""
    technologies: str = ""
    skills: str = ""

class ResumeJSON(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    summary: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    skills: Skills = Skills()
    roles: List[Role] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)


services/llm_extract.py (LangChain + OpenAI → strict JSON)
import os
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

from models.resume_schema import ResumeJSON

def extract_resume_json(raw_text: str) -> ResumeJSON:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    llm = ChatOpenAI(model=model, temperature=0)
    parser = PydanticOutputParser(pydantic_object=ResumeJSON)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You extract resume content into STRICT JSON that matches the provided schema. "
         "Rules: Use ONLY the resume text. Do NOT invent anything. "
         "If a field is missing, use empty string or empty array. "
         "Return ONLY valid JSON, no extra text."),
        ("human",
         "Resume text:\n{resume_text}\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser
    return chain.invoke({
        "resume_text": raw_text[:20000],  # avoid huge payloads; increase if needed
        "format_instructions": parser.get_format_instructions()
    })


services/render_docx.py (docxtpl fills your template)
import os
import re
from docxtpl import DocxTemplate
from models.resume_schema import ResumeJSON

TEMPLATE_PATH = os.path.join("templates", "COMPANY CV-Template.docx")
OUT_DIR = "outputs"

def safe_filename(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.replace(" ", "_")[:80] or "Candidate"

def render_company_docx(resume: ResumeJSON, candidate_id: str | None, job_id: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)

    name_part = safe_filename(resume.name)
    if candidate_id:
        out_name = f"COMPANY DETAILED PROFILE-{candidate_id}-{name_part}.docx"
    else:
        out_name = f"COMPANY DETAILED PROFILE-{job_id}-{name_part}.docx"

    out_path = os.path.join(OUT_DIR, out_name)

    tpl = DocxTemplate(TEMPLATE_PATH)

    context = resume.model_dump()  # keys match your template vars: name, email, roles, projects...
    tpl.render(context)
    tpl.save(out_path)

    return out_path


How to run
cd cv_formatter
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
