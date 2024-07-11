from fastapi import FastAPI , HTTPException ,Request, status
from fastapi.responses import RedirectResponse
from app.routers import upload, download, dashboard, auth
from fastapi.staticfiles import StaticFiles
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(upload.router)
app.include_router(download.router)
app.include_router(dashboard.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": 
            """
            Welcome to the file encryption service!
            go to /dashboard to start
            """}

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/login")
    return await request.app.default_exception_handler(request, exc)