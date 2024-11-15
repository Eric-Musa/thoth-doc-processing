from pypdf import PdfReader, PdfWriter

def write_pdf_pages(pdf_path, output_path, page_range=10):
    if isinstance(page_range, int):
        page_range = range(page_range)
    page_range = list(page_range)
    assert isinstance(page_range, list), "page_range must be a list of integers."

    pdf_in = PdfReader(pdf_path)
    pdf_out = PdfWriter()
    for i in page_range:
        pdf_out.add_page(pdf_in.pages[i])
    
    with open(output_path, "wb") as f:
        pdf_out.write(f)
