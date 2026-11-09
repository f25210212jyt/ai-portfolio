# AI 辅助编程实录 - 第三周

## 一、 本周目标与任务
完成 `vocab_tool.py` 独立运行，并基于AI辅助实现“生成填空题”的扩展功能。同时阅读Python官方英文文档，提取生词并记录。

## 二、 AI 结对编程过程
**我的 Prompt：**
“我有一个处理生词的脚本，现在我想增加一个生成填空题的功能。我希望读取原文，把指定的生词替换成下划线 `___`，并输出到txt文件里。请给我代码。”

**AI 给出的初始代码（部分）：**
```python
def generate_cloze(text, target_words):
    for word in target_words:
        text = text.replace(word, '___')
    return text