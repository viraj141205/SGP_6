from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "message": message, "data": data}
    )


def error_response(message: str, status_code: int = 400, details: Any = None) -> JSONResponse:
    content = {"success": False, "message": message}
    if details:
        content["details"] = details
    return JSONResponse(status_code=status_code, content=content)


def paginated_response(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "has_next": (page * page_size) < total,
        "has_prev": page > 1
    }
