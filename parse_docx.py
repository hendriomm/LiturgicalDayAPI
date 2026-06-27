import docx

doc = docx.Document('Calendário Próprio do Brasil.docx')
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)
