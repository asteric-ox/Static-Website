from app import app, mongo
from bson import ObjectId

def update_priests():
    with app.app_context():
        # Update Vicar
        mongo.db.parish_council.update_one(
            {"role": {"$in": ["Parish Priest", "Vicar"]}},
            {"$set": {
                "name": "Fr. Dr. Sebastian Panjikkaran",
                "role": "Vicar",
                "image_url": "/static/images/panji.jpg"
            }}
        )
        # Update Assistant Vicar
        mongo.db.parish_council.update_one(
            {"role": "Assistant Vicar"},
            {"$set": {
                "name": "Fr. Jeril James",
                "role": "Assistant Vicar",
                "image_url": "/static/images/jeril.jpg"
            }}
        )
        print("Priest details updated in database.")

if __name__ == "__main__":
    update_priests()
