
import subprocess
from string import whitespace
import datetime
import pymongo
from pymongo import MongoClient

uri = "mongodb+srv://boringsec:YXU2nkz4mdbwmt_dhv@cluster0.hmiqz4d.mongodb.net/boringsec_db?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client["boringsec_db"]
collection = db["phrases"]

# data = collection.find()


# partnersfile = 'partners.txt'
# with open(partnersfile, "w") as f:
#   partnerslist = f.write(str(document) + "\n")

# Read the data from partners.txt and insert to MongoDB collection

partnersfile = 'partners.txt'
with open(partnersfile, "r") as p:
    partners = p.readlines()

partner=''
keywords=[]

for partnerline in partners:
    if(partner == ''):
        partner = partnerline.strip()
        keywords = [partner]
        continue
    
    if(partnerline[0] in whitespace):
        keywords.append(partnerline)
        continue

    if partner and keywords:
        collection.insert_one({"partner": partner, "keywords": keywords})
        keywords = []
    
    partner = partnerline.strip()

    if partner and keywords:
        collection.insert_one({"partner": partner, "keywords": keywords})


message = ''
datestring = datetime.datetime.utcnow().strftime("%y-%m-%d")

for document in collection.find():
    partner = document["partner"]
    keywords = document["keywords"]

    with open("keywords.txt", "w") as k:
        k.write("\n".join(x.strip() for x in keywords))

    results = f'results.txt'
    cmd = f'python3 opensquat.py -o {results}'
    subprocess.call(cmd, shell=True)
    
    with open(results, "r") as f:
        lines = f.readlines()
    
    if(len(lines) > 0):
        message = f'{message}❗**Suspicious links for the {partner} community**❗\n{"".join(lines)}\n'

    #partner = ''
    #keywords = []


if(len(message) > 0):
    message = f'{message}For more information on what to do if your community has domains in this list, go here: https://discord.com/channels/933253328794689546/1073264004614594641/1073304829105016843'
    final = f'results-{datestring}.txt'
    with open(final, 'w') as f:
        f.write(message)

    print(message)