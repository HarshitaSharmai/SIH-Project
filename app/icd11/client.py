# WHO ICD-11 API Client for TM2 and Biomedicine
import httpx
import os
from typing import List, Dict, Optional

ICD11_API_BASE = "https://id.who.int/icd/release/11"
ICD11_API_KEY = os.getenv("ICD11_API_KEY", "demo-key")  # Replace with real key in production

class ICD11Client:
	def __init__(self, api_key: Optional[str] = None):
		self.api_key = api_key or ICD11_API_KEY
		self.base_url = ICD11_API_BASE
		self.headers = {"API-Version": "v2", "Accept": "application/json", "Authorization": f"Bearer {self.api_key}"}

	def fetch_tm2_codes(self, query: str = "") -> List[Dict]:
		"""Fetch TM2 codes from ICD-11 API (search or list)."""
		url = f"{self.base_url}/tm2/search"
		params = {"q": query, "flatResults": True}
		with httpx.Client() as client:
			resp = client.get(url, params=params, headers=self.headers)
			resp.raise_for_status()
			return resp.json().get("destinationEntities", [])

	def fetch_biomedicine_codes(self, query: str = "") -> List[Dict]:
		"""Fetch Biomedicine codes from ICD-11 API (search or list)."""
		url = f"{self.base_url}/mms/search"
		params = {"q": query, "flatResults": True}
		with httpx.Client() as client:
			resp = client.get(url, params=params, headers=self.headers)
			resp.raise_for_status()
			return resp.json().get("destinationEntities", [])

	def get_code_details(self, code: str) -> Dict:
		"""Fetch details for a specific ICD-11 code (TM2 or Biomedicine)."""
		url = f"{self.base_url}/entity/{code}"
		with httpx.Client() as client:
			resp = client.get(url, headers=self.headers)
			resp.raise_for_status()
			return resp.json()
