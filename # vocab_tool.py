# vocab_tool.py

def load_vocab(file_name="vocab.txt"):
    """从txt读取单词，返回字典{单词:例句} 文件读写"""
    vocab_dict = {}
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if "|" in line:
                    word, sentence = line.split("|")
                    vocab_dict[word.strip()] = sentence.strip()
    except FileNotFoundError:
        print("词汇文件不存在，新建空词库")
    return vocab_dict

def save_vocab(vocab_dict, file_name="vocab.txt"):
    """把字典保存回txt文件"""
    with open(file_name, "w", encoding="utf-8") as f:
        for word, sent in vocab_dict.items():
            f.write(f"{word}|{sent}\n")
    print("词汇保存成功")

def make_cloze(vocab_dict):
    """生成完形填空：把目标单词替换成____，返回填空题列表"""
    cloze_list = [] # 列表存储题目
    for target_word, sentence in vocab_dict.items():
        cloze_sent = sentence.replace(target_word, "____")
        cloze_list.append( {"question":cloze_sent, "answer":target_word} ) 
    return cloze_list

def show_cloze(cloze_list):
    """打印所有完形填空题目"""
    print("\n===== 完形填空练习题 =====")
    for idx, item in enumerate(cloze_list):
        print(f"{idx+1}. {item['question']}  答案：{item['answer']}")


if __name__ == "__main__":
   
    vocab = load_vocab()

  
    vocab["perspective"] = "We need a new perspective to solve this problem."
    vocab["analytical"] = "She has strong analytical thinking for reading."
    vocab["infer"] = "You can infer meaning from the context."
    vocab["context"] = "We should understand words within their context."

   
    save_vocab(vocab)

    
    cloze_exercises = make_cloze(vocab)
    show_cloze(cloze_exercises)