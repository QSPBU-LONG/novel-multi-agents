from agents import function_tool
from src.models import NovelOutline, Character, ChapterContent, ChapterSummary
from src.storage import NovelStorage

# 创建全局存储实例
novel_storage = NovelStorage()

@function_tool
def store_novel_outline(outline: NovelOutline) -> str:
    print("调用了 store_novel_outline，保存大纲:", outline.title)
    novel_storage.outline = outline
    return f"保存了小说大纲: {outline.title}"

@function_tool
def store_characters(characters: list[Character]) -> str:
    novel_storage.characters = characters
    return f"保存了{len(characters)}个角色档案"

@function_tool
def store_chapter(chapter_number: int, chapter: ChapterContent) -> str:
    novel_storage.chapters[chapter_number] = chapter
    return f"保存了第{chapter_number}章: {chapter.title}"

@function_tool
def store_chapter_summary(chapter_number: int, summary: ChapterSummary) -> str:
    """存储章节摘要用于上下文管理"""
    novel_storage.chapter_summaries[chapter_number] = summary
    return f"保存了第{chapter_number}章摘要"

@function_tool
def get_novel_outline() -> NovelOutline:
    return novel_storage.outline

@function_tool
def get_characters() -> list[Character]:
    return novel_storage.characters

@function_tool
def get_chapter(chapter_number: int) -> ChapterContent:
    return novel_storage.chapters.get(chapter_number, None)

@function_tool
def get_chapter_summary(chapter_number: int) -> ChapterSummary:
    """获取章节摘要用于上下文管理"""
    return novel_storage.chapter_summaries.get(chapter_number, None)

@function_tool
def get_relevant_characters(character_names: list[str]) -> list[Character]:
    """只返回章节涉及的角色信息，节省token"""
    return [c for c in novel_storage.characters if c.name in character_names]

def save_chapter_directly(chapter_number: int, chapter: ChapterContent) -> str:
    """直接保存章节到存储，无需等待异步函数"""
    novel_storage.chapters[chapter_number] = chapter
    return f"保存了第{chapter_number}章: {chapter.title}"