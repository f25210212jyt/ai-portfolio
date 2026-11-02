# 导入本地知识库处理与大语言模型调用的相关依赖
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# 步骤一：准备文本并切分
def prepare_text():
    loader = TextLoader("data.txt", encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    splits = text_splitter.split_documents(docs)
    return splits

# 步骤二：加载向量化模型并建立本地知识库
def build_retriever():
    splits = prepare_text()
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore.as_retriever()

# 步骤三与四：检索与生成，并实现“让答案附出处”的进阶要求
def rag_qa(question, prefer="local"):
    retriever = build_retriever()
    
    if prefer == "local":
        llm = Ollama(model="qwen2") # 本地小模型
    else:
        # 此处假设调用云端大模型，实际需配置
        pass 

    # 设定提示词，强制模型在回答时标注引用来源
    prompt_template = """请严格基于以下已知信息回答问题。
如果无法得到答案，请直接说“根据已知信息无法回答该问题”。
回答时，必须通过【出处：具体片段内容】的格式标注答案来源。
已知信息：
{context}
问题：{question}
答案："""
    
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    result = qa_chain({"query": question})
    
    # 提取检索到的文档片段作为出处
    source_docs = result["source_documents"]
    citation = "\n\n--- 参考出处 ---\n"
    for i, doc in enumerate(source_docs):
        citation += f"片段{i+1}: {doc.page_content.strip()}\n"
        
    return result["result"] + citation

# 本地测试运行
if __name__ == "__main__":
    print(rag_qa("中级工程师的补贴是多少？"))