from app.api.core.errors.test_api.http_errors import http_error_handler
from app.api.routes import all, average, yoy, property, rent
from fastapi import FastAPI
from starlette.exceptions import HTTPException

app = FastAPI()

app.include_router(yoy.router, prefix="/api/pmx")
app.include_router(average.router, prefix="/api/pmx")
app.include_router(all.router, prefix="/api/pmx")
app.include_router(property.router, prefix="/api/eval")
app.include_router(rent.router, prefix="/api/pmx")

app.add_exception_handler(HTTPException, http_error_handler)
