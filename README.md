

## 📘 `README.md` – Full Professional Documentation

```markdown
# 📚 RAG-Based Book Summarizer using Groq + LLaMA 4

This project is a **Retrieval-Augmented Generation (RAG)** based pipeline for summarizing large-scale documents (like 600-page books) into ~100-page, structured summaries. It leverages **Groq’s high-speed LLaMA 4 model**, **FAISS vector store**, and **SentenceTransformer embeddings** to enhance summarization accuracy by grounding responses in source material.

---

## 🚀 Features

- ✅ Summarizes lengthy books into condensed structured summaries
- 🧠 Uses **RAG** to fetch and inject context into the LLM
- ⚡ Powered by **Groq** with `meta-llama/llama-4-scout-17b-16e-instruct`
- 📄 PDF parsing and chunking support
- 🔍 FAISS + SentenceTransformer for fast vector search

---

## 📦 Tech Stack

- `Groq API` (for summarization)
- `SentenceTransformers` for embeddings
- `FAISS` (vector store)
- `fpdf` (PDF output of summary)
- `PyMuPDF` / `pdfplumber` for PDF parsing
- `dotenv` for secure key loading

---

```
## 📁 Folder Structure
```markdown
BOOK\_SUMMARIZER-RAG/
├── **pycache**/                  # Compiled cache
├── data/                         # Input PDFs
├── output/                       # Final summaries
├── .env                          # API key file (add your GROQ key here)
├── main.py                       # Pipeline controller
├── model.py                      # Summarization logic with Groq
├── pdf_utils.py                  # PDF loader & chunker
├── prompts.py                    # Prompt templates for RAG
├── rag.py                        # RAG flow with FAISS + retriever
├── requirements.txt              # Python dependencies

```

---

## 🔐 Environment Setup

Create a `.env` file:
```

GROQ\_API\_KEY=your\_groq\_api\_key\_here

````

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/rag-book-summarizer.git
cd rag-book-summarizer
pip install -r requirements.txt
````

---

## 🧠 How It Works

1. **PDF is loaded** and split into manageable chunks
2. **Embeddings** are generated using `all-MiniLM-L6-v2`
3. Chunks are stored and indexed in **FAISS vector DB**
4. For each summary prompt:

   * Relevant chunks are retrieved
   * Prompt + context are sent to **Groq** API
5. Summaries are written to a 100-page PDF

---

## 📌 Usage

```bash
python main.py
```

Check your output in the `output/` folder.

---

## 📈 Model & API Details

* Model: `meta-llama/llama-4-scout-17b-16e-instruct` via Groq
* Free Tier Limits:

  * 🧠 30K Tokens / Min
  * 🔁 30 Requests / Min
  * 📅 500K Tokens / Day

---

## 📋 Example Output

* Summary PDF with structured chapters
* 100 pages of condensed content from \~500+ pages source
* Retains original meaning, key events, and flow

---

## 📜 License

[MIT License](LICENSE)

---



