from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import configparser
config = configparser.ConfigParser()

config.read("../config.ini")
db_name = config.get('MongoDB', 'DB')
db_user = config.get('MongoDB', 'DB-user')
db_pass = config.get('MongoDB', 'DB-pass')
dna_db = config.get('MongoDB', 'DNA-Database')
dna_collection = config.get('MongoDB', 'Collection')

uri = f"mongodb+srv://{db_user}:{db_pass}@myatlasclusteredu.idrf7.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
dna_collection = mongo_client[dna_db][dna_collection]