from pydantic import BaseModel
from typing import List, Dict

class Character(BaseModel):
    name: str
    background: str
    personality: str
    goals: List[str]
    conflicts: List[str]
    arc: str

class ChapterOutline(BaseModel):
    title: str
    summary: str
    key_events: List[str]
    characters_involved: List[str]
    setting: str

class NovelOutline(BaseModel):
    title: str
    genre: str
    theme: str
    setting: str
    plot_summary: str
    chapters: List[ChapterOutline]
    characters: List[str]  # 角色名称列表，详细资料另存

class ChapterContent(BaseModel):
    title: str
    content: str
    notes: str = ""

class ChapterSection(BaseModel):
    """章节的一个部分"""
    section_type: str  # "opening", "middle", "ending"
    content: str

class ChapterSummary(BaseModel):
    """章节摘要，用于提供上下文但减少token消耗"""
    title: str
    summary: str
    ending: str  # 章节的结尾部分，作为下一章的上下文

class EditFeedback(BaseModel):
    quality_score: int  # 1-10
    strengths: List[str]
    areas_for_improvement: List[str]
    suggestions: str
    revised_content: str = ""

class QualityEvaluation(BaseModel):
    score: int  # 1-10
    feedback: str
    passes: bool  # 质量是否达标
    length_check: bool  # 长度是否达标