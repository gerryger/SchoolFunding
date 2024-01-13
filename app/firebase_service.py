

import os
from pprint import pprint
from datetime import datetime, timezone
from operator import itemgetter
from dotenv import load_dotenv
from flask import current_app

from firebase_admin import credentials, initialize_app, firestore, storage


load_dotenv()

DEFAULT_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "google-credentials.json")
CREDENTIALS_FILEPATH = os.getenv("GOOGLE_CREDENTIALS_FILEPATH", default=DEFAULT_FILEPATH)


def generate_timestamp():
    return datetime.now(tz=timezone.utc)


class FirebaseService:
    """
    Fetches data from the cloud firestore database.

    Uses locally downloaded credentials JSON file.
    """
    def __init__(self):
        self.creds = credentials.Certificate(CREDENTIALS_FILEPATH)
        self.app = initialize_app(self.creds) # or set FIREBASE_CONFIG variable and initialize without creds
        self.db = firestore.client()
        self.bucket = storage.bucket('school-funding.appspot.com')


    #
    # PRODUCTS
    #

    def fetch_products(self):
        products_ref = self.db.collection("products")
        products = [doc.to_dict() for doc in products_ref.stream()]
        return products
    

    #
    # ORDERS
    #

    @property
    def orders_ref(self):
        return self.db.collection("orders")

    def create_order(self, user_email, product_info):
        """
        Params :

            user_email (str)

            product_info (dict) with name, description, price, and url

        """
        new_order_ref = self.orders_ref.document() # new document with auto-generated id
        new_order = {
            "user_email": user_email,
            "product_info": product_info,
            "order_at": generate_timestamp()
        }
        results = new_order_ref.set(new_order)
        #print(results) #> {update_time: {seconds: 1648419942, nanos: 106452000}}
        return new_order, results

    def fetch_orders(self):
        orders = [doc.to_dict() for doc in self.orders_ref.stream()]
        return orders

    def fetch_user_orders(self, user_email):
        query_ref = self.orders_ref.where("user_email", "==", user_email)

        # sorting requires configuration of a composite index on the "orders" collection,
        # ... so to keep it simple for students, we'll sort manually (see below)
        #query_ref = query_ref.order_by("order_at", direction=firestore.Query.DESCENDING) #.limit_to_last(20)

        # let's return the dictionaries, so these are serializable (and can be stored in the session)
        docs = list(query_ref.stream())
        orders = []
        for doc in docs:
            order = doc.to_dict()
            order["id"] = doc.id
            #breakpoint()
            #order["order_at"] = order["order_at"].strftime("%Y-%m-%d %H:%M")
            orders.append(order)
        # sorting so latest order is first
        orders = sorted(orders, key=itemgetter("order_at"), reverse=True)
        return orders

    #
    # USERS
    #
    @property
    def users_ref(self):
        return self.db.collection("users")

    def create_or_update_user(self, user_info):
        user_with_email_ref = self.users_ref.where("email", "==", user_info["email"]).limit(1)
        user_with_email_doc = user_with_email_ref.get()
        user_data = {
            "email": user_info["email"],
            "given_name": user_info["given_name"],
            "family_name": user_info["family_name"],
            "profile_picture_url": user_info["picture"]
        }
        if len(user_with_email_doc) == 0:
            new_user_ref = self.users_ref.document()
            results = new_user_ref.set(user_data)
            print("New user has been created successfully")
        else:
            for doc in user_with_email_doc:
                doc_ref = self.users_ref.document(doc.id)
                results = doc_ref.update(user_data)
            print("User updated successfully")
        return user_data, results
    
    #
    # FUNDINGS
    #
    @property
    def fundings_ref(self):
        return self.db.collection("fundings")
    
    def fetch_fundings(self):
        fundings_ref = self.db.collection("fundings")
        documents = fundings_ref.stream()
        fields_to_lower = ['type']
        data_with_ids = []

        for document in documents:
            document_id = document.id
            document_data = {
                field: value.lower().replace("_", " ") if field in fields_to_lower and isinstance(value, str) else value
                for field, value in document.to_dict().items()
            }
            data_with_id = {'id': document_id, 'data': document_data}
            data_with_ids.append(data_with_id)

        return data_with_ids
    
    def fetch_funding_by_id(self, funding_id):
        funding_ref = self.fundings_ref.document(funding_id)
        funding_snapshot = funding_ref.get()
        funding_data = funding_snapshot.to_dict()
        data_with_id = {'id': funding_id, 'data': funding_data}
        return data_with_id

    def create_funding(self, funding):
        new_fundings_ref = self.fundings_ref.document()
        results = new_fundings_ref.set(funding)
        #print(results) #> {update_time: {seconds: 1648419942, nanos: 106452000}}
        return funding

    #
    # FUND TYPE
    #
    def fetch_fund_types(self):
        fund_type_ref = self.db.collection("fund_type")
        fund_types = [type.to_dict() for type in fund_type_ref.stream()]
        return fund_types
    
    def upload_to_bucket(self, fileName):
        destinationPath = f'fundings/{fileName}'
        sourceFilePath = os.path.join(
                current_app.root_path, 'static', 'images', 'fundhub', 'upload-temp', fileName
            )
        blob = self.bucket.blob(destinationPath)
        blob.upload_from_filename(sourceFilePath)
        blob.make_public()
        return blob.public_url

if __name__ == "__main__":


    service = FirebaseService()

    print("-----------")
    print("PRODUCTS...")
    products = service.fetch_products()
    pprint(products)

    print("-----------")
    print("ORDERS...")
    orders = service.fetch_orders()
    print(len(orders))

    print("-----------")
    print("NEW ORDER...")
    product = products[0]
    email_address = input("Email Address: ") or "hello@example.com"
    new_order, results = service.create_order(email_address, product)
    pprint(new_order)

    print("-----------")
    print("USER ORDERS...")
    user_orders = service.fetch_user_orders(email_address)
    print(len(user_orders))
