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
         "You are an expert resume parser. Extract all possible information from the provided resume text and output STRICT JSON matching the schema below. "
         "Do NOT hallucinate or invent data. Use only the information present in the resume. "
         "If a field is missing, use an empty string or empty array. "
         "For each skills category (domains, programming, frameworks, build_tools, testing, dev_tools, cicd, containerization, databases, issue_tracking, genai), extract both primary and secondary skills if available. "
         "For each project, extract all available details, including bullets, tools, technologies, and skills. "
         "For expertise, extract all relevant bullet points or summary lines. "
         "Return ONLY valid JSON, no extra text.\n\n"
         "Schema:\n"
         f"{ResumeJSON.schema_json(indent=2)}"
        ),
        ("human",
         "Resume text:\n{resume_text}\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser
    return chain.invoke({
        "resume_text": raw_text[:20000],  # avoid huge payloads; increase if needed
        "format_instructions": parser.get_format_instructions()
    })
