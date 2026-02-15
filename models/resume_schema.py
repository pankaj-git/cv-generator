from pydantic import BaseModel, Field
from typing import List

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
