import os
from pymongo import MongoClient
from bson import json_util

# Load the dumped database (previously exported MongoDB). It includes the embeddings.
with open("gameDatabase.games.json", "r") as f:
    data = json_util.loads(f.read())

# Connect to MongoDB
mongodb_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongodb_client["gameDatabase"]
collection = db["games"]

# Insert the documents
collection.insert_many(data)
print(f"Inserted {len(data)} documents into {collection.name}")

# Define our Vector Search Index. This can be done via the UI in MongoDB Atlas.
index_definition = {
    "name": "vector_index",
    "definition": {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 1536,
                "similarity": "cosine"
            }
        ]
    }
}
# Create the Search Index
collection.create_search_index(**index_definition)
print("Vector search index created.")