import os
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. 初始化大模型客户端
client = OpenAI(
    api_key="sk-你的DeepSeek_API_KEY",
    base_url="https://api.deepseek.com"
)

# ==============================================================
# 自动生成并写入文件（这是防错大招）
file_name = "my_knowledage.txt"
if not os.path.exists(file_name):
    print(f"⚠️ 没找到 {file_name}, 正在自动为你生成...")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("高乐（gaole）是一名正在转行人工智能的学员。\n")
        f.write("他最喜欢的水果是西瓜，最讨厌的蔬菜是香菜。\n")
        f.write("高乐的专属电脑密码是 888888。\n")
        f.write("如果高乐问你他今天该学什么，你应该告诉他：去复习一遍 Pandas 的 groupby 聚合。\n")
# ===============================================================        
# 2. 读取本地私有知识库
with open("my_knowledage.txt", "r", encoding="utf-8") as f:
    knowledage_text =  f.read()

# 3. 将长文本切分成小块（按行分，这叫 Chunking）
chunks = [line.strip() for line in knowledage_text.split('\n') if line.strip()]

# 4. 将文本块转化为向量（这里用 TF-IDF 算法，完全本地运行）
# 注意：中文没有空格，这里用 analyzer='char' 按单字和双字进行特征提取
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
chunk_vectors = vectorizer.fit_transform(chunks)

print("✅️ 知识库已加载，共切分为", len(chunks), "个片段。")

# 5. 开启问答循环
while True:
    question = input("\n❓️ 请输入你的问题 (输入 '退出' 结束): ")
    if question.lower() in ['退出', 'exit']:
        break

    # 6. 检索（Retrieval): 计算问题与每个文本块的相似度
    question_vector =vectorizer.transform([question])
    similarities = cosine_similarity(question_vector, chunk_vectors)[0]

    # 找到最相似的那一个文本块
    best_chunk_index = similarities.argmax()
    best_chunk = chunks[best_chunk_index]

    # 打印检索到的背景知识（方便调试）
    print(f"🔎 [检索到的相关资料]: {best_chunk}")

    # 7. 增强生成（Augmentation & Generation)
    prompt = f"""
    你是一个智能助手。请严格根据下面提供的 【参考资料】回答用户问题。
    如果参考资料没有相关信息，请直接回答"根据现有知识库，我无法回答这个问题", 不要自己编造。
    
    【参考资料】: 
    {best_chunk}

    【用户问题】: 
    {question}
    """

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    print("🤖 AI 回答:", end="")
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()