import sys
import pypdf

def convert_pdf_to_text(pdf_path, txt_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        
        with open(txt_path, "w") as f:
            f.write(text)
        print(f"Successfully converted {pdf_path} to {txt_path}")
    except Exception as e:
        print(f"Error converting PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    pdf_path = "/Users/surfiniaburger/Desktop/vigilant-journey/Context Engineering_ Sessions & Memory.pdf"
    txt_path = "/Users/surfiniaburger/Desktop/vigilant-journey/Context_Engineering_Sessions_Memory.txt"
    convert_pdf_to_text(pdf_path, txt_path)
