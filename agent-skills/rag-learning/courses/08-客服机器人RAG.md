# 08-客服机器人RAG

## 课程目标

- 理解客服机器人场景特点
- 掌握多轮对话处理方法
- 学会构建客服 RAG 系统

---

## 1. 场景特点

| 特点 | 说明 |
|------|------|
| 多轮对话 | 需要记住上下文 |
| 意图识别 | 理解用户目的 |
| 快速响应 | 客服场景延迟要求高 |
| 标准化回答 | 一致的服务质量 |

---

## 2. 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                  客服机器人 RAG 架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │  用户输入 │───▶│ 意图识别 │───▶│  知识检索 │            │
│   └──────────┘    └──────────┘    └──────────┘            │
│                          │                    │              │
│                          ▼                    ▼              │
│                    ┌──────────┐         ┌──────────┐        │
│                    │  话术维持 │         │  生成回答 │        │
│                    └──────────┘         └──────────┘        │
│                                                    │          │
│                                                    ▼          │
│                                              ┌──────────┐    │
│                                              │  多轮记忆 │    │
│                                              └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 多轮对话实现

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# 带记忆的对话链
from langchain.chains import ConversationalRetrievalChain

qa = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    memory=memory,
    condense_question_prompt=condense_prompt
)

# 对话
result = qa({"question": "你们的退货政策是什么？"})
```

---

## 4. 对话 Prompt 模板

```python
condense_prompt = PromptTemplate(
    template="""根据对话历史，改写用户问题使其独立完整。

对话历史：
{chat_history}

用户新问题：{question}

独立完整的问题：""",
    input_variables=["chat_history", "question"]
)

qa_prompt = PromptTemplate(
    template=""""你是一个专业的客服助手。根据知识库中的信息，回答用户问题。

知识库信息：
{context}

对话历史：
{chat_history}

当前问题：{question}

要求：
1. 回答专业、友好
2. 如信息不足，说明情况
3. 如需进一步帮助，提示用户

回答：""",
    input_variables=["context", "chat_history", "question"]
)
```

---

## 5. 意图识别路由

```python
from enum import Enum

class Intent(Enum):
    PRODUCT_INFO = "product_info"
    ORDER_STATUS = "order_status"
    RETURN_policy = "return_policy"
    TECHNICAL_SUPPORT = "technical_support"
    HUMAN_AGENT = "human_agent"

INTENT_KEYWORDS = {
    Intent.PRODUCT_INFO: ["产品", "功能", "规格", "介绍"],
    Intent.ORDER_STATUS: ["订单", "物流", "发货", "到了吗"],
    Intent.RETURN_POLICY: ["退货", "退款", "换货", "售后"],
    Intent.TECHNICAL_SUPPORT: ["问题", "故障", "报错", "解决"],
    Intent.HUMAN_AGENT: ["人工", "客服", "真人", "转人工"],
}

def classify_intent(query: str) -> Intent:
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        scores[intent] = sum(1 for kw in keywords if kw in query)
    return max(scores, key=scores.get)
```

---

## 6. 会话管理

```python
class SessionManager:
    """会话状态管理"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> state
    
    def get_state(self, session_id: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "turn_count": 0,
                "last_intent": None,
                "topic": None,
                "context": []
            }
        return self.sessions[session_id]
    
    def update_state(self, session_id: str, updates: dict):
        self.sessions[session_id].update(updates)
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
```

---

## 7. 完整示例

```python
class CustomerServiceRAG:
    """客服机器人"""
    
    def __init__(self):
        self.vectorstore = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.session_manager = SessionManager()
    
    def initialize(self, documents: list[Document]):
        # 加载文档
        chunks = self.chunk_documents(documents)
        # 向量化
        self.vectorstore = Chroma.from_documents(
            chunks, 
            OpenAIEmbeddings()
        )
    
    def chat(self, session_id: str, query: str) -> dict:
        # 获取会话状态
        state = self.session_manager.get_state(session_id)
        state["turn_count"] += 1
        
        # 意图识别
        intent = classify_intent(query)
        state["last_intent"] = intent
        
        # 根据意图选择策略
        if intent == Intent.HUMAN_AGENT:
            return {"answer": "正在为您转接人工客服...", "type": "transfer"}
        
        # RAG 查询
        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3),
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory
        )
        
        result = chain({"question": query})
        
        return {
            "answer": result["answer"],
            "intent": intent.value,
            "turn": state["turn_count"]
        }
```

---

## 8. 总结

- 多轮对话需要记忆组件
- 意图识别提升准确率
- 会话状态管理很重要
- 必要时转人工服务