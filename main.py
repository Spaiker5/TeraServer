import io
import json
from functools import wraps

from flask import request, Flask, render_template, redirect, Response, flash, url_for, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, logout_user
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from matplotlib.figure import Figure
from matplotlib_inline.backend_inline import FigureCanvas
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, RegisterForm

app = Flask("Api")
app.config['SECRET_KEY'] = 'secret'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tererium.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


# USER TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(50), nullable=False)


# CONFIGURE TABLE
class Snake(db.Model):
    __tablename__ = "snake"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(50), nullable=False)
    temp = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(100), nullable=False)


db.create_all()


@app.route("/sensors", methods=["POST"])
def sensors():
    json_data = request.get_json(force=True)
    data = json.loads(json_data)

    new_entry = Snake(
        name=data["Snake"],
        temp=data["Temp"],
        date=data["Data"],
        owner_id=data["Owner_ID"]
    )
    db.session.add(new_entry)
    db.session.commit()
    return data


@app.route("/")
def welcome_page():
    # TODO: All name's overview.
    return render_template("main.html")

@app.route("/test")
def test():
    # TODO: All name's overview.
    return render_template("dashboard.html")

@app.route("/list")
@login_required
def lista():
    user_id = current_user.id
    snakes = Snake.query.filter(Snake.owner_id == user_id).order_by(Snake.date.desc())
    return render_template("list.html", snakes=snakes)


@app.route("/snakes")
@login_required
def all_snakes():
    user_id = current_user.id
    snakes = Snake.query.filter(Snake.owner_id == user_id)

    return render_template("snakes.html", snakes=snakes)


@app.route("/snake/<name>")
@login_required
def snake_select_name(name):
    user_id = current_user.id
    query = Snake.query.filter(Snake.name == name).order_by(Snake.id.desc()).first()
    if query.owner_id == user_id:
        return render_template("single_overview.html", temp=query.temp, date=query.date, snake=name)
    else:
        flash("Nie znaleziono węża o takim imieniu.")
        return redirect(url_for('welcome_page'))


@app.route("/snake/<snake_id>")
@login_required
def snake_select_id(snake_id):
    user_id = current_user.id
    query = Snake.query.filter(Snake.id == snake_id)
    print(query.id)
    if query.owner_id == user_id:
        return render_template("single_overview.html", temp=query.temp, date=query.date, snake=query.name)
    else:
        return flash("Nie znaleziono węża o takim ID.")


@app.route("/<name>/plot.png")
def plot_png(name):
    fig = Figure(figsize=[7, 3], facecolor="#f5700c", edgecolor="#f5700c")
    ax = fig.subplots()
    ax.patch.set_facecolor("#f5700c")

    x = []
    y = []
    for date in Snake.query.filter(Snake.name == name).all():
        date = date.date

        x.append(date)
    for temp in Snake.query.filter(Snake.name == name).all():
        temp = temp.temp
        y.append(temp)

    ax.plot(x, y)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("staty"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('staty'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('staty'))


@app.route("/admin")
@admin_only
def admin():
    pass


app.run(debug=True)
