import streamlit as st
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. 页面设置
st.set_page_config(page_title="AI 文档阅读器", page_icon="📄", layout="centered")
st.title("📄 AI 个人专属文档阅读器")
st.caption("上传 TXT 文件，让 AI 帮你提炼信息")

# 2. 初始化大模型客户端
client = OpenAI(
    api_key="sk-3b5fb4ee01e542f8ba5cb73fe47e87d9",  # 👈 替换成你的 Key
    base_url="https://api.deepseek.com"
)

# 3. 侧边栏：上传文件
with st.sidebar:
    st.header("上传你的文档")
    uploaded_file = st.file_uploader("选择一个 TXT 文件", type=["txt"])
    st.info("💡 提示：你可以随便找一个小说或笔记的 txt 文件测试。")

# 4. 核心逻辑
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    chunks = [line.strip() for line in text.split('\n') if line.strip()]
    
    if len(chunks) == 0:
        st.warning("文件是空的，请换一个文件。")
    else:
        @st.cache_resource
        def build_vectorizer(chunks):
            vec = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
            vectors = vec.fit_transform(chunks)
            return vec, vectors
            
        vectorizer, chunk_vectors = build_vectorizer(chunks)
        st.success(f"✅ 文档已成功加载！共切分为 {len(chunks)} 个片段。")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 接收输入
        user_input = st.chat_input("针对这篇文档提问...")
        
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 计算相似度
            question_vector = vectorizer.transform([user_input])
            similarities = cosine_similarity(question_vector, chunk_vectors)[0]
            best_chunk = chunks[similarities.argmax()]
            
            prompt = f"""
            你是一个文档阅读助手。请严格根据下面提供的【文档片段】回答用户的问题。
            如果片段中没有相关信息，请直接回答“文档中未提及”，不要自己编造。
            
            【文档片段】：
            {best_chunk}
            
            【用户问题】：
            {user_input}
            """
            
            with st.chat_message("assistant"):
                try:
                    response = client.chat.completions.create(
                        model="deepseek-flash",
                        messages=[{"role": "user", "content": prompt}],
                        stream=True
                    )
                    
                    def generate_chunks():
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content
                    
                    ai_reply = st.write_stream(generate_chunks())
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    
                except Exception as e:
                    st.error(f"出错了: {e}")