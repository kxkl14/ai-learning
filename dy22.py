import os
import chromadb
from openai import OpenAI

# 1. 初始化大模型 (生成用)
client = OpenAI(
    api_key="sk-78d74451fb154af792833e99cfae0288",  # 👈 替换成你的 Key
    base_url="https://api.deepseek.com"
)

# 2. 准备数据 (自动生成测试文档)
file_name = "my_knowledge.txt"
if not os.path.exists(file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("高乐是一名正在转行人工智能的学员。\n")
        f.write("他最喜欢的水果是西瓜，最讨厌的蔬菜是香菜。\n")
        f.write("高乐的专属电脑密码是 888888。\n")

with open(file_name, "r", encoding="utf-8") as f:
    text = f.read()
chunks = [line.strip() for line in text.split('\n') if line.strip()]

# 3. 初始化 ChromaDB 向量数据库
print("⏳ 正在初始化向量数据库（首次运行需下载模型，请稍候）...")
# 创建一个内存中的数据库（每次运行都会重置）
chroma_client = chromadb.Client()
# 创建一个集合（相当于数据库里的一张表）
collection = chroma_client.create_collection(name="my_knowledge_base")

# 4. 把文本块存入向量数据库
# ChromaDB 会自动调用内置的模型，把文字转成向量并存储
collection.add(
    documents=chunks,
    ids=[str(i) for i in range(len(chunks))] # 给每个片段一个唯一的ID
)
print(f"✅ 知识库已存入向量数据库！共 {len(chunks)} 个片段。")

# 5. 开启问答循环
while True:
    question = input("\n❓ 请输入你的问题 (输入 '退出' 结束): ")
    if question.lower() in ['退出', 'exit']:
        break
    
    # 6. 语义检索 (Retrieval)
    # 我们只问一句，返回最相似的一个结果
    results = collection.query(
        query_texts=[question],
        n_results=1
    )
    
    # 从结果中提取最相关的文档片段
    if results['documents'] and results['documents'][0]:
        best_chunk = results['documents'][0][0]
    else:
        best_chunk = "没有找到相关资料。"
        
    print(f"🔍 [语义检索到的资料]: {best_chunk}")
    
    # 7. 发给大模型生成回答
    prompt = f"""
    你是一个文档阅读助手。请严格根据下面提供的【文档片段】回答用户的问题。
    如果片段中没有相关信息，请直接回答“文档中未提及”，不要自己编造。
    
    【文档片段】：
    {best_chunk}
    
    【用户问题】：
    {question}
    """
    
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    print("🤖 AI 回答: ", end="")
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()