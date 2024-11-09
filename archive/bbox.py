from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, ArrayObject, FloatObject, RectangleObject
import os

# with bbox in (l, t, r, b) format
def convert_topleft_to_bottomleft(bbox, page_height):
    l, t, r, b = bbox
    return (l, page_height - b, r, page_height - t)


def draw_bounding_boxes_on_pdf(input_pdf_path, output_pdf_path, bboxes, convert_tl_to_bl=False, color_palette=None):
    """
    Draws rectangle bounding boxes on a page of the input PDF using annotations and saves it as a new PDF.
    
    Args:
        input_pdf_path (str): Path to the original PDF file.
        output_pdf_path (str): Path to save the new PDF file with bounding boxes.
        bboxes (list of tuples): List of bounding box coordinates in the format (x0, y0, x1, y1).
        color_palette (list of tuples): List of RGB color tuples (values between 0 and 1) to use for the bounding boxes.
    """
    # Default color palette if none is provided
    if color_palette is None:
        color_palette = [
            (1, 0, 0),  # Red
            (0, 1, 0),  # Green
            (0, 0, 1),  # Blue
            (1, 1, 0),  # Yellow
            (1, 0, 1),  # Magenta
            (0, 1, 1)   # Cyan
        ]

    # Open the original PDF
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    # Add each bounding box with a different color
    for i, data in enumerate(bboxes):
        page_number, bbox = data[0], data[1]
        # Ensure the page number is within the valid range
        if page_number < 0 or page_number >= len(pdf_reader.pages):
            print(f"Invalid page number: {page_number}. The document has {len(pdf_reader.pages)} pages.")
            return

        # Get the specific page
        page = pdf_reader.pages[page_number]
        page_height = page.mediabox.top
        bbox = convert_topleft_to_bottomleft(bbox, page_height) if convert_tl_to_bl else bbox  # Convert top-left to bottom-left coordinates

        color = color_palette[i % len(color_palette)]  # Cycle through the color palette
        annotation = DictionaryObject()
        annotation.update({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Square"),
            NameObject("/Rect"): RectangleObject(bbox),
            NameObject("/C"): ArrayObject([FloatObject(c) for c in color]),  # RGB color
            NameObject("/Border"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(2)])  # Border with width 2
        })

        # Add the annotation to the page
        if "/Annots" in page:
            page["/Annots"].append(annotation)
        else:
            page[NameObject("/Annots")] = ArrayObject([annotation])

    # Add all pages to the writer
    for p in pdf_reader.pages:
        pdf_writer.add_page(p)

    # Save the modified PDF to a new file
    with open(output_pdf_path, "wb") as output_file:
        pdf_writer.write(output_file)
    print(f"Bounding boxes drawn and saved to {output_pdf_path}")


from pdf2image import convert_from_path

def crop_bounding_boxes_to_jpgs(input_pdf_path, output_jpg_dir, bbox, convert_tl_to_bl=False):
    """
    Crops a rectangular bounding box from a page of the input PDF and saves it as a PNG image.
    
    Args:
        input_pdf_path (str): Path to the original PDF file.
        output_png_path (str): Path to save the cropped PNG image.
        bbox (tuple): Bounding box coordinates in the format (x0, y0, x1, y1).
    """
    # Open the original PDF
    pdf_reader = PdfReader(input_pdf_path)
    
    for i, data in enumerate(bbox):
        page_number, bbox, label = data[0], data[1], data[2]

        # Ensure the page number is within the valid range
        if page_number < 0 or page_number >= len(pdf_reader.pages):
            print(f"Invalid page number: {page_number}. The document has {len(pdf_reader.pages)} pages.")
            return

        # Get the specific page
        page = pdf_reader.pages[page_number]
        pdf_writer = PdfWriter()
        pdf_writer.add_page(page)
        pdf_writer.write('.temp.pdf')
        
        page_reader = PdfReader('.temp.pdf')
        page2 = page_reader.pages[0]
        page_height = page2.mediabox.top
        bbox = convert_topleft_to_bottomleft(bbox, page_height) if convert_tl_to_bl else bbox  # Convert top-left to bottom-left coordinates

        # Crop the page to the bounding box
        page2.mediabox = RectangleObject(bbox)

        # Add the cropped page to the writer
        pdf_writer2 = PdfWriter()
        pdf_writer2.add_page(page2)
        pdf_writer2.write('.temp2.pdf')
        
        image = convert_from_path('.temp2.pdf')[0]
        output_jpg_path = f"{output_jpg_dir}/{page_number}-{i}_{label}.png"
        if not os.path.exists(output_jpg_dir):
            os.makedirs(output_jpg_dir)
        image.save(output_jpg_path, 'JPEG')
        os.remove('.temp.pdf')
        os.remove('.temp2.pdf')

        # Save the cropped page as a PNG image
        print(f"Bounding box cropped and saved to {output_jpg_path}")


if __name__ == "__main__":

    # Example usage
    input_pdf = "data/ingest/A review of the global climate change impacts, adaptation, and sustainable mitigation measures.pdf"
    output_pdf = "data/processed/A review of the global climate change impacts, adaptation, and sustainable mitigation measures.pdf"
    page_number = 0  # First page (0-indexed)
    bounding_box = (50, 100, 300, 400)  # Example bounding box coordinates
    bounding_boxes = [
        (50, 100, 300, 400),  # Example bounding box 1
        (150, 200, 350, 450), # Example bounding box 2
        (200, 250, 400, 500)  # Example bounding box 3
    ]
    draw_bounding_boxes_on_pdf(input_pdf, output_pdf, page_number, bounding_boxes)
