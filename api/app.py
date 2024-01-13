from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os, wget, json
from elasticsearch.exceptions import NotFoundError

ELASTIC_PASSWORD = "KENehWXj_IpXqG5-n7sX"
CERT_FINGERPRINT = "b9d7dc9c6a701580d91134d1de46db58610e98718a97a9c710ea72cd14e73856"
index_name = "stellar"

client =  Elasticsearch(
    "https://localhost:9200",
    # ca_certs="http_ca.crt",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    basic_auth=("elastic", ELASTIC_PASSWORD)
) 
print(client.info())
# create index with mapping
def create_index_by_mapping():
    index_mapping = {
        "properties":{
            "title_vector":{
                "type" : "dense_vector",
                "dims": 1536,
                "index": "true",
                "similarity":"cosine"
            },
            "content_vector": {
                "type": "dense_vector",
                "dims": 1536,
                "index": "true",
                "similarity": "cosine"
        },
            
            "title": {"type": "text"},
            "content": {"type": "text"},
            "vector_id": {"type": "long"}
        }
    }
    client.indices.create(index=index_name, mappings=index_mapping)

    #index data into elasticSeach
def dataframe_to_bulk_actions(df):

    for index, row in df.iterrows():
        yield {
            "_index": index_name,
            "_source": {
                'title' : row["title"],
                'content' : row["content"],
                'content_vector' : using_embedding_model(row['content']).data[0].embedding,
            #  'title_vector' : json.loads(row["content_vector"]),
            }
        }
def insert_document(data):
    start = 0
    end = len(data)
    batch_size = 100
    for batch_start in range(start, end, batch_size):
        batch_end = min(batch_start + batch_size, end)
        batch_dataframe = data.iloc[batch_start:batch_end]
        action = dataframe_to_bulk_actions(batch_dataframe)
        helpers.bulk(client, action)

def search_index_by_query(question, k):

    query = using_embedding_model(question).data[0].embedding
    response = client.search(
        index = index_name,
        knn={
            "field": "content_vector",
            "query_vector": query,
            "k": k,
            "num_candidates": 100
        }
    )

    result = []
    for i in range(k):
        result.append( response['hits']['hits'][i]['_source']['content'])
    return result

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
    return response
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


data_path = "data\openai.csv"
data = pd.read_csv(data_path)
data = pd.DataFrame(data)
history_path = "data\history.csv"
print(data)
while True:
    history = pd.read_csv(history_path)
    history = pd.DataFrame(history)
    last_row = history.iloc[-1]
    if last_row["role"] == "user":
        question = last_row["content"] #-> output : ban phai du 127 tin chi -> ok
        # data = array[vector] : sinh vien phai dang ky 127 tin -> vector[1]

        demo = insert_document(data)

        k = 1
        result = search_index_by_query(question, 1)
        print(result)

        context = "Dữ liệu đoạn hội thoại trước đây:\n"
        for index, row in history.iterrows():
            if row["content"] != last_row["content"]:
                context += row["content"]
                context += "\n"
        context += f"Dữ liệu được cung cấp thêm: {result[0]}\n"
        context += f"Câu hỏi: {question}"
        print(context)
        
        answer = create_answer(context)
        print(answer)
        
        with open(history_path, "a") as file:
            writer = csv.writer(file)
            fields = ["assistant", answer]
            writer.writerow(fields)
            file.close()    

    
# H*gu8-e9l8zcrLFQA*L-


