import pytesseract
from pdf2image import convert_from_path
import re
import json
class InvoiceExtraction:
    
    def __init__(self, nlp) -> None:
        self.nlp =nlp
          
    def extract_key_paragraphs(self,text):
        invoice_key_lines = re.findall(r'(?i)(.*(?:invoice|total|amount|price|due|date).*[^\n])', text)
        return None if len(invoice_key_lines) ==0 else invoice_key_lines

    def extract_text_from_pdf(self, pdf_path):
        # Convert PDF to image

        pages = convert_from_path(pdf_path, 500)
        
        # Extract text from each page using Tesseract OCR
        text_data = ''
        for page in pages:
            text = pytesseract.image_to_string(page)
            text_data += text 
        # Return the text data
        return text_data


    # file_name = "1_xxqI8ve_i9YY0sUeHoe66A"
    
    def extract_data(self, file_name):
        text = self.extract_text_from_pdf(f'{file_name}.pdf')
        # with open(f'hybrid_{file_name}.txt', 'w') as f:
        #     # lines = text.split('\n')
        #     f.write(text)
        invoice_number = None
        invoice_date = None
        due_date = None
        total_amount_due = 0.0


        for para in self.extract_key_paragraphs(text):
            for ent in self.nlp(para).ents:
                print(ent.label_+ " - "+ent.text)

                if ent.label_ == 'INVOICE_NUMBER':
                    invoice_number = ent.text.strip()
            
                #First date entity would be the date of the invoice
                elif ent.label_ == 'DATE' and invoice_date== None:
                        invoice_date = ent.text.strip()
                #Finding date entity with due keyword
                elif ent.label_ == 'DATE' :
                        due_date = ent.text.strip()
                
                #Assuming hightest Money entity would be the total amount
                elif ent.label_ == 'MONEY' and total_amount_due<float(ent.text.strip()):
                    total_amount_due = float(ent.text.strip())
        # print()
        # print('Invoice Number:', invoice_number)
        # print('Invoice Date:', invoice_date)
        # print('Due Date:', due_date)
        # print('Total Amount Due:', total_amount_due)
        return json.dumps([
        {
            "fieldName": "invoice Id",
            "fieldValue": f"{invoice_number}"
        },
        {
            "fieldName": "Order Number",
            "fieldValue": f"{invoice_date}"
        },
        {
            "fieldName": "Total Due",
            "fieldValue":  f"{total_amount_due}"
        },
        {
            "fieldName": "Due Date",
            "fieldValue":  f"{due_date}"
        }
    ])