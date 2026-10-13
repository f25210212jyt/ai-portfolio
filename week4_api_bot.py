import os
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

from openai import OpenAI

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 多轮对话历史，用来保存全部上下文
messages_history = []

def chat_with_bot(user_input:str):
    # 将用户新提问追加到历史
    messages_history.append({"role":"user", "content":user_input})
    response = client.chat.completions.create(
        model=model_name,
        messages = messages_history,
        temperature = 0.7,
        max_tokens = 1024,
        timeout = 30
    )
    bot_reply = response.choices[0].message.content
    # 将AI回复也存入历史，供下一轮对话读取
    messages_history.append({"role":"assistant", "content":bot_reply})
    return bot_reply

if __name__ == "__main__":
    print("====支持多轮追问学科AI助教机器人启动=====")
    while True:
        user_q = input("你（输入exit退出）：")
        if user_q.lower() == "exit":
            print("对话结束")
            break
        ans = chat_with_bot(user_q)
        print(f"AI助教：{ans}")
        # 写入聊天日志 chat_log.txt
        with open("chat_log.txt","a",encoding="utf-8") as f:
            f.write(f"用户：{user_q}\nAI：{ans}\n--------------------------\n")