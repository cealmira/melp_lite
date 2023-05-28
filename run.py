from flask import Flask, request, json, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_wtf import FlaskForm
import os.path
from datetime import datetime
import hashlib
import numpy as np

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()

# database configuration
app = Flask(__name__)

# name  of the sqlite db
db_name = 'melp.db'

# note - path is necessary for a SQLite db!!!
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JSON_AS_ASCII'] = False
db.init_app(app)

# instance of the table restaurants
class Restaurants(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Text, primary_key=True, nullable=False) 
    rating = db.Column(db.Integer)
    name = db.Column(db.Text)
    site = db.Column(db.Text)
    email = db.Column(db.Text)
    phone = db.Column(db.Text)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __init__(self, id, rating, name, site, email, phone, street, city, state, lat, lng):
        self.id = id
        self.rating = rating
        self.name = name
        self.site = site
        self.email = email
        self.phone = phone
        self.street = street
        self.city = city
        self.state = state
        self.lat = lat
        self.lng = lng

def checkFormData(id, rating, name, site, email, phone, street, city, state, lat, lng):
    # check if the variables are correct
    isCorrect = True
    msg = []

    # we want rating to be a number bewtween 0-4
    if rating != None:
        try :
            ratingI = int(rating)
            if ratingI > 4 or ratingI < 0:
                msg.append("rating out of bounds!")
                isCorrect = False
        except:
            isCorrect = False
    else:
        isCorrect = False

    # the name must not be empty
    if name == None:
        msg.append("name is missing!")
        isCorrect = False

    # also latitude must be in the range(-90,90)
    if lat != None:
        try :
            latI = float(lat)
            if latI > 90 or latI < -90:
                msg.append("lat out of bounds!")
                isCorrect = False
        except:
            isCorrect = False
    else:
        isCorrect = False

    # longitude must be in the range(-180,180)
    if lng != None:
        try :
            lngI = float(lng)
            if lngI > 180 or lngI < -180:
                msg.append("lng out of bounds!")
                isCorrect = False
        except:
            isCorrect = False
    else:
        isCorrect = False

    # the return is a variable that contains if the variables are in the 
    # appropriate range and if not the appropriate messages 
    val = {"isCorrect": isCorrect, "message": msg}
    return val


