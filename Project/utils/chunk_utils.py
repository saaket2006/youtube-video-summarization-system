import re


def chunk_text(text: str, max_chars: int = 500):
    """
    Splits a transcript text into smaller chunks without cutting sentences mid-way.

    Args:
        text (str): Full transcript string.
        max_chars (int): Maximum characters per chunk (default = 500).

    Returns:
        list[str]: Clean list of text chunks ready for summarization.
    """

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    chunks = []
    while len(text) > max_chars:
        # Try to split on sentence boundary before max_chars
        split_index = max(
            text.rfind('.', 0, max_chars),
            text.rfind('?', 0, max_chars),
            text.rfind('!', 0, max_chars)
        )

        # If no sentence end found, hard split
        if split_index == -1 or split_index < max_chars * 0.6:
            split_index = max_chars

        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()

    # Add the last chunk
    if text:
        chunks.append(text)

    # Merge leftover small chunks (<150 chars) with previous one
    merged_chunks = []
    for chunk in chunks:
        if merged_chunks and len(chunk) < 150:
            merged_chunks[-1] += ' ' + chunk
        else:
            merged_chunks.append(chunk)

    return merged_chunks


def preview_chunks(chunks, limit=2):
    """
    Quick preview for debugging chunking behavior.
    """
    print(f"\n🧩 Created {len(chunks)} chunks. Showing first {limit}:\n")
    for i, c in enumerate(chunks[:limit], 1):
        print(f"--- Chunk {i} ---\n{c[:300]}...\n")
