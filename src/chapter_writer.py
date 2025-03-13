import asyncio
from agents import Runner, trace
from src.models import ChapterContent, ChapterOutline, ChapterSummary, ChapterSection
from src.tools import novel_storage, save_chapter_directly, store_chapter_summary

async def get_relevant_context(chapter_num: int, chapter_outline: ChapterOutline) -> str:
    """获取当前章节的相关上下文，减少token消耗"""
    context = ""

    # 获取相关角色信息（只包含章节涉及的角色）
    relevant_chars = []
    for char in novel_storage.characters:
        if char.name in chapter_outline.characters_involved:
            # 简化角色信息以减少token使用
            char_summary = f"角色名：{char.name}\n性格：{char.personality}\n"
            char_summary += f"目标：{', '.join(char.goals[:2])}\n"  # 只包含前两个目标
            relevant_chars.append(char_summary)

    if relevant_chars:
        context += "相关角色信息：\n" + "\n".join(relevant_chars) + "\n\n"

    # 获取前一章的摘要（如果有）
    if chapter_num > 1 and (chapter_num - 1) in novel_storage.chapter_summaries:
        prev_summary = novel_storage.chapter_summaries[chapter_num - 1]
        context += f"前一章（{prev_summary.title}）摘要：\n{prev_summary.summary}\n"
        context += f"前一章结尾：\n{prev_summary.ending}\n\n"

    return context

async def create_chapter_summary(chapter_num: int, chapter_content: ChapterContent, summary_agent) -> None:
    """为章节创建摘要，用于后续章节的上下文"""
    summary_prompt = f"""
    为以下章节创建摘要：

    章节标题：{chapter_content.title}

    章节内容：
    {chapter_content.content[:2000]}...  # 只使用开头部分以节省token

    请创建：
    1. 简明扼要的摘要（200-300字）
    2. 提取章节结尾部分（约500字）
    """

    summary_result = await Runner.run(
        summary_agent,
        input=[{"content": summary_prompt, "role": "user"}]
    )

    # 存储摘要
    chapter_summary = summary_result.final_output
    await store_chapter_summary(chapter_num, chapter_summary)
    print(f"已创建第{chapter_num}章摘要")

async def write_chapter_in_sections(chapter_num: int, chapter_outline: ChapterOutline, section_writer_agent, chapter_writer_agent) -> ChapterContent:
    """分段写作章节，以避免上下文限制"""
    print(f"开始分段撰写第{chapter_num}章: {chapter_outline.title}")

    # 获取相关上下文
    context = await get_relevant_context(chapter_num, chapter_outline)

    # 章节基本信息
    base_info = f"""
    第{chapter_num}章: {chapter_outline.title}
    章节摘要: {chapter_outline.summary}
    关键事件: {', '.join(chapter_outline.key_events)}
    场景: {chapter_outline.setting}
    涉及角色: {', '.join(chapter_outline.characters_involved)}
    """

    # 分三部分写作：开头、中间、结尾
    sections = []

    # 1. 开头部分 (约1500字)
    opening_prompt = f"""
    {context}

    {base_info}

    请撰写这一章的开头部分（约1500字），包括：
    - 场景描述
    - 引入主要人物
    - 设定章节基调
    - 引出本章主要事件的开端

    确保内容生动、细节丰富，字数不少于1500字。
    """
    opening_result = await Runner.run(
        section_writer_agent,
        input=[{"content": opening_prompt, "role": "user"}]
    )
    opening_section = opening_result.final_output.content
    sections.append(opening_section)
    print(f"  ✓ 完成开头部分 ({len(opening_section.split())}字)")

    # 2. 中间部分 (约1500-2000字)
    # 提供前文作为上下文
    middle_prompt = f"""
    {base_info}

    本章开头部分内容：
    {opening_section[-500:]}  # 只提供开头部分的结尾段落作为上下文连接

    请继续撰写本章的中间部分（约2000字），包括：
    - 发展章节的主要冲突和事件
    - 展示角色互动
    - 推进情节发展
    - 增加情节紧张度或复杂性

    确保内容生动、细节丰富，字数不少于1500字，衔接流畅。
    """
    middle_result = await Runner.run(
        section_writer_agent,
        input=[{"content": middle_prompt, "role": "user"}]
    )
    middle_section = middle_result.final_output.content
    sections.append(middle_section)
    print(f"  ✓ 完成中间部分 ({len(middle_section.split())}字)")

    # 3. 结尾部分 (约1500字)
    ending_prompt = f"""
    {base_info}

    本章前文内容摘要：
    开头：{opening_section[:300]}...
    中间部分结尾：{middle_section[-500:]}

    请完成本章的结尾部分（约1500字），包括：
    - 解决或推进本章的主要冲突
    - 展示角色的反应和情感变化
    - 为下一章埋下伏笔
    - 以合适的钩子结束本章

    确保内容生动、细节丰富，字数不少于1500字，与前文无缝衔接。
    """
    ending_result = await Runner.run(
        section_writer_agent,
        input=[{"content": ending_prompt, "role": "user"}]
    )
    ending_section = ending_result.final_output.content
    sections.append(ending_section)
    print(f"  ✓ 完成结尾部分 ({len(ending_section.split())}字)")

    # 合并所有部分
    full_content = "\n\n".join(sections)

    # 检查总字数
    total_words = len(full_content.split())
    print(f"  ✓ 章节完成，总字数: {total_words}")

    if total_words < 4000:
        print(f"  ! 章节字数不足，进行扩展...")

        # 确定要扩展的部分（通常是中间部分）
        expansion_prompt = f"""
        {base_info}

        目前章节内容（总字数只有{total_words}字，需要扩展）：
        {full_content[:500]}...（中间内容省略）...{full_content[-500:]}

        请扩展这个章节的内容，添加更多细节、描写和对话，使总字数达到至少4000字。
        你可以：
        - 添加更多场景描述
        - 扩展角色对话
        - 增加角色内心活动描写
        - 丰富情节细节

        扩展后的章节应该保持原有情节走向不变，只是更加丰富和详细。
        """

        expansion_result = await Runner.run(
            chapter_writer_agent,
            input=[{"content": expansion_prompt, "role": "user"}]
        )

        expanded_content = expansion_result.final_output.content
        total_words = len(expanded_content.split())
        print(f"  ✓ 扩展完成，新字数: {total_words}")

        # 使用扩展后的内容
        full_content = expanded_content

    return ChapterContent(title=chapter_outline.title, content=full_content)

