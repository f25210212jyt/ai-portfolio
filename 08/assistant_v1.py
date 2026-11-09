import os, sys
# 让跨周import生效
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath
weekpath.load_env()

from llm import LLM          # W6双引擎
from rag_qa import retrieve, build_prompt  # W7知识库

llm = LLM()
SYSTEM_HINT = "你是国际中文教学助手，面向HSK3-4学习者，回答需给出依据。"

def answer(question, use_rag=True, prefer="local"):
    if use_rag:
        ctx = retrieve(question)
        prompt = SYSTEM_HINT + "\n" + build_prompt(question, ctx)
    else:
        prompt = SYSTEM_HINT + "\n" + question
    return llm.ask(prompt, prefer=prefer)

if __name__ == "__main__":
    # 讲义要求的三问三答测试
    questions = [
        "把字句的教学难点有哪些", 
        "HSK4词汇量要求是多少",
        "《愚公移山》可以设计什么课堂活动"
    ]
    
    print("=== 纯对话模式 (use_rag=False) ===")
    for q in questions:
        print(f"Q: {q}")
        try:
            # 使用本地模型，如果没有可改成 prefer="api"
            print(f"A: {answer(q, use_rag=False, prefer='local')}")
        except Exception as e:
            print(f"A: [运行失败] {e}")
        print("-" * 40)
        
    print("\n=== 基于资料模式 (use_rag=True) ===")
    for q in questions:
        print(f"Q: {q}")
        try:
            print(f"A: {answer(q, use_rag=True, prefer='local')}")
        except Exception as e:
            print(f"A: [运行失败] {e}")
        print("-" * 40)