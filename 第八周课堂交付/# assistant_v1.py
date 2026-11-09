# assistant_v1.py
class FakeRAG:
    def search(self, question):
        return "【知识库检索结果】国际中文教育面向外国学习者，教授汉语和中华文化。"

rag = FakeRAG()

class FakeAPI:
    def chat(self, prompt):
        return "【API回答】国际中文教育，是对母语非汉语的人开展汉语教学。"

class LocalEngine:
    def chat(self, prompt):
        return "【本地引擎回答】国际中文教育，教授外国人汉语，传播中国文化。"

api = FakeAPI()
local = LocalEngine()

def answer(prompt, prefer="local", use_rag=False):
    # use_rag开关
    if use_rag:
        context = rag.search(prompt)
        prompt = f"参考资料：{context}\n问题：{prompt}"

    if prefer == "api":
        try:
            return api.chat(prompt)
        except Exception as err:
            print(f"【回退日志】API失败，错误信息：{err}，自动切换 LocalEngine")
            return local.chat(prompt)
    elif prefer == "local":
        return local.chat(prompt)
    else:
        raise ValueError("prefer 参数只能是 local / api")


if __name__ == "__main__":
    # 三问三答测试
    q1 = "什么是国际中文教育？"
    q2 = "国际中文教育的目标是什么？"
    q3 = "国际中文教育有什么难点？"

    print("=====第1问 prefer=local use_rag=False=====")
    print(answer(q1, prefer="local", use_rag=False))
    print("\n=====第2问 prefer=api use_rag=True=====")
    print(answer(q2, prefer="api", use_rag=True))
    print("\n=====第3问 prefer=api use_rag=False=====")
    print(answer(q3, prefer="api", use_rag=False))