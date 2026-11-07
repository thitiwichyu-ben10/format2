
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.calculate import calculate_totals
from app.validate import validate_quotation

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def set_cell_text(cell, text):
    cell.text = str(text)
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.name = "TH Sarabun New"
            run.font.size = Pt(14)

def fill_template(data, company, output_path):
    template_path = ROOT / "templates" / "quotation_template.docx"
    doc = Document(template_path)

    # Company identity placeholders
    replacements = {
        "{{COMPANY_NAME}}": company.get("company_name", ""),
        "{{COMPANY_ADDRESS}}": company.get("address", ""),
        "{{COMPANY_PHONE}}": company.get("phone", ""),
        "{{COMPANY_EMAIL}}": company.get("email", ""),
        "{{COMPANY_TAX_ID}}": company.get("tax_id", ""),
        "{{COMPANY_LOGO_TEXT}}": company.get("logo_text", ""),
        "{{BANK_DETAILS}}": company.get("bank_details", ""),
        "{{AUTHORIZED_SIGNATORY}}": company.get("authorized_signatory", ""),
    }

    # Replace placeholders in paragraphs and table cells while preserving template layout.
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old, new in replacements.items():
                if old in run.text:
                    run.text = run.text.replace(old, str(new))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        for old, new in replacements.items():
                            if old in run.text:
                                run.text = run.text.replace(old, str(new))

    # Fill quotation metadata placeholders.
    values = {
        "{{QUOTATION_NUMBER}}": data["quotation_number"],
        "{{QUOTATION_DATE}}": data["quotation_date"],
        "{{VALID_UNTIL}}": data.get("valid_until", ""),
        "{{CUSTOMER_NAME}}": data["customer"]["name"],
        "{{CUSTOMER_ADDRESS}}": data["customer"].get("address", ""),
        "{{CUSTOMER_TAX_ID}}": data["customer"].get("tax_id", ""),
        "{{CUSTOMER_CONTACT}}": data["customer"].get("contact", ""),
        "{{CUSTOMER_PHONE}}": data["customer"].get("phone", ""),
        "{{CUSTOMER_EMAIL}}": data["customer"].get("email", ""),
        "{{SUBJECT}}": data.get("subject", ""),
        "{{NOTES}}": data.get("notes", ""),
        "{{PAYMENT_TERMS}}": data.get("payment_terms", ""),
        "{{DELIVERY_TERMS}}": data.get("delivery_terms", ""),
    }
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old, new in values.items():
                if old in run.text:
                    run.text = run.text.replace(old, str(new))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        for old, new in values.items():
                            if old in run.text:
                                run.text = run.text.replace(old, str(new))

    totals = calculate_totals(
        data["items"],
        discount=data.get("discount", 0),
        vat_rate=data.get("vat_rate", 7),
        vat_included=data.get("vat_included", False),
    )

    # Template table order: metadata, line items, totals.
    item_table = doc.tables[1]
    for item in totals["items"]:
        cells = item_table.add_row().cells
        row_values = [
            len(item_table.rows) - 1,
            item["description"],
            item.get("unit", ""),
            item["quantity"],
            f'{item["unit_price"]:,.2f}',
            f'{item["amount"]:,.2f}',
        ]
        for cell, value in zip(cells, row_values):
            set_cell_text(cell, value)

    summary_values = {
        "{{SUBTOTAL}}": f'{totals["subtotal"]:,.2f}',
        "{{DISCOUNT}}": f'{totals["discount"]:,.2f}',
        "{{BEFORE_VAT}}": f'{totals["before_vat"]:,.2f}',
        "{{VAT_RATE}}": f'{totals["vat_rate"]:,.2f}',
        "{{VAT_AMOUNT}}": f'{totals["vat_amount"]:,.2f}',
        "{{GRAND_TOTAL}}": f'{totals["grand_total"]:,.2f}',
    }
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old, new in summary_values.items():
                if old in run.text:
                    run.text = run.text.replace(old, str(new))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        for old, new in summary_values.items():
                            if old in run.text:
                                run.text = run.text.replace(old, str(new))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return totals

def export_pdf(docx_path, output_dir):
    soffice = os.getenv("LIBREOFFICE_BIN", "soffice")
    executable = shutil.which(soffice) or (soffice if Path(soffice).exists() else None)
    if not executable:
        return None
    subprocess.run(
        [executable, "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(docx_path)],
        check=True, capture_output=True, text=True
    )
    return output_dir / (docx_path.stem + ".pdf")

def main():
    parser = argparse.ArgumentParser(description="Generate a quotation DOCX/PDF from JSON")
    parser.add_argument("input", help="Quotation JSON file")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    data = load_json(args.input)
    validate_quotation(data)
    company = load_json(ROOT / "config" / "company.json")

    out_dir = Path(args.output)
    docx_path = out_dir / f'quotation_{data["quotation_number"]}.docx'
    totals = fill_template(data, company, docx_path)
    pdf_path = export_pdf(docx_path, out_dir)

    print(f"DOCX: {docx_path}")
    print(f"ยอดสุทธิ: {totals['grand_total']:,.2f} THB")
    print(f"PDF: {pdf_path if pdf_path else 'ข้าม (ไม่พบ LibreOffice/soffice)'}")

if __name__ == "__main__":
    main()
