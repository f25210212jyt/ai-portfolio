import json
import time
import csv
from datetime import datetime

# ========== 三个工具 ==========
def get_current_time() -> str:
    """工具1：获取当前时间"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def safe_calc(expr: str) -> str:
    """工具2：安全四则运算，只允许数字和+-*/()"""
    allowed_chars = "0123456789+-*/(). "
    for c in expr:
        if c not in allowed_chars:
            return "表达式包含非法字符，拒绝计算"
    try:
        res = eval(expr)
        return f"计算结果 = {res}"
    except Exception as e:
        return f"计算失败：{str(e)}"

def get_hsk_level(word: str, csv_path="hsk_words.csv") -> str:
    """工具3：读取csv生词表，查询HSK等级"""
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["word"] == word.strip():
                    return f"单词「{word}」属于 HSK{row['level']}"
        return f"未在词库找到单词「{word}」"
    except Exception as e:
        return f"词库读取异常: {e}"

# ========== 模拟模型：输出function call的意图与参数 ==========
def llm_decide(query: str):
    """模拟大模型，输出json，只决定调用哪个工具，不直接执行"""
    if "时间" in query:
        return {
            "tool": "get_current_time",
            "params": {}
        }
    elif any(op in query for op in ["+", "-", "*", "/"]):
        expr = query.replace("等于多少","").replace("计算","").strip()
        return {
            "tool": "safe_calc",
            "params": {"expr": expr}
        }
    elif "HSK" in query or "单词" in query:
        #提取单词
        w = query.replace("HSK等级","").replace("单词","").replace("的","").strip()
        return {
            "tool": "get_hsk_level",
            "params": {"word": w}
        }
    else:
        return {"tool": None, "params": {}, "reply":"我无法处理这个问题"}

# ========== Agent主循环：执行工具，把结果返回，生成最终回答 ==========
def agent_run(user_query: str):
    print(f"\n【用户问句】{user_query}")
    #1.模型决策，输出意图+参数
    func_call = llm_decide(user_query)
    print(f"【模型输出JSON】{json.dumps(func_call, ensure_ascii=False)}")
    tool_name = func_call["tool"]
    params = func_call["params"]
    #2.执行工具
    if tool_name == "get_current_time":
        tool_ret = get_current_time()
    elif tool_name == "safe_calc":
        tool_ret = safe_calc(params["expr"])
    elif tool_name == "get_hsk_level":
        tool_ret = get_hsk_level(params["word"])
    else:
        tool_ret = func_call.get("reply","")
    print(f"【工具返回值】{tool_ret}")
    #3.生成最终回答
    final_ans = f"根据工具查询结果：{tool_ret}"
    print(f"【最终回答】{final_ans}")
    return {
        "query": user_query,
        "model_json": func_call,
        "tool_return": tool_ret,
        "final_answer": final_ans
    }

if __name__ == "__main__":
    # 3个样例，生成轨迹记录
    trace1 = agent_run("现在几点了？")
    trace2 = agent_run("计算 12 + 34 * 2")
    trace3 = agent_run("单词 爱 的HSK等级")