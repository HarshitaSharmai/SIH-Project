# Auto-complete value-set lookup endpoint for terminology search
from fastapi import APIRouter, Query


import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging
from app.icd11.client import ICD11Client  # Run with: uvicorn app.main:app --reload

router = APIRouter()




NAMASTE_CSV = Path(__file__).parent.parent / 'data' / 'namaste.csv'
if NAMASTE_CSV.exists():
	namaste_df = pd.read_csv(NAMASTE_CSV)
else:
	namaste_df = pd.DataFrame()

icd11_client = ICD11Client()


@router.get('/autocomplete', summary="Auto-complete terminology lookup")
def autocomplete(
	q: str = Query(..., description="Search term (partial or full)", min_length=2),
	system: str = Query('all', description="Code system: namaste|icd11-tm2|icd11-biomed|who-ayurveda|all")
) -> List[Dict]:
	results = []
	q_lower = q.lower()
	# NAMASTE (from CSV)
	if system in ('namaste', 'all') and not namaste_df.empty:
		mask = (
			namaste_df['Disorder_Name'].str.contains(q_lower, case=False, na=False) |
			namaste_df['NAMASTE_Code'].str.contains(q_lower, case=False, na=False)
		)
		for _, row in namaste_df[mask].iterrows():
			results.append({
				'system': 'namaste',
				'code': row['NAMASTE_Code'],
				'display': row['Disorder_Name'],
				'icd11_tm2': row.get('ICD11_TM2_Code', ''),
				'icd11_biomed': row.get('ICD11_Biomedicine_Code', ''),
				'who_ayurveda': row.get('WHO_Ayurveda_Term', '')
			})
	# WHO Ayurveda (from CSV)
	if system in ('who-ayurveda', 'all') and not namaste_df.empty:
		mask = namaste_df['WHO_Ayurveda_Term'].str.contains(q_lower, case=False, na=False)
		for _, row in namaste_df[mask].iterrows():
			results.append({
				'system': 'who-ayurveda',
				'code': row['NAMASTE_Code'],
				'display': row['WHO_Ayurveda_Term']
			})
	# ICD-11 TM2
	if system in ('icd11-tm2', 'all'):
		tm2_results = icd11_client.fetch_tm2_codes(q)
		for ent in tm2_results:
			results.append({
				'system': 'icd11-tm2',
				'code': ent.get('code', ''),
				'display': ent.get('title', {}).get('value', '')
			})
	# ICD-11 Biomedicine
	if system in ('icd11-biomed', 'all'):
		biomed_results = icd11_client.fetch_biomedicine_codes(q)
		for ent in biomed_results:
			results.append({
				'system': 'icd11-biomed',
				'code': ent.get('code', ''),
				'display': ent.get('title', {}).get('value', '')
			})
	return results[:20]  # Limit results for demo
