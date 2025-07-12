def get_summary_prompt(section_text, context, target_words):
    section_title = section_text.get("title", "Section")
    main_text = section_text.get("content", "")[:10000]  # Limit to 10k chars
    return f"""You are summarizing a section of 'Nexus: A Brief History of Information Networks from the Stone Age to AI' by Yuval Noah Harari. Your summary must:
- Be clear, concise, and professional, preserving key arguments, facts, and tone.
- Avoid repetition of ideas from other sections.
- Target ~{target_words} words for a 100-page summary (25,000 words total).
- Use provided context to ensure coherence.
- Structure the summary with an introduction, key points, and conclusion.

Section Title: {section_title}
Section Text: {main_text}
Relevant Context: {context[:5000]}  # Limit context size

Provide the summary in a narrative format, readable as part of a cohesive book summary.
"""