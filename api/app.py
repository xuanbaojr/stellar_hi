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
    index_mapping = {
        "properties":{
            
            "title": {"type": "text"},
            "content": {
                "properties": {
                    # "type": "nested",
                    "text": {
                        "type": "text",
                        "index": "true"
                    },
                    "vector": {
                        "type": "dense_vector",
                        "dims": 1536,
                        "index": "true",
                        "similarity": "cosine"
                    }
                }
                },
        }
    }
    client.indices.create(index=index_name, mappings=index_mapping)
    #index data into elasticSeach
def dataframe_to_bulk_actions(df):

    for index, row in df.iterrows():
        yield {
            "_index": index_name,
            "_source": {
                'title' : row["Title"],
                'content':{
                    "text": row["content0"], "vector": using_embedding_model(row['content0']).data[0].embedding
                }
                # 'content' : [
                #     {"text": row["content0"], "vector": using_embedding_model(row['content0']).data[0].embedding},
                #     {"text": row["content1"], "vector": using_embedding_model(row['content1']).data[0].embedding},
                #     {"text": row["content2"], "vector": using_embedding_model(row['content2']).data[0].embedding},
                #     {"text": row["content3"], "vector": using_embedding_model(row['content3']).data[0].embedding},
                #     {"text": row["content4"], "vector": using_embedding_model(row['content4']).data[0].embedding},
                #     {"text": row["content5"], "vector": using_embedding_model(row['content5']).data[0].embedding},
                #     {"text": row["content6"], "vector": using_embedding_model(row['content6']).data[0].embedding},
                #     {"text": row["content7"], "vector": using_embedding_model(row['content7']).data[0].embedding},
                #     {"text": row["content8"], "vector": using_embedding_model(row['content8']).data[0].embedding},
                #     {"text": row["content9"], "vector": using_embedding_model(row['content9']).data[0].embedding}
                # ],
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
    print(query)
    response = client.search(
    index = index_name,
    knn={
        "field": "content.vector",
        "query_vector": query,
        "k": k,
        "num_candidates": 100,
        # "inner_hits": {
        #     "fields": [
        #        'content.text'
        #     ]
        # }
        }
    )

    result = []
    for i in range(k):
        result.append( response['hits']['hits'][i]['_source']['content']['text'])
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

data_path = os.path.join("data", "openai.csv")
data = pd.read_csv(data_path)
begin = 0
step = 3
for i in range(len(data)):
    for j in range(10):
        end = min((begin+step),len(data.at[i, 'content']))
        data.at[i, 'content' + str(j)] = data.at[i, 'content'][begin:end]
        begin = begin + step

print(data)

demo = insert_document(data)

k = 2
for i in range(100):
    question = input("Nhap cau hoi:") #-> output : ban phai du 127 tin chi -> ok
    result = search_index_by_query(question, k)
    print(result)

    
# H*gu8-e9l8zcrLFQA*L-


