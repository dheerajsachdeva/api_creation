from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def get_random_cafe():
    response = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(response)
    return jsonify(cafe=random_cafe.to_dict())
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })


@app.route("/all")
def get_all_cafes():
    response = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    all_cafes = response
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    

@app.route("/search")
def get_cafe_at_location():
    query = request.args.get("loc")
    response = db.session.execute(db.select(Cafe).where(Cafe.location == query)).scalars().all()
    all_cafes = response
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not found: We don't found cafe at this location"}), 404
## HTTP GET - Read Record

## HTTP POST - Create Record
@app.route('/add', method=["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"Success": "New cafe added successfully."})

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', method=["PATCH"])
def patch_cafe(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response = {"Success": "Price successfully updated"}), 200
    else:
        return jsonify(response = {"Failed": "Not found"}), 404


## HTTP DELETE - Delete Record

@app.route("/delete_cafe/<int:cafe_id>", method=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "SECRET_KEY":
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response = {"Success": "Cafe deleted successfully"}), 200
        else:
            return jsonify(response={"Failed": "Not found"}), 404
    else:
        return jsonify(response={"Forbidden": "KEY Not found"}), 403

if __name__ == '__main__':
    app.run(debug=True)
