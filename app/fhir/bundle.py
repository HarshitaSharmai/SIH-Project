# FHIR Bundle upload endpoint for dual-coded ProblemList
from fastapi import APIRouter, Request, HTTPException
from fhir.resources.bundle import Bundle
from fhir.resources.operationoutcome import OperationOutcome
from typing import Dict, Any
import json

router = APIRouter()

@router.post('/fhir/bundle', summary="Upload FHIR Bundle with ProblemList")
async def upload_bundle(request: Request) -> Dict[str, Any]:
	try:
		data = await request.json()
		bundle = Bundle.parse_obj(data)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid FHIR Bundle: {e}")

	# Validate ProblemList entries for dual coding
	problems = []
	for entry in bundle.entry or []:
		resource = entry.resource
		if resource.resource_type == 'List' and getattr(resource, 'code', None):
			# Check for both NAMASTE and ICD-11 codes in the ProblemList
			codings = getattr(resource.code, 'coding', [])
			has_namaste = any(c.system and 'namaste' in c.system for c in codings)
			has_icd11 = any(c.system and 'icd' in c.system for c in codings)
			if has_namaste and has_icd11:
				problems.append(resource)
	if not problems:
		return OperationOutcome(issue=[{"severity": "error", "code": "invalid", "diagnostics": "No dual-coded ProblemList entries found."}]).dict()

	# For demo: just return count and echo back
	return {
		"status": "success",
		"dual_coded_problem_lists": len(problems),
		"received": data
	}
