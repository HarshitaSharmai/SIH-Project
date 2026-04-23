# NAMASTE CSV Ingestion and FHIR CodeSystem/ConceptMap Generator
# This script parses the NAMASTE CSV and generates FHIR-compliant CodeSystem and ConceptMap resources.


import csv
from fhir.resources.codesystem import CodeSystem, CodeSystemConcept
from fhir.resources.conceptmap import ConceptMap, ConceptMapGroup, ConceptMapGroupElement, ConceptMapGroupElementTarget
from pathlib import Path
import json
from app.db import SessionLocal
from app.models import Terminology

# Path to NAMASTE CSV (update filename if needed)
NAMASTE_CSV = Path(__file__).parent.parent.parent / 'data' / 'namaste.csv'

# Output FHIR resources
CODESYSTEM_OUT = Path(__file__).parent.parent.parent / 'data' / 'namaste_codesystem.json'
CONCEPTMAP_OUT = Path(__file__).parent.parent.parent / 'data' / 'namaste_conceptmap.json'

# Example: expected columns in NAMASTE CSV
# ['NAMASTE_Code', 'Disorder_Name', 'ICD11_TM2_Code', 'ICD11_Biomedicine_Code', 'WHO_Ayurveda_Term']


def ingest_namaste_csv():
    # Ingest to database
    db = SessionLocal()
    with open(NAMASTE_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            try:
                term = Terminology(
                    namaste_code=row.get('NAMASTE_Code', ''),
                    disorder_name=row.get('Disorder_Name', ''),
                    icd11_tm2_code=row.get('ICD11_TM2_Code', ''),
                    icd11_biomedicine_code=row.get('ICD11_Biomedicine_Code', ''),
                    who_ayurveda_term=row.get('WHO_Ayurveda_Term', '')
                )
                db.add(term)
                count += 1
            except Exception as e:
                print(f"Error ingesting row: {row} - {e}")
        db.commit()
    db.close()
    print(f"Ingestion complete. {count} records ingested.")

    # Also build FHIR resources as before
    # Reload CSV for FHIR (or reuse reader if needed)
    with open(NAMASTE_CSV, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
    concepts = []
    for row in reader:
        concepts.append(CodeSystemConcept(
            code=row['NAMASTE_Code'],
            display=row['Disorder_Name'],
            property=[
                {'code': 'icd11-tm2', 'valueCode': str(row.get('ICD11_TM2_Code', ''))},
                {'code': 'icd11-biomed', 'valueCode': str(row.get('ICD11_Biomedicine_Code', ''))},
                {'code': 'who-ayurveda', 'valueString': str(row.get('WHO_Ayurveda_Term', ''))}
            ]
        ))
    codesystem = CodeSystem(
        resourceType='CodeSystem',
        id='namaste',
        url='http://example.org/fhir/CodeSystem/namaste',
        name='NAMASTE',
        status='active',
        content='complete',
        concept=concepts
    )
    # Build FHIR ConceptMap (NAMASTE → ICD-11 TM2)
    elements = []
    for row in reader:
        if row.get('ICD11_TM2_Code'):
            elements.append(ConceptMapGroupElement(
                code=row['NAMASTE_Code'],
                display=row['Disorder_Name'],
                target=[ConceptMapGroupElementTarget(
                    code=row['ICD11_TM2_Code'],
                    display='',
                    equivalence='equivalent'
                )]
            ))
    group = ConceptMapGroup(
        source='http://example.org/fhir/CodeSystem/namaste',
        target='http://id.who.int/icd/entity',
        element=elements
    )
    conceptmap = ConceptMap(
        resourceType='ConceptMap',
        id='namaste-to-icd11-tm2',
        url='http://example.org/fhir/ConceptMap/namaste-to-icd11-tm2',
        status='active',
        group=[group]
    )
    # Save resources
    with open(CODESYSTEM_OUT, 'w', encoding='utf-8') as f:
        json.dump(codesystem.dict(), f, ensure_ascii=False, indent=2)
    with open(CONCEPTMAP_OUT, 'w', encoding='utf-8') as f:
        json.dump(conceptmap.dict(), f, ensure_ascii=False, indent=2)
    print(f"FHIR CodeSystem written to {CODESYSTEM_OUT}")
    print(f"FHIR ConceptMap written to {CONCEPTMAP_OUT}")

if __name__ == '__main__':
    ingest_namaste_csv()
