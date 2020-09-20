from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256


app = Flask(__name__)
app.config['SECRET_KEY'] = 'anatolihalasny1969'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


class Verses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(80))
    message = db.Column(db.Text)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Главная')


@app.route('/verses')
def verses():
    verses = Verses.query.all()
    return render_template('verses.html', title='Стихи', verses=verses)


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')


@app.route('/guest', methods=['GET', 'POST'])
def guest():
    guest = Guest.query.all()
    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]
        guest = Guest(name=name, message=message)
        db.session.add(guest)
        db.session.commit()
        return redirect(url_for('guest'))
    return render_template('guest.html', title='Гостевая книга', guest=guest)


# @app.route('/guest_book', methods=['GET', 'POST'])
# def guest_book():
#     if request.method == "POST":
#         name = request.form["name"]
#         message = request.form["message"]
#         guest = Guest(name=name, message=message)
#         db.session.add(guest)
#         db.session.commit()
#         return redirect(url_for('guest'))
#     return render_template('guest.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты')


@app.route('/admin')
def admin():
    return render_template('admin.html', title='Панель администратора')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        login = User.query.filter_by(email=email, password=password).first()
        if login is not None:
            return redirect(url_for("create"))
        else:
            flash('Что-то не так!')
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = pbkdf2_sha256.hash(request.form["password"])
        register = User(email=email, password=password)
        db.session.add(register)
        db.session.commit()
        flash('Вы успешно зарегистрированы, теперь можете войти в систему!')
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/<int:verse_id>')
def verse(verse_id):
    verse = Verses.query.filter_by(id=verse_id).one()
    return render_template('verse.html', verse=verse)


@app.route('/create', methods=['GET', 'POST'])
# @login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        verse = Verses(title=title, content=content)

        db.session.add(verse)
        db.session.commit()
        return redirect(url_for('verses'))
    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    verse = Verses.query.get_or_404(id)
    if request.method == 'POST':
        verse.title = request.form['title']
        verse.content = request.form['content']
        db.session.commit()
        return redirect('/verses')
    else:
        return render_template('edit.html', verse=verse)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    verse = Verses.query.get_or_404(id)
    db.session.delete(verse)
    db.session.commit()
    return redirect(url_for('verses'))


if __name__ == '__main__':
    app.run()
