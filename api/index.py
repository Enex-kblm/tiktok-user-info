from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from scraper import get_user_data

app = FastAPI(title="TikTok Info Lookup")

# Setup templates directory
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def handle_form(request: Request, username: str = Form(...)):
    try:
        if not username.strip():
            raise HTTPException(status_code=400, detail="Username tidak boleh kosong")
        
        info = get_user_data(username.strip())
        return templates.TemplateResponse("result.html", {"request": request, "info": info})
    except Exception as e:
        error_info = {"error": f"Terjadi kesalahan: {str(e)}"}
        return templates.TemplateResponse("result.html", {"request": request, "info": error_info})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# For Vercel deployment
handler = app