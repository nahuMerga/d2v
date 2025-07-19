def summarize_chunks(chunks):
    return "\n\n".join([f"📝 Summary of chunk {i+1}: {chunk[:100]}..." for i, chunk in enumerate(chunks)])
