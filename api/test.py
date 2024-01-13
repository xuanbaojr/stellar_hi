import os
# from openai import AzureOpenAI

# client = AzureOpenAI(
#     azure_endpoint = "https://sunhackathon14.openai.azure.com/",
#     api_key="9b2cb1b0bb95439e938ddf43e13aa955",
#     api_version="2023-05-15"
# )
# def chatgpt(content):

#     response = client.chat.completions.create(
#         model="GPT35TURBO16K", # model = "deployment_name".
#         messages=[
#             {"role": "user", "content": content}
#         ]
#     )
#     print(response.model_dump_json(indent=2))
#     print(response.choices[0].message.content)

# #print(response)

# for i in range(10):
#     content = input(":")
#     chatgpt(content)


# split data to structure
import pandas as pd
import os

data_path = os.path.join("data", "openai.csv")
data = pd.read_csv(data_path)


begin = 0
step = 3
for i in range(len(data)):
    for j in range(10):
        end = min((begin+step),len(data.at[i, 'content']))
        data.at[i, 'content' + str(j)] = data.at[i, 'content'][begin:end]
        begin = begin + step
# Using loc to access the 'text' column of the first, row

print(data)
