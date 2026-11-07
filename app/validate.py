
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "quotation.schema.json"

def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

def validate_quotation(data):
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        messages = []
        for error in errors:
            path = ".".join(str(part) for part in error.path) or "(root)"
            messages.append(f"{path}: {error.message}")
        raise ValueError("ข้อมูลใบเสนอราคาไม่ผ่านการตรวจสอบ:\\n- " + "\\n- ".join(messages))
    return True
