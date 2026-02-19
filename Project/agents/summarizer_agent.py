# agents/summarizer_agent.py
from agents.agent_base import ADKAgent

# Agent that summarizes each chunk of cleaned transcript tex
chunk_summarizer = ADKAgent(
    role="Chunk Summarizer",
    goal="Summarize transcript chunks into short structured notes.",
    backstory="Efficient concise summaries capturing key ideas.",
    # model="qwen2.5:7b",
    temperature=0.3
)

# Agent that merges all chunk summaries into a final lecture-style document
final_summarizer = ADKAgent(
    role="Final Summarizer",
    goal="Combine all chunk summaries into lecture-style notes in Markdown.",
    backstory="Professor-level writer for high-quality study notes.",
    # model="qwen2.5:7b",
    temperature=0.35    # Slightly higher creativity
)

def summarize_chunk(text: str):
    # Summarize a single cleaned transcript chunk into short bullet points.
    prompt = (
        "You are an expert technical writer creating high-density study notes. "
        "Your goal is to capture EVERY technical detail, definition, and concept from the following text. "
        "Do NOT use filler words or conversational language. be extremely CONCISE but COMPREHENSIVE. "
        "Format as dense bullet points.\n\n" + text
    )
    return chunk_summarizer.run(prompt, max_tokens=1500)

def summarize_final(all_chunk_summaries: str):
    # Combine all chunk-level summaries into a complete lecture-style Markdown summary.
    prompt = (
        "You are compiling a comprehensive study guide from the following notes. "
        "Your task is to merge them into a single, cohesive, and detailed document. "
        "RETAIN ALL DETAILS but remove redundancy. Use high information density. "
        "STRICT FORMAT:\n- Use Markdown headings (#, ##, ###)\n- Use detailed bullet points\n- Include a 'Key Terminology' section if applicable.\n\n"
        + all_chunk_summaries
    )
    return final_summarizer.run(prompt, max_tokens=4096)
