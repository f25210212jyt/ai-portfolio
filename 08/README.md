# 学科智能问答助手 v1.0

## 功能
- 基于 RAG 的学科智能问答助手。支持“纯对话”和“基于资料检索”两种模式自由切换，支持本地 Ollama 和云端 API 双引擎驱动。
- 提供 HSK 3-4 级别的语法、词汇及课文教学辅助回答。

## 怎么装
1. 克隆本项目到本地：
   `git clone <你的仓库链接>`
2. 安装依赖：
   `pip install -r requirements.txt`
3. 安装并启动本地模型（若使用 local 模式）：
   `ollama pull qwen2.5:0.5b`
   `ollama pull nomic-embed-text`
4. 配置环境变量：复制 `.env.example` 为 `.env`，填入你的 `DEEPSEEK_API_KEY`。

## 怎么用
- 运行主程序：
  `python week08/assistant_v1.py`
- 脚本会默认执行“三问三答”测试，并对比开/关 RAG 的结果差异。

## 已知问题
- 若本地未启动 Ollama 服务，且在代码中强制 `prefer="local"`，程序会报错提示连接失败。此时需在代码中手动将 `prefer` 切换为 `"api"` 走云端，或在终端输入 `ollama serve` 启动本地引擎。
- 当前检索切片大小为 500，有时可能会截断长篇课文的连贯语义。