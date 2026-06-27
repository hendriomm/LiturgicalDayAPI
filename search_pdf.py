from PyPDF2 import PdfReader
reader = PdfReader("romanmissal_classical.pdf")
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if "Carmel" in text:
        print(f"Page {i+1}:")
        print(text[:1000]) # Print context
        print("---")
