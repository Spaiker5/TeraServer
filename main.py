import io
import json

from flask import request, Flask, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from matplotlib.figure import Figure
from matplotlib_inline.backend_inline import FigureCanvas

app = Flask("Api")
app.config['SECRET_KEY'] = 'secret'

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tererium.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class TeraData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snake = db.Column(db.String(50), nullable=False)
    temp = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(100), nullable=False)


db.create_all()


@app.route("/sensors", methods=["POST"])
def sensors():
    json_data = request.get_json(force=True)
    data = json.loads(json_data)

    new_entry = TeraData(
        snake=data["Snake"],
        temp=data["Temp"],
        date=data["Data"],
    )
    db.session.add(new_entry)
    db.session.commit()
    return data


#
# @app.route("/")
# def staty():
#     for snake in TeraData.query.group_by(TeraData.snake).all():
#         query = TeraData.query.order_by(TeraData.id.desc()).first()
#         print(query)
#     return render_template("template.html", temp=query.temp, date=query.date)


@app.route("/name/<snake>")
def staty_snake(snake):
    query = TeraData.query.filter(TeraData.snake == snake).order_by(TeraData.id.desc()).first()
    return render_template("template.html", temp=query.temp, date=query.date, snake=snake)


@app.route('/plot.png')
def plot_png():
    fig = Figure(figsize=[7, 3], facecolor="#f5700c", edgecolor="#f5700c")
    ax = fig.subplots()
    ax.patch.set_facecolor("#f5700c")

    x = []
    y = []
    for date in TeraData.query.all():
        date = date.date
        x.append(date)
    for temp in TeraData.query.all():
        temp = temp.temp
        y.append(temp)

    # print(x, y, TeraData.query.all())
    ax.plot(x, y)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


app.run(debug=True)
