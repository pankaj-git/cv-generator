# AI CV Generator — External Resume to Company Format Converter

## 📌 Project Overview

This application converts external candidate resumes (PDF or DOCX) into a standardized company CV format (DOCX) automatically using:

- Python
- Streamlit (UI)
- LangChain
- OpenAI LLM
- docxtpl (for Word template generation)

The tool will be used internally by recruiters/architects to quickly convert candidate resumes into company-defined format before sending to clients.

---

# 🎯 Functional Requirements

## UI Behavior

The UI will be built using **Streamlit** (Python only, no React).

Flow:

1. User uploads external CV (PDF or DOCX)
2. User clicks **Generate Company CV**
3. UI shows loading message/spinner:
   **"Generating company CV… please wait"**
4. System processes resume using LLM
5. Once complete:
   - Show success message
   - Show download button for generated DOCX

Optional:
- Show preview of extracted name/email/projects count

---

# 📂 Input & Output

## Input

External candidate resume:
- PDF format OR
- DOCX format

Examples:
- `rohitsavajCV.pdf`
- `AkshayBartakke_Angular.docx`

## Output

Company formatted resume in DOCX:

Naming format:
```
COMPANY DETAILED PROFILE-{CandidateID}-{CandidateName}.docx
```
If CandidateID not provided:
```
COMPANY DETAILED PROFILE-{autoid}-{CandidateName}.docx
```

---

# 🧠 AI Processing Flow

### Step 1 — Upload Resume
User uploads resume via Streamlit UI.

### Step 2 — Extract Resume Text
If PDF:
- Use pymupdf (fitz)
If DOCX:
- Use python-docx
Extract raw text from resume.

### Step 3 — LLM Structured Extraction
Use:
- LangChain
- OpenAI API
- Pydantic schema
Convert raw resume text → structured JSON.

IMPORTANT RULES:
- Do NOT hallucinate data
- Use only resume content
- If data missing → empty string/array
- Temperature = 0
- Return STRICT JSON only

---

# 📊 Resume JSON Structure (Important)

LLM must output structured JSON like:
```
{
 name: "",
 email: "",
 phone: "",
 location: "",
 linkedin: "",
 summary: [],
 education: [],
 certifications: [],
 awards: [],
 skills: {
   domains:{primary:"",secondary:""},
   programming:{primary:"",secondary:""},
   frameworks:{primary:"",secondary:""},
   build_tools:{primary:"",secondary:""},
   testing:{primary:"",secondary:""},
   dev_tools:{primary:"",secondary:""},
   cicd:{primary:"",secondary:""},
   containerization:{primary:"",secondary:""},
   databases:{primary:"",secondary:""},
   issue_tracking:{primary:"",secondary:""},
   genai:{primary:"",secondary:""}
 },
 roles:[
   {title:"", company:"", dates:"", description:""}
 ],
 projects:[
   {
    name:"",
    duration:"",
    role:"",
    description:"",
    key_activities:"",
    bullets:[],
    tools:"",
    technologies:"",
    skills:""
   }
 ]
}
```

---

# 📝 DOCX Template Filling

The company template DOCX already exists.
Location:
```
templates/COMPANY CV-Template.docx
```
Template uses **docxtpl Jinja placeholders** like:
```
{{ name }}
{{ email }}
{{ phone }}

{% for p in projects %}
Project {{loop.index}} – {{p.name}}
{% endfor %}
```
Use:
```
docxtpl
```
to fill template using JSON output.

---

# 🏗️ Project Architecture

## Folder Structure
```
cv-generator/
│
├── app.py                 # Streamlit UI
├── requirements.txt
├── .env
│
├── templates/
│   └── COMPANY CV-Template.docx
│
├── uploads/
├── outputs/
│
├── services/
│   ├── extract_text.py
│   ├── llm_extract.py
│   ├── render_docx.py
│   └── normalize.py
│
└── models/
    └── resume_schema.py
```

---

# ⚙️ Tech Stack

## UI
- Streamlit
## Backend
- Python 3.11+
## AI
- LangChain
- OpenAI API
## Document Processing
- docxtpl
- python-docx
- pymupdf
## Validation
- Pydantic

---

# 🔑 Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
```

---

# 📦 requirements.txt
```
streamlit
python-dotenv
pydantic
docxtpl
python-docx
pymupdf
langchain
langchain-openai
openai
```

---

# 🚀 How Application Should Work
1. Run Streamlit UI
2. Upload resume
3. Click Generate
4. Show spinner/loading
5. Call LLM extraction
6. Fill company template
7. Save DOCX
8. Show download button

---

# 🧠 LLM Prompt Rules (Very Important)
System prompt:
- Extract resume into structured JSON
- No hallucination
- Use only resume data
- Missing data = empty
- Strict JSON only
- No extra text
Temperature:
```
0
```

---

# 🛡️ Constraints
- No React frontend
- Only Python UI (Streamlit)
- Must support PDF & DOCX input
- Must generate DOCX output
- Must work locally
- OpenAI key will be added later by user

---

# 🎯 Goal for GitHub Copilot
When generating code:
Copilot should generate:
- Full Streamlit UI
- Resume parser
- LLM extraction module
- Pydantic schema
- docxtpl template renderer
- Download functionality
Everything should run locally after adding:
```
OPENAI_API_KEY
```

---

# 👨‍💻 Developer Instructions
1. Generate all Python modules
2. Keep code clean and modular
3. Add comments
4. Add error handling
5. Ensure docxtpl mapping matches JSON schema
6. Ensure download button works after generation

---

# 🏁 End Goal
A one-click internal AI tool that converts any external resume into company-standard formatted DOCX using LLM automation.

---

## How to Run

```sh
cd cv-generator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Add your OpenAI key in `.env` before running.
