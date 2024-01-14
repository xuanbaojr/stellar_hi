from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os, wget, json
from elasticsearch.exceptions import NotFoundError

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

def bulk_data(data):
    for index, row in data.iterrows():
        bulk_data = [
            {
                "title": "first paragraph another paragraph",
                "content": [
                    {"vector": using_embedding_model(row['content']), "text": row['content']},
                    {"vector": using_embedding_model(row['Content0']), "text": row['Content0']},
                    {"vector": using_embedding_model(row['Content1']), "text": row['Content1']},
                    {"vector": using_embedding_model(row['Content2']), "text": row['Content2']},
                    {"vector": using_embedding_model(row['Content3']), "text": row['Content3']},
                    {"vector": using_embedding_model(row['Content4']), "text": row['Content4']},
                    {"vector": using_embedding_model(row['Content5']), "text": row['Content5']},
                    {"vector": using_embedding_model(row['Content6']), "text": row['Content6']},
                    {"vector": using_embedding_model(row['Content7']), "text": row['Content7']},
                    {"vector": using_embedding_model(row['Content8']), "text": row['Content8']},
                    {"vector": using_embedding_model(row['Content9']), "text": row['Content9']},
                    
                ],
            },
        ]
        response = helpers.bulk(client, bulk_data, index=index_name, refresh=True)


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
            "num_candidates": 2,
            "inner_hits": {
                "_source": False,
                "fields": [
                    "content.text"
                ]
            }
            }
        }
    )
    result = []
    for i in range(k):
        inner_hits = response['hits']['hits'][i]['inner_hits']['content']['hits']['hits']
        for j in range(len(inner_hits)):
            content = inner_hits[j]['fields']['content']
            for k in range(len(content)):
                result.append(content[k]['text'][0])
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
    return response.data[0].embedding

data_path = os.path.join("data", "openai.csv")
data = pd.read_csv(data_path)

print(data)
bulk_data(data)
k = 2
question = "s" #-> output : ban phai du 127 tin chi -> ok
result = search_index_by_query(question, k)
print(result)


