import subprocess
from string import whitespace
import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGO_CONNECTION')

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["boringsec_db"]
collection = db["phrases"]

message = ''
datestring = datetime.datetime.utcnow().strftime("%y-%m-%d")

for document in collection.find():
    partner = document["partner"]
    keywords = document["keywords"]
    keywords.insert(0, partner)

    with open("keywords.txt", "w") as k:
        k.write("\n".join(x.strip() for x in keywords))

    results = f'results.txt'
    cmd = f'python3 opensquat.py -o {results}'
    subprocess.call(cmd, shell=True)

    with open(results, "r") as f:
        lines = f.readlines()

    if (len(lines) > 0):
        message = f'{message}❗**Suspicious links for the {partner} community**❗\n{"".join(lines)}\n'

if (len(message) > 0):
    message = f'{message}For more information on what to do if your community has domains in this list, go here: https://discord.com/channels/933253328794689546/1073264004614594641/1073304829105016843'
    final = f'results-{datestring}.txt'
    with open(final, 'w') as f:
        f.write(message)

    print(message)