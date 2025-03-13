# novel-multi-agents

novel-multi-agents是一个利用opeai-agnet-SDK进行小说创作的框架，通过多个专业化AI智能体协作完成从大纲构思到章节写作的全流程。
该项目使用Ollama本地部署模型创建每个Agent，也可以使用在线大模型或者其他类似LLM运行环境


## 目前智能体构成

- **大纲创建专家**：负责创建详细的小说大纲
- **角色开发专家**：根据大纲深化角色设定和背景故事
- **章节撰写专家**：负责根据大纲和角色撰写章节内容
- **编辑专家**：评估章节质量并提供改进建议
- **协调者**：协调整个创作流程

## 安装与使用

- Python 3.11+
- (如果使用本地模型)[Ollama](https://ollama.ai/)或类似LLM运行环境

### 安装步骤

1. 安装依赖
pip install -r requirements.txt

2. （如果使用Ollama部署的本地模型）启动Ollama并加载模型
ollama run qwen2.5:14b

### 使用方法

运行主程序开始创作：

python -m src.main

程序会提示输入你想创作的小说类型、主题、背景等信息，然后自动开始创作流程。

## 配置

你可以在`src/novel_agents.py`中调整模型参数：


# 修改默认模型
agents = create_agents(model="qwen2.5:14b")  # 改为你喜欢的模型
# 开发者说明
src/models.py - 包含所有数据模型定义 
src/storage.py - 负责存储小说内容
src/tools.py - 定义工具函数供各智能体使用
src/novel_agents.py - 定义各专业智能体
src/chapter_writer.py - 章节写作相关逻辑
src/main.py - 主程序入口
# 输出示例
生成的小说会保存为TXT文件，格式如下：

# 小说标题

类型: 科幻
主题: 宇宙探索

## 情节概要

在2150年，人类第一次接触到...

## 角色

### 张三
背景: ...
性格: ...
目标: ...
冲突: ...
成长弧线: ...

## 小说内容

### 第1章: 新的开始

（章节内容）

[字数：4356]