@app.route('/restaurants', methods=["GET"])
def restaurants_get():
    # GET handler for restaurants
    # if an id is provided the restaurant is resturned
    # otherwise all restaurans are returned
    id = request.form.get("id")
    restaurant = Restaurants.query.filter(Restaurants.id == id).first()
    if restaurant != None:
        obj = {
            'id': restaurant.id,
            'rating': restaurant.rating,
            'name': restaurant.name,
            'site': restaurant.site,
            'email': restaurant.email,
            'phone': restaurant.phone,
            'street': restaurant.street,
            'city': restaurant.city,
            'state': restaurant.state,
            'lat': restaurant.lat,
            'lng': restaurant.lng
        }
        json_string = json.dumps(obj, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    # we select all restaurants from the database
    lst = [] 
    all = db.session.execute(db.select(Restaurants).order_by(Restaurants.rating))
    for ele in all:
        row = ele[0]
        obj = {
            'id': row.id,
            'rating': row.rating,
            'name': row.name,
            'site': row.site,
            'email': row.email,
            'phone': row.phone,
            'street': row.street,
            'city': row.city,
            'state': row.state,
            'lat': row.lat,
            'lng': row.lng
        }
        lst.append(obj)
        
    # a json is returned in unicode
    data = { "restaurants" : lst}
    json_string = json.dumps(data, ensure_ascii = False)
    response = Response(json_string,content_type="application/json; charset=utf-8" )
    return response

@app.route('/restaurants', methods=["POST"])
def restaurants_post():
    # Post handler to add new data
    obj = {
        'id': None,
        'rating': None,
        'name': None,
        'site': None,
        'email': None,
        'phone': None,
        'street': None,
        'city': None,
        'state': None,
        'lat': None,
        'lng': None
    }

    # all parameters are captured
    keysList = list(obj.keys())
    for i in request.form:
        if i in keysList:
            obj[i] = request.form[i]
    
    val = checkFormData(obj['id'], obj['rating'], obj['name'], obj['site'], obj['email'], 
        obj['phone'], obj['street'], obj['city'], obj['state'], obj['lat'], obj['lng'])

    if not val['isCorrect']:
        json_string = json.dumps(val, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    # for the id we create a hash using the name and the current date
    now = datetime.now()
    hashcode = str(now) + obj['name']
    hashcode = hashcode.encode()
    obj['id'] = hashlib.md5(hashcode).hexdigest()

    # the new restaurant is added
    new_data = Restaurants(obj['id'], obj['rating'], obj['name'], obj['site'], obj['email'], 
        obj['phone'], obj['street'], obj['city'], obj['state'], obj['lat'], obj['lng'])
    db.session.add(new_data)
    db.session.commit()

    # a json is returned in unicode
    json_string = json.dumps(obj, ensure_ascii = False)
    response = Response(json_string,content_type="application/json; charset=utf-8" )
    return response

@app.route('/restaurants', methods=["PUT"])
def restaurants_put():
    # put handler to modify data
    # an id has to be provided, so if it is not found the error message will be sent
    id = request.form.get("id")
    if id == None:
        json_string = json.dumps({"message":"No id provided"}, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    # if the id does not belong to any record then an error message is sent
    restaurant = Restaurants.query.filter(Restaurants.id == id).first()
    if restaurant == None:
        json_string = json.dumps({"message":"No restaurant found with the provided id"}, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    # the data prior to the modification is obtained and then updated
    obj = {
        'id': restaurant.id,
        'rating': restaurant.rating,
        'name': restaurant.name,
        'site': restaurant.site,
        'email': restaurant.email,
        'phone': restaurant.phone,
        'street': restaurant.street,
        'city': restaurant.city,
        'state': restaurant.state,
        'lat': restaurant.lat,
        'lng': restaurant.lng
    }

    keysList = list(obj.keys())
    for i in request.form:
        if i in keysList:
            obj[i] = request.form[i]

    val = checkFormData(obj['id'], obj['rating'], obj['name'], obj['site'], obj['email'], 
        obj['phone'], obj['street'], obj['city'], obj['state'], obj['lat'], obj['lng'])

    if not val['isCorrect']:
        json_string = json.dumps(val, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response
    
    restaurant.rating = obj['rating']
    restaurant.name = obj['name']
    restaurant.site = obj['site']
    restaurant.email = obj['email']
    restaurant.phone = obj['phone']
    restaurant.street = obj['street']
    restaurant.city = obj['city']
    restaurant.state = obj['state']
    restaurant.lat = obj['lat']
    restaurant.lng = obj['lng']

    db.session.commit()

    # a json is returned in unicode
    json_string = json.dumps(obj, ensure_ascii = False)
    response = Response(json_string,content_type="application/json; charset=utf-8" )
    return response

@app.route('/restaurants', methods=["DELETE"])
def restaurants_delete():
    # delete handler
    # It is verified that there is an id in the parameters and that it belongs to a record.
    id = request.form.get("id")
    if id == None:
        json_string = json.dumps({"message":"No id provided"}, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    restaurant = Restaurants.query.filter(Restaurants.id == id).first()
    if restaurant == None:
        json_string = json.dumps({"message":"No restaurant found with the provided id"}, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    # the database record is deleted
    db.session.delete(restaurant)
    db.session.commit()

    # a json is returned in unicode
    json_string = json.dumps({"message": f"deleted {id}"}, ensure_ascii = False)
    response = Response(json_string,content_type="application/json; charset=utf-8" )
    return response


@app.route('/restaurants/statistics', methods=["GET"])
def restaurants_statistics():
    # handler to get the statistics of the restaurants
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    radius = request.args.get("radius")

    # a validation is done for the coordinates to be in correct range
    val = checkFormData(None, 1, 'a', None, None, 
        None, None, None, None, latitude, longitude)

    # otherwise an error message is sent
    if not val['isCorrect']:
        json_string = json.dumps(val, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response

    # the radius is validated
    radiusCorrect = True
    if radius != None:
        try :
            radiusI = float(radius)
            if radiusI <= 0:
                radiusCorrect = False
        except:
            radiusCorrect = False
    else:
        radiusCorrect = False

    if not radiusCorrect:
        json_string = json.dumps({"message": "Wrong radius"}, ensure_ascii = False)
        response = Response(json_string,content_type="application/json; charset=utf-8" )
        return response
    
    # the query below is used to get the distance in meters between the given coordinates and the ones in the database
    # to achive this we use postgis
    lst = [] 
    ratings = []
    query = text(f"SELECT name, rating, ST_DistanceSpheroid(ST_MakePoint({longitude}, {latitude}), ST_MakePoint(lng, lat)) from restaurants")
    all = db.session.execute(query)
    for i in all:
        if i[2] != None and i[2] <= radiusI:
            obj = {
                'name': i[0],
                'rating': i[1],
                'mts': i[2]
            }
            lst.append(obj)
            if i[1] != None:
                ratings.append(i[1])

    count = len(ratings)
    avg = 0
    std = 0

    # if there are restaurants inside the radius we use numpy for the mean end std
    if count > 0:
        avg = np.mean(ratings)
        std = np.std(ratings)

    # a json is returned in unicode
    data = {"count": count, "avg": avg, "std": std}
    json_string = json.dumps(data, ensure_ascii = False)
    response = Response(json_string,content_type="application/json; charset=utf-8" )
    return response


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=False)