import base64, asyncio
import uvicorn
from typing import Annotated
from thefuzz import process, fuzz
from fastapi import FastAPI, WebSocket, File, UploadFile, WebSocketDisconnect, Body, Header, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise
from models import FileModel


app = FastAPI(root_path="/api", docs_url=None, redoc_url=None)

register_tortoise(
    app,
    db_url="postgres://postgres:1234@gosts-database:5432/gosts",  # Или PostgreSQL: "postgres://user:pass@localhost/db"
    modules={"models": ["models"]},  # Где искать модели
    generate_schemas=True,  # Автосоздание таблиц
    add_exception_handlers=True,
)


@app.websocket("/")
async def get_gosts(websocket: WebSocket):
    await websocket.accept()
    try:
        #await FileModel.all().delete()

        files = await FileModel.all().values("name", "content")
        for i in range(len(files)):
            files[i]["content"] = base64.b64encode(files[i]["content"]).decode("utf-8") #{files: [{content: "sdvvb", name: "as"}, {content: "asdf", name: "as"}]}
            await websocket.send_json({"file": files[i], "number": i, "its_search": False})

        while True:
            data = await websocket.receive_json()
            print(data)
            sorted_file_names = await search(data["text"])
            for i in range(len(sorted_file_names)):
                file_name = sorted_file_names[i][0]
                similarity = sorted_file_names[i][1]
                file = await FileModel.get(name=file_name)
                file_content = file.content
                await websocket.send_json({"file": {"name": file_name, "content": base64.b64encode(file_content).decode("utf-8")}, "number": i, "its_search": True})
    except WebSocketDisconnect:
        pass



async def search(text):
    for_send = await FileModel.filter(name=text).values("name", "content")

    if for_send: # если есть точное совпадение
        for file in for_send:
            file["content"] = base64.b64encode(file["content"]).decode("utf-8")
        return for_send

    files = await FileModel.all().values("name")

    # Выносим синхронный код в отдельный поток
    def sync_search():
        file_names = [file["name"] for file in files]
        return process.extract(text.lower(), file_names, scorer=fuzz.WRatio, limit=len(file_names))

    matches = await asyncio.to_thread(sync_search)# получаем [("ГОСТ 12345-2020", 95), ("ТУ 12345-2015", 75), ("ГОСТ 12346-2021", 60)]
    return matches


SECRET_KEY = "1234"


async def verify_secret_key(secret_key: Annotated[str, Header(alias="secret-key")] = None):
    if secret_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    return True


@app.post("/add-file/")
async def create_db(file: Annotated[UploadFile, File()], verified: bool = Depends(verify_secret_key)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_content = await file.read()  # Читаем файл как бинарные данные

    await FileModel.create(name=file.filename, content=file_content)

    return {"Success": True, "message": "File created"}


class FileForDelete(BaseModel):
    name: str


@app.delete("/delete-file/")
async def delete_file(name: FileForDelete, verified: bool = Depends(verify_secret_key)):
    files = await FileModel.filter(name=name.name)
    if files:
        await files[0].delete()
        return {"Success": True, "message": "File deleted"}
    elif name.name == "last":
        last_added = await FileModel.all().order_by("-id").first()
        if last_added:
            await last_added.delete()
            return {"Success": True, "message": "File deleted"}
        else:
            return {"Success": False, "message": "File not found"}
    return {"Success": False, "message": "File not found"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://87.228.102.121"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if "__main__" == __name__:
    uvicorn.run(app, host="0.0.0.0", port=8001)