async def write_chapter_with_quality_loop(chapter_num: int, chapter_outline: ChapterOutline, agents):
    """编写并改进章节，直到满足质量标准"""
    print(f"\n开始编写第{chapter_num}章: {chapter_outline.title}")

    with trace(f"第{chapter_num}章质量循环"):
        iteration = 1
        while True:
            print(f"撰写第{chapter_num}章 (迭代{iteration})...")

            # 使用分段方法生成章节
            chapter_content = await write_chapter_in_sections(
                chapter_num,
                chapter_outline,
                agents["section_writer_agent"],
                agents["chapter_writer_agent"]
            )

            # 评估质量
            evaluation_prompt = f"""
            评估这个章节的质量:

            章节标题: {chapter_content.title}
            字数: {len(chapter_content.content.split())}

            章节内容:
            {chapter_content.content}

            请评估以上章节的质量，特别关注:
            1. 文学质量和吸引力 (情节、描写、对话等)
            2. 与大纲和人物设定的一致性
            3. 内容长度是否至少4000字
            """

            evaluation_result = await Runner.run(
                agents["quality_evaluator"],
                input=[{"content": evaluation_prompt, "role": "user"}]
            )

            result = evaluation_result.final_output
            print(f"质量评分: {result.score}/10")
            print(f"字数检查: {'通过' if result.length_check else '未通过'}")

            if result.passes and result.length_check:
                print("章节通过质量和字数检查!")
                save_chapter_directly(chapter_num, chapter_content)

                # 创建章节摘要用于后续章节的上下文
                await create_chapter_summary(chapter_num, chapter_content, agents["summary_agent"])
                break

            if not result.length_check:
                print(f"章节字数不足。反馈: {result.feedback}")
            elif not result.passes:
                print(f"章节质量需要提升。反馈: {result.feedback}")

            # 根据反馈改进
            revision_prompt = f"""
            之前的章节草稿需要改进:

            反馈: {result.feedback}

            请根据此反馈重写章节，确保:
            1. 解决指出的问题
            2. 保持情节一致性
            3. 确保字数至少4000字

            章节大纲:
            标题: {chapter_outline.title}
            摘要: {chapter_outline.summary}
            关键事件: {', '.join(chapter_outline.key_events)}
            """

            iteration += 1
            if iteration > 3:  # 限制迭代次数
                print("达到最大迭代次数，接受当前版本")
                save_chapter_directly(chapter_num, chapter_content)
                await create_chapter_summary(chapter_num, chapter_content, agents["summary_agent"])
                break