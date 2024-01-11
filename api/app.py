from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os, wget, json
from elasticsearch.exceptions import NotFoundError

ELASTIC_PASSWORD = "JhDVEGyUbsDCy_8zM*6V"
CERT_FINGERPRINT = "ba625541c728aa5b9c0f6e46854847aaaf127508d8c4d7598383e752c0ae6a4a"
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

data_path = "data\openai.csv"
data = pd.read_csv(data_path)
data = pd.DataFrame(data)
print(data)

question = input("Nhap cau hoi:") #-> output : ban phai du 127 tin chi -> ok
# data = array[vector] : sinh vien phai dang ky 127 tin -> vector[1]

demo = insert_document(data)

k = 1
result = search_index_by_query(question, k)
print(result)

    
# H*gu8-e9l8zcrLFQA*L-


