def chunk_text(text, max_chars=3500):
    chunks = []
    while len(text) > max_chars:
        split_index = text.rfind('.', 0, max_chars)
        if split_index == -1:
            split_index = max_chars
        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()
    chunks.append(text)
    return chunks
