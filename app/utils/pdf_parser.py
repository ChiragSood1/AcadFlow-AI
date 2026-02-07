from io import BytesIO

import pdfplumber


def extract_text_from_pdf(pdf_bytes: BytesIO):
    # simple helper that reads all pages and joins the text
    pdf_bytes.seek(0)
    texts = []
    with pdfplumber.open(pdf_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        page_count = len(pdf.pages)

    full_text = "\n".join(texts)
    return full_text, page_count

