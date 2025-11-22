# agents/summarizer_agent.py
from agents.agent_base import ADKAgent

# Agent that summarizes each chunk of cleaned transcript tex
chunk_summarizer = ADKAgent(
    role="Chunk Summarizer",
    goal="Summarize transcript chunks into short structured notes.",
    backstory="Efficient concise summaries capturing key ideas.",
    model="gemini-2.0-flash-lite",
    temperature=0.3
)

# Agent that merges all chunk summaries into a final lecture-style document
final_summarizer = ADKAgent(
    role="Final Summarizer",
    goal="Combine all chunk summaries into lecture-style notes in Markdown.",
    backstory="Professor-level writer for high-quality study notes.",
    model="gemini-2.5-flash-lite",
    temperature=0.35    # Slightly higher creativity
)

def summarize_chunk(text: str):
    # Summarize a single cleaned transcript chunk into short bullet points.
    prompt = (
        "Summarize this cleaned transcript batch into short bullet-point structured notes. "
        "Focus on clarity, topic flow, and main ideas. Return only bullet points.\n\n" + text
    )
    return chunk_summarizer.run(prompt, max_tokens=1024)

def summarize_final(all_chunk_summaries: str):
    # Combine all chunk-level summaries into a complete lecture-style Markdown summary.
    prompt = (
        "Combine these batch-level summaries into well-structured lecture-style notes.\n"
        "STRICT FORMAT:\n- Use Markdown headings (#, ##, ###)\n- Use bullet points\n- Include key takeaways and a one-line summary\n\n"
        + all_chunk_summaries
    )
    return final_summarizer.run(prompt, max_tokens=4096)
