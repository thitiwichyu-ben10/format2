
# Quotation Agent Starter

โครงสร้างเริ่มต้นสำหรับระบบ AI Agent ที่รับข้อมูลใบเสนอราคาในรูปแบบ JSON
ตรวจสอบข้อมูล คำนวณยอดเงิน และสร้างเอกสารจาก Master Template โดยไม่ให้ AI
เปลี่ยนรูปแบบเอกสารเอง

> **ข้อมูลบริษัทถูกเว้นว่างไว้ทั้งหมด** ให้เติมใน `config/company.json` และแก้
> `templates/quotation_template.docx` ตาม CI ของบริษัทก่อนใช้งานจริง

## หลักการออกแบบ

- AI Agent มีหน้าที่แปลงคำสั่ง/เอกสารต้นทางให้เป็นข้อมูลตาม `schemas/quotation.schema.json`
- Python เป็นผู้ตรวจสอบข้อมูลและคำนวณยอดเงิน ไม่ใช้ LLM คำนวณยอดเงินจริง
- DOCX Master Template เป็นผู้ควบคุมหน้าตาเอกสาร
- ระบบเติมข้อมูลลง Template และส่งออก DOCX; หากติดตั้ง LibreOffice จะส่งออก PDF ได้
- ข้อมูลบริษัท, โลโก้, ที่อยู่, เลขผู้เสียภาษี, ช่องทางชำระเงิน และผู้ลงนามเป็น placeholder

## โครงสร้างโปรเจกต์

```text
quotation-agent-starter/
├── app/
│   ├── __init__.py
│   ├── calculate.py
│   ├── generate.py
│   └── validate.py
├── config/
│   └── company.json
├── examples/
│   └── quotation.json
├── schemas/
│   └── quotation.schema.json
├── templates/
│   └── quotation_template.docx
├── tests/
│   └── test_quotation.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## เริ่มต้นใช้งาน

### 1. ติดตั้ง

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. เติมข้อมูลบริษัท

แก้ไข `config/company.json` และใส่ข้อมูลจริงแทนค่าว่าง เช่น ชื่อบริษัท ที่อยู่ เลขประจำตัวผู้เสียภาษี
เบอร์โทร อีเมล โลโก้ และข้อมูลการชำระเงิน

### 3. เตรียมข้อมูลใบเสนอราคา

ดูตัวอย่างที่ `examples/quotation.json` แล้วสร้าง JSON ของงานจริงตาม schema

### 4. สร้างเอกสาร

```bash
python -m app.generate examples/quotation.json --output output
```

ผลลัพธ์:
- `output/quotation_QT-2026-001.docx`
- `output/quotation_QT-2026-001.pdf` (ถ้าติดตั้ง LibreOffice และพบคำสั่ง `soffice`)

### 5. ทดสอบ

```bash
pytest
```

## เชื่อมกับ AI Agent

ให้ AI ส่งออกเฉพาะ JSON ตาม schema ใน `schemas/quotation.schema.json` แล้วส่ง JSON นั้นให้ระบบนี้
อย่าให้ AI สร้าง DOCX/PDF หรือกำหนด style เอง

ตัวอย่าง system instruction สำหรับ AI:

```text
คุณเป็นผู้ช่วยจัดเตรียมข้อมูลใบเสนอราคา
1. แปลงข้อมูลที่ผู้ใช้ให้เป็น JSON ตาม quotation.schema.json เท่านั้น
2. ห้ามเดาราคา จำนวน เลขผู้เสียภาษี ที่อยู่ หรือข้อมูลที่ไม่มีในแหล่งข้อมูล
3. ถ้าข้อมูลจำเป็นขาด ให้ถามผู้ใช้ก่อนส่งข้อมูล
4. ห้ามคำนวณยอดรวมเอง ให้ส่ง quantity, unit_price, discount และ vat_rate
5. ใช้ null หรือแจ้งว่าขาดข้อมูลตาม schema ห้ามสร้างข้อมูลสมมติ
6. ห้ามเปลี่ยนรูปแบบเอกสาร เพราะระบบ Template เป็นผู้ควบคุม
```

## กฎการคำนวณเริ่มต้น

- จำนวนเงินใช้ทศนิยม 2 ตำแหน่ง
- ส่วนลดเป็นจำนวนเงินรวมทั้งเอกสาร (THB)
- VAT คำนวณจากยอดหลังหักส่วนลด
- `vat_included = false` หมายถึงราคายังไม่รวม VAT
- `vat_included = true` หมายถึงราคาต่อหน่วยรวม VAT แล้ว
- กฎเหล่านี้เป็นค่าเริ่มต้น ต้องให้ฝ่ายบัญชีตรวจสอบก่อนใช้งานจริง

## จุดที่ต้องปรับก่อนใช้งานจริง

- เติมข้อมูลบริษัทและ branding ใน `config/company.json` และ DOCX template
- ให้ฝ่ายบัญชียืนยันวิธีคิด VAT, ส่วนลด, การปัดเศษ และเงื่อนไขเครดิต
- กำหนดเลขที่ใบเสนอราคาให้ไม่ซ้ำ โดยเชื่อมฐานข้อมูล/ระบบเลขเอกสาร
- เพิ่มระบบสิทธิ์ผู้ใช้, audit log, approval และการจัดเก็บเอกสาร
- เพิ่มการตรวจสอบข้อมูลลูกค้าและรายการสินค้าจากฐานข้อมูลจริง
- ทดสอบเอกสารหลายหน้าและฟอนต์ภาษาไทยบนเครื่อง production

## หมายเหตุ

Starter นี้ยังไม่เชื่อม OpenAI API หรือฐานข้อมูลโดยตรง เป็นแกน Document Engine
ที่พร้อมให้เชื่อมกับ AI Agent ภายหลัง
