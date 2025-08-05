from fastapi import FastAPI

app = FastAPI(
    title="Pullsar API",
    description="API for the Pullsar operator statistics dashboard.",
    version="0.1.0",
)


@app.get("/v1/")
def read_api_root():
    """Returns a simple API welcome message."""
    return {"message": "Welcome to the Pullsar API"}
