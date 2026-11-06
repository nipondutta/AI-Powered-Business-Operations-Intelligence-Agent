from pathlib import Path
import pandas as pd
import fitz

def extract_file(path):
    p=Path(path); ext=p.suffix.lower()
    if ext==".pdf":
        with fitz.open(p) as doc: return "\\n".join(page.get_text() for page in doc)
    if ext in {".txt",".md"}: return p.read_text(encoding="utf-8",errors="ignore")
    if ext==".csv": return pd.read_csv(p).to_string(index=False)
    if ext==".xlsx":
        sheets=pd.read_excel(p,sheet_name=None)
        return "\\n".join(f"Sheet: {n}\\n{df.to_string(index=False)}" for n,df in sheets.items())
    raise ValueError("Supported file types: PDF, TXT, MD, CSV, XLSX.")
