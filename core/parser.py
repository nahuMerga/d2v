import fitz 
import os

def parse_pdf_text_chunks(pdf_path, max_chunk_size=700):

    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()


    paragraphs = [p.strip() for p in full_text.split('\n') if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk_size:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def parse_multiple_pdfs(file_paths, progressbar=None):

    result = {}
    total = len(file_paths)
    for idx, path in enumerate(file_paths):
        filename = os.path.basename(path)
        chunks = parse_pdf_text_chunks(path)
        result[filename] = chunks

        if progressbar:
            progressbar.setValue(int(((idx + 1) / total) * 100))

    return result
