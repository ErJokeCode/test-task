from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import settings
from swapi_dev.router import router as r_swapi_dev
from chat.router import router as r_chat


_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log.info("Start server")
    yield
    _log.info("Stop server")

app = FastAPI(
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(r_swapi_dev)
app.include_router(r_chat)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
