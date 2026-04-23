# Translation endpoint for NAMASTE ↔ TM2 using ConceptMap
from fastapi import APIRouter, Query


from typing import Dict, Optional
import pandas as pd
from pathlib import Path

router = APIRouter()


# Load NAMASTE CSV (for mapping)
NAMASTE_CSV = Path(__file__).parent.parent / 'data' / 'namaste.csv'
if NAMASTE_CSV.exists():
    namaste_df = pd.read_csv(NAMASTE_CSV)
else:
    namaste_df = pd.DataFrame()

@router.get('/translate', summary="Translate NAMASTE ↔ TM2 codes")
def translate(
    code: str = Query(..., description="Source code (NAMASTE or TM2)"),
    direction: str = Query('namaste-to-tm2', description="namaste-to-tm2 or tm2-to-namaste")
) -> Optional[Dict]:
    if namaste_df.empty:
        return {"error": "NAMASTE data not loaded"}
    if direction == 'namaste-to-tm2':
        row = namaste_df[namaste_df['NAMASTE_Code'] == code]
        if not row.empty:
            tm2_code = row.iloc[0].get('ICD11_TM2_Code', '')
            return {
                'source_system': 'namaste',
                'source_code': code,
                'target_system': 'icd11-tm2',
                'target_code': tm2_code,
                'display': row.iloc[0].get('Disorder_Name', '')
            }
    elif direction == 'tm2-to-namaste':
        row = namaste_df[namaste_df['ICD11_TM2_Code'] == code]
        if not row.empty:
            namaste_code = row.iloc[0].get('NAMASTE_Code', '')
            return {
                'source_system': 'icd11-tm2',
                'source_code': code,
                'target_system': 'namaste',
                'target_code': namaste_code,
                'display': row.iloc[0].get('Disorder_Name', '')
            }
    return {"error": "Mapping not found"}
