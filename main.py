import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask("Api")
app.config['SECRET_KEY'] = 'secret'

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tererium.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class TereriumData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snake = db.Column(db.String(50), nullable=False)
    temp = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(100), nullable=False)


db.create_all()


@app.route("/sensors", methods=["POST"])
def sensors():
    json_data = request.get_json(force=True)
    data = json.loads(json_data)

    new_entry = TereriumData(
        snake=data["Snake"],
        temp=data["Temp"],
        date=data["Data"],
    )
    db.session.add(new_entry)
    db.session.commit()
    return data


@app.route("/staty")
def staty():
    pass


app.run(debug=True)
