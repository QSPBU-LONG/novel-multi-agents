from openai import AsyncOpenAI
from novle_agents import Agent, set_default_openai_client, set_default_openai_api
from src.models import *
from src.tools import *


# 设置默认客户端
def setup_client(base_url="http://localhost:11434/v1", api_key="ollama"):
    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key
    )
    set_default_openai_client(client)
    set_default_openai_api("chat_completions")
    return client


# 定义各专业Agent
def create_agents(model="qwen2.5:14b"):
    """创建并返回所有需要的agents"""

    outline_agent = Agent(
        name="outline_agent",
        instructions="""你是小说大纲创建专家。根据用户需求创建详细的小说大纲，包括:
- 标题、类型、主题、背景
- 情节概要
- 章节大纲(标题、摘要、关键事件、涉及角色、场景)
- 角色名称列表

创建一个有清晰开端、中部和结尾的叙事结构，包含适当的冲突和解决方案。
请确保最后调用函数 store_novel_outline 将大纲存储。
        """,
        model=model,
        output_type=NovelOutline,
        tools=[store_novel_outline],
    )

    character_agent = Agent(
        name="character_agent",
        instructions="""你是角色发展专家。你负责将角色名称和概要发展为丰富、复杂的角色档案，包括:
- 详细背景
- 性格特点
- 内外目标
- 冲突(内部和外部)
- 角色在故事中的成长弧线

创造真实、有缺陷且立体的角色。
        """,
        model=model,
        output_type=List[Character],
        tools=[get_novel_outline, store_characters],
    )

    chapter_writer_agent = Agent(
        name="chapter_writer_agent",
        instructions="""你是专业的小说章节撰写人。根据章节大纲、角色信息和小说上下文，写出完整章节:
- 每章必须至少包含4000字的内容，情节丰富且细节充分
- 遵循大纲
- 保持角色声音一致性
- 包含生动描写和场景细节
- 平衡对话、动作和描述
- 推进情节和角色发展
- 保持适当节奏
- 在需要时以适当的钩子结束章节

如果你被要求写章节的某一部分（开头、中间或结尾），请确保这部分内容足够丰富。
使用适合类型的引人入胜的文学风格。
        """,
        model=model,
        output_type=ChapterContent,
        tools=[get_novel_outline, get_characters, get_relevant_characters, get_chapter, get_chapter_summary,
               store_chapter],
    )

    section_writer_agent = Agent(
        name="section_writer_agent",
        instructions="""你是专业的小说章节部分撰写人。根据提供的信息，写出章节的特定部分（开头、中间或结尾）:
- 保持与整体故事和前文的连贯性
- 每个部分必须内容丰富，通常至少1500字
- 开头部分：引入场景和角色，设定基调
- 中间部分：发展冲突，推进事件
- 结尾部分：提供章节事件的结局或悬念，为下一章做铺垫

确保你的写作风格一致，角色表现符合其性格特点。
        """,
        model=model,
        output_type=ChapterSection,
        tools=[get_novel_outline, get_relevant_characters, get_chapter_summary],
    )

    summary_agent = Agent(
        name="summary_agent",
        instructions="""你是章节摘要专家。针对提供的章节内容:
1. 创建一个简明扼要的摘要（200-300字）
2. 提取章节结尾部分（最后几段，约500字）作为上下文线索

摘要应包含章节的关键事件和角色发展，以便为后续章节写作提供足够上下文。
        """,
        model=model,
        output_type=ChapterSummary,
        tools=[store_chapter_summary],
    )

    editor_agent = Agent(
        name="editor_agent",
        instructions="""你是专业小说编辑。审阅提供的章节并提供详细反馈:
- 总体质量评分(1-10)
- 写作优点
- 需要改进的地方
- 具体建议
- 修改内容(如需大幅修改)

专注于改善散文质量、角色一致性、节奏、对话和叙事吸引力。
提供有实质性、建设性的反馈。
        """,
        model=model,
        output_type=EditFeedback,
    )

    quality_evaluator = Agent(
        name="quality_evaluator",
        instructions="""你评估小说章节的质量。对每章提供:
1. 1-10分评分
2. 详细反馈(优点和不足)
3. 确定章节是否达到质量标准(分数>=8)
4. 检查章节字数是否至少4000字

评价要有建设性但严格。特别关注内容长度，必须至少4000字才能通过。
        """,
        model=model,
        output_type=QualityEvaluation,
    )

    orchestrator_agent = Agent(
        name="orchestrator_agent",
        instructions="""你是小说创作项目经理，协调整个创作过程:
1. 理解用户对小说的要求
2. 将任务委派给专业Agent(大纲创建、角色开发、章节撰写和编辑)
3. 整合不同Agent的工作成一个连贯整体
4. 向用户通报进度和结果

适当使用专业Agent团队，引导小说创作从概念到完成。
        """,
        model=model,
        handoffs=[outline_agent, character_agent, chapter_writer_agent, editor_agent],
        tools=[get_novel_outline, get_characters, get_chapter],
    )

    return {
        "outline_agent": outline_agent,
        "character_agent": character_agent,
        "chapter_writer_agent": chapter_writer_agent,
        "section_writer_agent": section_writer_agent,
        "summary_agent": summary_agent,
        "editor_agent": editor_agent,
        "quality_evaluator": quality_evaluator,
        "orchestrator_agent": orchestrator_agent
    }