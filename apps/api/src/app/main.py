from fastapi import FastAPI

app = FastAPI(
    title="Pullsar API",
    description="API for the Pullsar operator statistics dashboard.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Returns a welcome message for the API root."""
    return {"message": "Welcome to the Pullsar API"}
