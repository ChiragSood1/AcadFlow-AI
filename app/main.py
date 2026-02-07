from fastapi import FastAPI
from dotenv import load_dotenv


from app.api.routes import upload, analyze, query
from app.core.logging import configure_logging

# create the main FastAPI app
app = FastAPI(title="AI Academic Workflow Engine")

# set up logging once
configure_logging()

# add all our routers
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
app.include_router(query.router, prefix="/query", tags=["query"])


load_dotenv()
