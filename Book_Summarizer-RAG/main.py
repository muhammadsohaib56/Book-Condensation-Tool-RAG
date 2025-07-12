from pdf_utils import load_book, split_into_sections
from prompts import get_summary_prompt
from model import summarize_with_groq
from rag import build_vector_store, retrieve_relevant_chunks
from tqdm import tqdm
from fpdf import FPDF
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def estimate_word_count(text):
    """Estimate word count of a text string."""
    return len(text.split())

def clean_text_for_pdf(text):
    """Clean text to remove non-Latin-1 characters for FPDF compatibility."""
    text = text.replace('\u2013', '-')  # En dash to hyphen
    text = text.replace('\u2014', '--')  # Em dash to double hyphen
    text = text.replace('\u2018', "'").replace('\u2019', "'")  # Smart quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    return ''.join(c if ord(c) < 256 else ' ' for c in text)

def main():
    # Paths
    input_pdf_path = os.path.join("data", "Nexus A Brief History of Information Networks from the Stone Age to AI (Yuval Noah Harari) (Z-Library).pdf")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Target 100 pages (~25,000 words, assuming 250 words/page)
    target_total_words = 25000
    logger.info("📖 Loading book...")
    book_pages = load_book(input_pdf_path)

    logger.info("📚 Splitting into sections...")
    sections = split_into_sections(book_pages)

    # Build vector DB (RAG)
    logger.info("🧠 Building vector store for RAG...")
    index, embeddings, section_list = build_vector_store(sections)

    logger.info(f"📝 Total sections to summarize: {len(sections)}")
    summary_sections = []
    total_words = 0

    # Estimate target words per section
    section_word_targets = [target_total_words // len(sections)] * len(sections) if sections else [target_total_words]
    remaining_words = target_total_words % len(sections) if sections else 0
    for i in range(remaining_words):
        section_word_targets[i] += 1

    for i, (section, target_words) in enumerate(tqdm(zip(sections, section_word_targets), total=len(sections), desc="🔍 Summarizing Sections")):
        try:
            # Retrieve relevant context using RAG
            context = "\n\n".join(retrieve_relevant_chunks(index, embeddings, section_list, section, top_k=2))
            prompt = get_summary_prompt(section, context, target_words)

            # Generate summary
            summary = summarize_with_groq(prompt)
            summary_words = estimate_word_count(summary)
            logger.info(f"Section {i+1} summary: {summary_words} words")

            # Append summary with section metadata
            section_title = section.get("title", f"Section {i+1}")
            summary_text = f"# {section_title}\n{summary}\n\n"
            summary_sections.append(summary_text)
            total_words += summary_words

        except Exception as e:
            logger.error(f"⚠️ Error in section {i+1}: {e}")
            summary_sections.append(f"# Section {i+1}\n[Error in summarizing this section: {str(e)}]\n\n")

    logger.info(f"📊 Total words in summary: {total_words}")

    # Save to .txt
    output_txt_path = os.path.join(output_dir, "final_summary.txt")
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_sections))
    logger.info(f"✅ Text summary saved to {output_txt_path}")

    # Save to PDF
    output_pdf_path = os.path.join(output_dir, "final_summary.pdf")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Nexus: A Brief History of Information Networks - Summary", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)

    for summary in summary_sections:
        lines = summary.split("\n")
        if lines[0].startswith("# "):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, clean_text_for_pdf(lines[0][2:]), ln=True)
            pdf.set_font("Arial", size=12)
            for line in lines[1:]:
                if line.strip():
                    pdf.multi_cell(0, 10, clean_text_for_pdf(line.strip()), align="L")
            pdf.ln(5)
        else:
            for line in lines:
                if line.strip():
                    pdf.multi_cell(0, 10, clean_text_for_pdf(line.strip()), align="L")
            pdf.ln(5)

    pdf.output(output_pdf_path)
    logger.info(f"✅ PDF summary saved to {output_pdf_path}")

if __name__ == "__main__":
    main()