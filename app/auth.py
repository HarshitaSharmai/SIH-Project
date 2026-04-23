# OAuth 2.0 (ABHA) token validation and audit logging
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
import logging
import time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dummy ABHA public key for demo (replace with real key in production)
ABHA_PUBLIC_KEY = "demo-public-key"

def verify_abha_token(token: str = Depends(oauth2_scheme)) -> dict:
	try:
		# For demo, just decode without verification
		payload = jwt.get_unverified_claims(token)
		# In production, use: jwt.decode(token, ABHA_PUBLIC_KEY, algorithms=["RS256"])
		return payload
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid ABHA token",
			headers={"WWW-Authenticate": "Bearer"},
		)

def audit_log(request: Request, user: Optional[dict], action: str, resource: str, consent: Optional[dict] = None):
	# Simple audit log to file (extend for DB or external logging)
	log_entry = {
		"timestamp": int(time.time()),
		"ip": request.client.host if request.client else None,
		"user": user,
		"action": action,
		"resource": resource,
		"consent": consent
	}
	logging.basicConfig(filename="audit.log", level=logging.INFO)
	logging.info(log_entry)
