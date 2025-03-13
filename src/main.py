import asyncio
import uuid
from agents import Runner, trace
from src.models import NovelOutline
from src.novle_agents import setup_client, create_agents
from src.tools import novel_storage
from src.chapter_writer import write_chapter_with_quality_loop


async def create_novel(user_prompt=None):
    # 设置模型客户端
    setup_client()

    # 创建Agent
    agents = create_agents()

    # 创建对话ID追踪整个创作过程
    conversation_id = "novel_project_" + str(uuid.uuid4())[:8]

    # 获取用户输入
    if not user_prompt:
        user_prompt = input("请描述你想创作的小说(类型、主题、背景等): ")

    # 为整个工作流使用追踪
    with trace("小说创作", group_id=conversation_id):
        print("开始小说创作过程...")

        # 步骤1: 创建大纲
        print("创建小说大纲...")
        messages = [
            {"role": "system", "content": agents["outline_agent"].instructions},
            {"role": "user", "content": user_prompt}
        ]
        outline_result = await Runner.run(
            agents["outline_agent"],
            input=messages,
            max_turns=10
        )

        # 检查大纲是否已存储
        if not novel_storage.outline:
            try:
                outline_obj = NovelOutline.model_validate(outline_result.final_output)
                novel_storage.outline = outline_obj
                print("通过解析大纲返回值存储了大纲。")
            except Exception as e:
                print("大纲解析失败：", e)
                raise ValueError("小说大纲未能生成，请检查大纲创建 Agent 是否正常工作！")

        print("✓ 小说大纲已创建")
        print(f"标题: {novel_storage.outline.title}")
        print(f"类型: {novel_storage.outline.genre}")
        print(f"章节数: {len(novel_storage.outline.chapters)}")

        # 步骤2: 开发角色
        print("\n开发角色档案...")
        messages_for_character = [
            {"role": "system", "content": agents["character_agent"].instructions},
            {"role": "user", "content": "根据大纲开发详细的角色档案"}
        ]
        character_result = await Runner.run(
            agents["character_agent"],
            input=messages_for_character,
            max_turns=10
        )
        print("✓ 角色档案已创建")
        print(f"角色: {', '.join([c.name for c in novel_storage.characters])}")

        # 步骤3: 按顺序写章节
        print("\n开始写作章节...")
        for i, chapter_outline in enumerate(novel_storage.outline.chapters):
            chapter_num = i + 1
            await write_chapter_with_quality_loop(chapter_num, chapter_outline, agents)
            print(f"✓ 第{chapter_num}章已完成")

            # 输出章节字数统计
            chapter = novel_storage.chapters.get(chapter_num)
            if chapter:
                word_count = len(chapter.content.split())
                print(f"  章节字数: {word_count}")

        # 保存完成的小说
        print("\n完成小说...")
        novel_storage.save_to_file()

        print("\n✓ 小说创作完成!")
        return "小说创作完成!"


# 运行程序
if __name__ == "__main__":
    asyncio.run(create_novel())