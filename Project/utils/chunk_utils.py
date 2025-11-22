import re


def chunk_text(text: str, max_chars: int = 3000):
    """
    Splits a long transcript into moderately large chunks for faster
    summarization while respecting sentence boundaries.

    Args:
        text (str): Full transcript string.
        max_chars (int): Max characters per chunk (~3000 for ~750 tokens).

    Returns:
        list[str]: List of text chunks.
    """
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    while len(text) > max_chars:
        # Try splitting on a sentence-ending punctuation before max_chars
        split_index = max(
            text.rfind(".", 0, max_chars),
            text.rfind("?", 0, max_chars),
            text.rfind("!", 0, max_chars),
        )
        # If no good punctuation found → hard split at max_chars
        if split_index == -1 or split_index < max_chars * 0.6:
            split_index = max_chars
            
        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()

    if text:
        chunks.append(text)

    # Merge small tail chunks (<400 chars)
    merged = []
    for c in chunks:
        if merged and len(c) < 400:
            merged[-1] += " " + c
        else:
            merged.append(c)

    return merged


def group_chunks(chunks, batch_size=10):
    """
    Groups chunks hierarchically to reduce LLM calls.
    E.g., 10 chunks → 1 batch summary.
    """
    return [
        " ".join(chunks[i : i + batch_size])
        for i in range(0, len(chunks), batch_size)
    ]


def preview_chunks(chunks, limit=2):
    """Quick preview for debugging chunking behavior."""
    print(f"\n🧩 Created {len(chunks)} chunks. Showing first {limit}:\n")
    for i, c in enumerate(chunks[:limit], 1):
        print(f"--- Chunk {i} ---\n{c[:300]}...\n")
