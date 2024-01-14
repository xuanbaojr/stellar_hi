from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import pandas as pd
import shutil

app = FastAPI()

origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

class Chat(BaseModel):
    role: str | None = None
    content: str | None = None
    
class ChatHistory(BaseModel):
    chats: list


@app.post("/chats/add/{box_id}", response_model=ChatHistory)
async def update_history(box_id: str, chat: Chat):
    update_chat = jsonable_encoder(chat)
    filename = "data\history.csv"
    with open(filename, "a") as csvfile:
        writer = csv.writer(csvfile)
        fields = [box_id, update_chat["role"], update_chat["content"]]
        writer.writerow(fields)
        csvfile.close()
    new_chats = {"chats": []}
    new_chats["chats"].append({"role": update_chat["role"], "content": update_chat["content"]})
    answer = await get_latest_chat(box_id)
    new_chats["chats"].append({"role": answer["role"], "content": answer["content"]})
    return new_chats

@app.get("/chats/{box_id}", response_model=ChatHistory)
async def get_chats(box_id: str):
    filename = "data\history.csv"
    df = pd.DataFrame(pd.read_csv(filename))
    chat_list = {"chats": []}
    for index, row in df.iterrows():
        if int(row["box_id"]) == int(box_id):
            chat_list["chats"].append({"role": row["role"], "content": row["content"]})
    return jsonable_encoder(chat_list)

@app.get("/chats/latest/{box_id}", response_model=Chat)
async def get_latest_chat(box_id: str):
    filename = "data\history.csv"
    latest_chat = {"role": ""}
    while latest_chat["role"] != "assistant":
        df = pd.DataFrame(pd.read_csv(filename))
        for index, row in df.iterrows():
            if int(row["box_id"]) == int(box_id):
                latest_chat = {"role": row["role"], "content": row["content"]}
    return jsonable_encoder(latest_chat)


@app.delete("/chats/delete/{box_id}")
async def delete_box_chats(box_id: str):
    filename = "data\history.csv"
    with open(filename) as file, open("data\out.csv", 'w') as tmpfile:
        reader = csv.DictReader(file, fieldnames=["box_id", "role", "content"])
        writer = csv.DictWriter(tmpfile, fieldnames=["box_id", "role", "content"])
        for row in reader:
            if row["box_id"] != box_id:
                writer.writerow({"box_id": row["box_id"], "role": row["role"], "content": row["content"]})

    shutil.move("data\out.csv", filename)
        