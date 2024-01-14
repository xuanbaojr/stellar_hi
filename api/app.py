from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os, wget, json
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import BulkIndexError


# ELASTIC_PASSWORD = "dA9UFqZxZ4uL-*-v=4lH"
ELASTIC_PASSWORD = "dA9UFqZxZ4uL-*-v=4lH"
CERT_FINGERPRINT = "ddd5637f667684e20163b3438d55edb5d15b6eff79978e81da7e3f9628ca4b8e"
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
    
# create_index_by_mapping()
def bulk_data(data):
    for index, row in data.iterrows():
        bulk_data = [
            {
                "title": "first paragraph another",
                "content": [
                    {"vector": using_embedding_model(row['content0']), "text": row['content0']},
                    {"vector": using_embedding_model(row['content1']), "text": row['content1']},
                    {"vector": using_embedding_model(row['content2']), "text": row['content2']},
                    {"vector": using_embedding_model(row['content3']), "text": row['content3']},
                    # {"vector": using_embedding_model(row['content3']), "text": row['content3']},
                    # {"vector": using_embedding_model(row['Content4']), "text": row['Content4']},
                    # {"vector": using_embedding_model(row['Content5']), "text": row['Content5']},
                    # {"vector": using_embedding_model(row['Content6']), "text": row['Content6']},
                    # {"vector": using_embedding_model(row['Content7']), "text": row['Content7']},
                    # {"vector": using_embedding_model(row['Content8']), "text": row['Content8']},
                    # {"vector": using_embedding_model(row['Content9']), "text": row['Content9']},
                    
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

data_path = os.path.join("data", "openai.csv")
data = pd.read_csv(data_path)

print(data)
# bulk_data(data)
k = 1
for i in range(10):
    question = input(":") #-> output : ban phai du 127 tin chi -> ok
    result = search_index_by_query(question, k)
    print(result)


