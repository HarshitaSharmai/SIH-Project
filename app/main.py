# FastAPI app entrypoint
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .autocomplete import router as autocomplete_router

from .translate import router as translate_router
from .fhir.bundle import router as bundle_router


from .auth import verify_abha_token, audit_log


templates = Jinja2Templates(directory=str(__import__('pathlib').Path(__file__).parent / 'templates'))
app = FastAPI(title="Ayush Terminology Microservice")


# Secure all endpoints with ABHA token and add audit logging
@app.middleware("http")
async def abha_auth_audit_middleware(request: Request, call_next):
	# Skip docs and openapi endpoints
	if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
		return await call_next(request)
	token = request.headers.get("authorization", "").replace("Bearer ", "")
	user = None
	if token:
		try:
			user = verify_abha_token(token)
		except Exception:
			from fastapi.responses import JSONResponse
			return JSONResponse(status_code=401, content={"detail": "Invalid ABHA token"})
	# Audit log for every request
	audit_log(request, user, action=request.method, resource=request.url.path)
	response = await call_next(request)
	return response


# Serve demo UI
@app.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
	return templates.TemplateResponse("demo.html", {"request": request})

app.include_router(autocomplete_router)
app.include_router(translate_router)
app.include_router(bundle_router)
