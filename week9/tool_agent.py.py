# W9 手写最小工具调用循环（不用框架）
# 依赖：pip install openai python-dotenv
import os
import csv
import sys
import ast
import json
import re
import operator
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  数据路径 + 加载 .env

weekpath.load_env()

import openai  # noqa: E402

VOCAB = weekpath.data_path("生词表.csv")

# 默认走 DeepSeek 云端；教师机演示可通过环境变量切到本机 Ollama
# （OpenAI 兼容端点），例如 DEEPSEEK_BASE_URL=http://localhost:11434/v1
# DEEPSEEK_MODEL=llama3.1:8b-local。不设置时行为与云端口径完全一致。
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("未配置 DEEPSEEK_API_KEY，请先在 .env 中填写")
        base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        _client = openai.OpenAI(base_url=base, api_key=key)
    return _client


def get_time():
    return str(datetime.datetime.now())


# ---- 安全计算：白名单 AST，绝不使用裸 eval ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只允许数字与 + - * / ** % 运算")


def calc(expr):
    """教学演示用：只做四则运算。为什么不用 eval？
    因为 eval 会执行任意 Python 代码，是典型的安全反模式（本课程伦理红线之一）。"""
    try:
        return str(_eval_node(ast.parse(str(expr), mode="eval")))
    except ZeroDivisionError:
        return "错误：除数为 0"
    except Exception as e:
        return "拒绝计算：%s" % e


def hsk_level(word):
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["词汇"].strip() == str(word).strip():
                return "%s 是 %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


def _parse_level(target_level):
    """把 '4'、'HSK4'、'四级' 等统一解析为 1-9 的整数。"""
    s = str(target_level).strip()
    m = re.search(r"[1-9]", s)
    if m:
        return int(m.group())
    cn = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9}
    for k, v in cn.items():
        if k in s:
            return v
    raise ValueError("目标等级需为 HSK 1-9 的数字，如 '4' 或 'HSK4'")


def _read_text_arg(text):
    """允许模型传课文原文，也允许传文件路径。路径支持根目录相对路径和 data/ 文件名。"""
    s = str(text)
    if "\n" in s or len(s) > 80:
        return s
    candidates = [
        s,
        weekpath.root_path(s),
        weekpath.data_path(os.path.basename(s)),
    ]
    for p in candidates:
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                return f.read()
    return s


def evaluate_text_difficulty(text, target_level="4"):
    """第 4 个工具：课文难度评估。

    输入：
        text: 课文原文，或课文文件路径（如 data/愚公移山.txt）
        target_level: 目标 HSK 等级，1-9，支持 '4'、'HSK4'、'四级'
    输出：
        目标等级、词表命中总次数、已学词命中次数、生词覆盖率、超纲词列表。

    统计口径：基于课程 data/生词表.csv 逐词做字符串匹配；
    词表外词语暂不统计；允许词条字符串重叠。适合课堂演示与作业提交。
    """
    text = _read_text_arg(text)
    target = _parse_level(target_level)

    rows = []
    with open(VOCAB, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total_hits = 0
    known_hits = 0
    over = []

    for row in rows:
        word = row["词汇"].strip()
        if not word:
            continue
        cnt = str(text).count(word)
        if cnt <= 0:
            continue
        lvl = int(str(row["HSK等级"]).strip())
        total_hits += cnt
        if lvl <= target:
            known_hits += cnt
        else:
            over.append((word, lvl, cnt))

    coverage = 0.0 if total_hits == 0 else known_hits / total_hits * 100
    over.sort(key=lambda x: (x[1], x[0]))

    lines = [
        "目标等级：HSK%d" % target,
        "词表命中总次数：%d；已学词命中次数：%d；生词覆盖率：%.1f%%"
        % (total_hits, known_hits, coverage),
    ]
    if total_hits == 0:
        lines.append("未命中课程生词表中的词条。")
    if over:
        lines.append("超纲词（%d 个）：" % len(over))
        for word, lvl, cnt in over:
            lines.append("- %s（HSK%d，%d 次）" % (word, lvl, cnt))
    else:
        lines.append("超纲词：无")
    lines.append("说明：按课程生词表逐词字符串匹配统计，允许词条重叠；词表外词语未计入。")
    return "\n".join(lines)


TOOLS = {
    "get_time": get_time,
    "calc": calc,
    "hsk_level": hsk_level,
    "evaluate_text_difficulty": evaluate_text_difficulty,
}

SYS = (
    "你是国际中文助教。可用工具只有这 4 个："
    "get_time（查当前时间，无参数）、"
    "calc（四则运算，如 calc('35*24')）、"
    "hsk_level（查生词 HSK 等级，如 hsk_level('把')）、"
    "evaluate_text_difficulty（评估课文对目标 HSK 等级的难度，"
    "参数为 [课文文本或文件路径, 目标等级]，"
    "如 evaluate_text_difficulty('北山愚公者，年且九十。', '4')）。"
    '如需调用，只输出一行 JSON，格式：{"tool": "工具名", "args": [参数]}；'
    "一次只调用一个工具，绝不编造不存在的工具名；无需工具时直接回答。"
)


def parse_calls(txt):
    """容错解析：剥掉 ```json 围栏与前后客套话，返回全部工具调用（0/1/多个）。

    模型不一定老实输出一个 JSON：可能带围栏、可能一段自然语言里夹着 JSON、
    也可能把多个工具调用并列输出成多行——这里全部兜住。"""
    s = (txt or "").strip()
    s = s.replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
        return [obj] if isinstance(obj, dict) else []
    except Exception:
        m = re.search(r"\{.*\}", s, re.S)  # re.S：跨行也能匹配到 JSON 块
        if m:
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict):
                    return [obj]
            except Exception:
                pass
        # 多个工具调用并列输出（小模型常态）：逐块全部解析，一轮依次执行
        calls = []
        for blk in re.findall(r"\{[^{}]*\}", s):
            try:
                obj = json.loads(blk)
            except Exception:
                continue
            if isinstance(obj, dict):
                calls.append(obj)
        return calls


def run(user_msg, max_calls=2):
    msgs = [{"role": "system", "content": SYS},
            {"role": "user", "content": user_msg}]
    for _ in range(max_calls):
        txt = get_client().chat.completions.create(
            model=MODEL, messages=msgs).choices[0].message.content
        calls = [c for c in parse_calls(txt)
                 if isinstance(c.get("tool"), str) and c.get("tool") in TOOLS]
        if not calls:
            return txt                                   # 没调用工具 → 直接回答
        # 一轮内依次执行模型请求的全部工具，结果合并回喂
        results = []
        for call in calls:
            args = call.get("args") or []
            if not isinstance(args, list):
                results.append("工具参数格式错误：%r" % (args,))
                continue
            try:
                results.append("%s%r → %s"
                               % (call["tool"], args,
                                  TOOLS[call["tool"]](*args)))
            except Exception as e:
                results.append("工具执行失败：%s" % e)
        msgs += [{"role": "assistant", "content": txt},
                 {"role": "user",
                  "content": "工具返回：%s。请据此作答。" % "；".join(results)}]
    # 达到上限后强制收口，避免无限循环烧 token
    return get_client().chat.completions.create(
        model=MODEL, messages=msgs).choices[0].message.content


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or (
        "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？"
    )
    print("用户输入：", q)
    print("助手：", run(q))