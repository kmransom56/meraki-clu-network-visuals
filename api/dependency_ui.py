from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from api.dependency_dashboard import dependency_status

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/dependencies/ui")
def dependency_ui(request: Request):
    data = dependency_status()
    return templates.TemplateResponse(
        "dependencies.html",
        {
            "request": request,
            "status": data["status"],
            "missing": data["missing_packages"],
            "extra": data["extra_packages"],
        }
    )
