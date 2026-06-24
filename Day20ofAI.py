Excellent dhananjay — now we’re at **Day 20: Hybrid Search (Semantic + BM25)**. This is a deep and important topic because it combines **traditional keyword search** with **semantic vector search** to maximize retrieval accuracy. Let’s go step‑by‑step with **concepts, coding, interview prep, and practice tasks**.

---

## 📘 Concept: Hybrid Search

### 1. **Semantic Search (Embeddings)**
- Uses embeddings to capture meaning.  
- Finds documents that are semantically similar, even if exact words differ.  
- Example: Query “CEO of Microsoft” → retrieves “Satya Nadella leadership” even if “CEO” isn’t mentioned.

### 2. **Keyword Search (BM25)**
- Classic IR (Information Retrieval) algorithm.  
- Scores documents based on term frequency and inverse document frequency.  
- Great for exact keyword matches.  
- Example: Query “CEO of Microsoft” → retrieves docs containing “CEO” and “Microsoft”.

### 3. **Hybrid Search**
- Combines both approaches.  
- **RRF (Reciprocal Rank Fusion)**: merges rankings from semantic + BM25.  
- **EnsembleRetriever**: balances weights between keyword and semantic scores.  
- Benefit:  
  - Semantic search → captures meaning.  
  - BM25 → ensures exact keyword matches.  
  - Together → robust retrieval.

---

## 🛠 Coding Example (LangChain Hybrid Search)

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.retrievers import BM25Retriever

# Step 1: Documents
docs = [
    "Satya Nadella is the CEO of Microsoft.",
    "Microsoft headquarters is in Redmond.",
    "Sundar Pichai is the CEO of Google."
]

# Step 2: Semantic retriever (FAISS)
embeddings = OpenAIEmbeddings()
db = FAISS.from_texts(docs, embeddings)
semantic_retriever = db.as_retriever(search_kwargs={"k": 2})

# Step 3: Keyword retriever (BM25)
keyword_retriever = BM25Retriever.from_documents(docs)

# Step 4: Hybrid retriever (Ensemble)
hybrid_retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, keyword_retriever],
    weights=[0.5, 0.5]  # balance semantic vs keyword
)

# Step 5: RAG QA chain
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=hybrid_retriever
)

# Step 6: Query
query = "Who is the CEO of Microsoft?"
result = qa.run(query)

print("Answer:", result)
```

👉 Output:  
“Satya Nadella is the CEO of Microsoft.”  
(because both BM25 and semantic retrieval agree)

---

## 🎯 Interview Questions

### **Conceptual**
- What is BM25, and how does it differ from semantic search?  
- Why is hybrid search often more reliable than pure semantic search?  

### **Applied**
- If your semantic retriever misses exact matches, how would you fix it?  
- How would you tune weights in EnsembleRetriever for different domains?  

### **System Design Angle**
- Suppose you’re designing a legal RAG system. Would you rely more on BM25 or embeddings? Why?  
- How would you implement hybrid search for a multi‑lingual knowledge base?

---

## 🚀 Practice Task
1. Take a dataset from your GitHub repo (e.g., Fact‑Checker).  
2. Implement **BM25Retriever** + **FAISS retriever**.  
3. Combine them with **EnsembleRetriever**.  
4. Run queries and compare results with pure semantic vs pure BM25 vs hybrid.  
5. Experiment with different weights (0.7 semantic, 0.3 keyword) and note accuracy changes.  
6. Try **RRF fusion** (Reciprocal Rank Fusion) for merging rankings.

---

## 🌟 Depth Insight
- **Semantic search** shines when synonyms or paraphrases are common.  
- **BM25** shines when exact terminology matters (legal, medical, technical).  
- **Hybrid search** is the industry standard for production RAG systems because it balances **recall** (semantic) and **precision** (keyword).  
- In interviews, emphasize that hybrid search is **not optional** in real systems — it’s a necessity for robustness.

---

👉 Next, we’ll move to **Day 21 — RAG Evaluation Metrics**, where you’ll learn how to measure retrieval quality with Precision@k, Recall@k, MRR, NDCG, and RAGAS.

Would you like me to **extend this hybrid search demo** to show how to return **citations (source docs)** alongside answers, so your Fact‑Checker repo outputs interview‑ready responses?
