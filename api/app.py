from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os, wget, json
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import BulkIndexError

ELASTIC_PASSWORD = "+4kXjAbs6A9bPnm*3b=B"
CERT_FINGERPRINT = "59530e151800deccd2c9f15f625f1fc11aa53c08e25e27d7741a3a0d2f69e119"

index_name = "stellar"

client =  Elasticsearch(
    "https://localhost:9200",
    
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD)
) 
print(client.info())
# create index with mapping
def create_index_by_mapping():
    mapping_code = {
        "mappings": {
            "properties": {
                "full_text": {"type": "text"},
                "creation_time": {"type": "date"},
                "content": {
                    "type": "nested",
                    "properties": {
                        "vector": {"type": "dense_vector", "dims": 1536},
                        "text": {"type": "text", "index": False}
                    }
                }
            }
        }
    }

    # Gửi yêu cầu PUT đến Elasticsearch
    response = client.indices.create(index=index_name, body=mapping_code)

    # In thông báo phản hồi từ Elasticsearch
    print(response)
    
def bulk_data(data):
    data_cols = data.shape[1]
    for index, row in data.iterrows():
        bulk_data = [
            {
                "title": "first paragraph another",
                "content": [
                    {"vector": using_embedding_model(row[f'content{i}']), "text": row[f'content{i}']} for i in range(data_cols-1)
                ],
            },
        ]

        try:
            response = helpers.bulk(client, bulk_data, index=index_name, refresh=True)
        except BulkIndexError as e:
            for err in e.errors:
                print(f"Error: {err}")



def search_index_by_query(query, k):
    query = using_embedding_model(query)
    response = client.search(
    index=index_name,
    body={
        "fields": ["title", "content"],
        "_source": False,
        "knn": {
            "query_vector": query,
            "field": "content.vector",
            "k": k,
            "num_candidates": 20,
            "inner_hits": {
                "_source": False,
                "fields": [
                    "content.text"
                ]
            }
            }
        }
    )

    return response['hits']['hits'][0]['inner_hits']['content']['hits']['hits'][0]['fields']['content'][0]['text']

# embedding
import os
from openai import AzureOpenAI
import json
import csv

def using_embedding_model(input):
    client_ = AzureOpenAI(
        azure_endpoint = "https://sunhackathon14.openai.azure.com/",
        api_key="9b2cb1b0bb95439e938ddf43e13aa955",
        api_version="2023-05-15"
    )

    response = client_.embeddings.create(
        model="ADA",
        input=input
    )
    # truong minh co 127 tin + toi hoc 50 tin -> chatgpt ->
    return response.data[0].embedding



def create_answer(context):
    client_ = AzureOpenAI(
        azure_endpoint = "https://sunhackathon14.openai.azure.com/",
        api_key="9b2cb1b0bb95439e938ddf43e13aa955",
        api_version="2023-05-15"
    )
    
    prompt = f"Trả lời câu hỏi dựa vào dữ liệu được cho ở bên dưới, và nếu câu hỏi không thể trả lời được, hãy trả lời mà không cần dựa vào dữ liệu được cho và nếu vẫn không trả lời được, hãy nói \"Tôi không biết\"\n\nDữ liệu được cho:\n {context}\n\n---\n\nCâu trả lời:"
    
    response = client_.chat.completions.create(
        model="GPT35TURBO",
        messages=[
            {'role': 'system', 'content': 'Bạn là một trợ lý tốt bụng.'},
            {'role': 'user', 'content': prompt}
        ],
    )
    return response.choices[0].message.content


data_path = "data/openai.csv"
data = pd.read_csv(data_path)

# data = pd.DataFrame(data)
# history_path = "data/history.csv"

print(data)

print(data.shape[1])
history_path = "data\history.csv"
his_data = pd.read_csv(history_path)

 
while True:
    
    history = pd.read_csv(history_path)
    history = pd.DataFrame(history)
    if history.empty == False:
        last_row = history.iloc[-1]
        
    else:
        last_row = {"role": ""}
        # print("a")
    if last_row["role"] == "user":
        
        question = last_row["content"] #-> output : ban phai du 127 tin chi -> ok
        # data = array[vector] : sinh vien phai dang ky 127 tin -> vector[1]


        k = 1
        result = search_index_by_query(question, 1)
        print(result)
        data['content'+str(data.shape[1] - 1)] = question
        data.to_csv(data_path, index=False)
         
        client.indices.delete(index=index_name)
        create_index_by_mapping()
        demo = bulk_data(data)

        context = "Bài toán tương tự:\n"
        for index, row in history.iterrows():
            if row["box_id"] == last_row["box_id"] and row["content"] != last_row["content"]:
                context += row["content"]
                context += "\n"
        context += f"Dữ liệu được cung cấp thêm: {result[0]}\n"
        context += f"Câu hỏi: {question}"
        print(context)
        
        answer = create_answer(context)
        print(answer)
        
        with open(history_path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            fields = [last_row["box_id"], "assistant", answer]
            writer.writerow(fields)
            file.close()