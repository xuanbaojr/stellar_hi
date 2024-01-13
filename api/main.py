from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import csv
import pandas as pd

app = FastAPI()

class Chat(BaseModel):
    role: str | None = None
    content: str | None = None
    
class ChatHistory(BaseModel):
    chats: list

@app.put("/chats/{chat_id}", response_model=Chat)
async def update_history(chat_id: str, chat: Chat):
    update_chat = jsonable_encoder(chat)
    filename = "data\history.csv"
    with open(filename, "a") as csvfile:
        writer = csv.writer(csvfile)
        fields = [update_chat["role"], update_chat["content"]]
        writer.writerow(fields)
        csvfile.close()
    return update_chat

@app.get("/chats", response_model=ChatHistory)
async def get_chats():
    filename = "data\history.csv"
    df = pd.DataFrame(pd.read_csv(filename))
    chat_list = {"chats": []}
    for index, row in df.iterrows():
        chat_list["chats"].append({"role": row["role"], "content": row["content"]})
    return jsonable_encoder(chat_list)