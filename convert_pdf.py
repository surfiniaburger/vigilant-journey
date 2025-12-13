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
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input.pdf> <output.txt>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    txt_path = sys.argv[2]
    convert_pdf_to_text(pdf_path, txt_path)
