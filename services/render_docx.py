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
