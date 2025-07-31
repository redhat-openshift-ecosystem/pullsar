from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Pullsar API",
    description="API for the Pullsar operator statistics dashboard.",
    version="0.1.0",
)


@app.get("/api/v1/")
def read_api_root():
    """Returns a simple API welcome message."""
    return {"message": "Welcome to the Pullsar API"}


static_files_path = "static"
if os.path.isdir(static_files_path):
    app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")
