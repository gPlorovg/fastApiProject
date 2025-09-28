from asyncio import start_unix_server
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import engine, Base, get_session
from app import models

templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # DANGER!!! ONLY FOR DEVEL MODE!
        await conn.run_sync(Base.metadata.drop_all)
        ###
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Catering", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
Db = Annotated[AsyncSession, Depends(get_session)]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, status: str | None = Query(None)):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Catering", "status": status})

@app.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    db: Db,
    name: str = Form(...),
    email: str = Form(...),
    message: str | None = Form(None),
):
    order = models.Order(name=name.strip(), email=email.strip(), message=message.strip())
    db.add(order)
    try:
        await db.commit()
        return RedirectResponse(url="/?status=ok", status_code=303)
    except IntegrityError:
        await db.rollback()
        return RedirectResponse("/?status=dup", status_code=303)
    except Exception:
        await db.rollback()
        return RedirectResponse("/?status=err", status_code=303)
