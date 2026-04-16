from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "class_notes"
COLLECTION_NAME = "notes"


def init_database(uri=MONGO_URI, db_name=DB_NAME, collection_name=COLLECTION_NAME):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    collection.drop()
    print(f"Reset collection: {db_name}.{collection_name}")

    client.close()


if __name__ == "__main__":
    init_database()