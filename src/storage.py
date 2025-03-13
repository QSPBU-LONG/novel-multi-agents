from src.models import NovelOutline, Character, ChapterContent, ChapterSummary


# 小说内容存储
class NovelStorage:
    def __init__(self):
        self.outline = None
        self.characters = []
        self.chapters = {}
        self.chapter_summaries = {}
        self.feedback = {}

    def save_to_file(self, filename=None):
        """将完成的小说保存到文件"""
        if not self.outline:
            return "没有小说可保存"

        if not filename:
            filename = f"{self.outline.title.replace(' ', '_')}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            # 写入标题和信息
            f.write(f"# {self.outline.title}\n\n")
            f.write(f"类型: {self.outline.genre}\n")
            f.write(f"主题: {self.outline.theme}\n\n")
            f.write(f"## 情节概要\n\n{self.outline.plot_summary}\n\n")

            # 写入角色档案
            f.write("## 角色\n\n")
            for character in self.characters:
                f.write(f"### {character.name}\n")
                f.write(f"背景: {character.background}\n")
                f.write(f"性格: {character.personality}\n")
                f.write(f"目标: {', '.join(character.goals)}\n")
                f.write(f"冲突: {', '.join(character.conflicts)}\n")
                f.write(f"成长弧线: {character.arc}\n\n")

            # 按顺序写入章节
            f.write("## 小说内容\n\n")
            for i in range(1, len(self.outline.chapters) + 1):
                if i in self.chapters:
                    chapter = self.chapters[i]
                    f.write(f"\n\n### 第{i}章: {chapter.title}\n\n")
                    f.write(chapter.content)

                    # 添加章节字数统计
                    word_count = len(chapter.content.split())
                    f.write(f"\n\n[字数：{word_count}]\n\n")

        print(f"小说已保存至 {filename}")
        return f"小说已保存至 {filename}"