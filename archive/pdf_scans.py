from pypdf import PdfReader, PdfWriter
import os

orig_pdf_path = 'test/Pdf scans.pdf'
rotated_pdf_path = 'test/Pdf scans rotated.pdf'

if not os.path.isfile(rotated_pdf_path):
    ## read in 'test/Pdf scans.pdf' and rotate each page 90 degrees counter-clockwise
    pdf = PdfReader(orig_pdf_path)
    out = PdfWriter()
    for page in pdf.pages:
        page.rotate(270)
        out.add_page(page)

    out.write(rotated_pdf_path)


from utils.docling_utils import docling_export, docling_parse

# doc_path = 'test/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1 - page 1.pdf'
doc_path = rotated_pdf_path
document, conv_res = docling_parse(doc_path)  # , force_parse=True)
elements, tables, images = docling_export(doc_path)