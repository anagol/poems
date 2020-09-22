from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'anatolihalasny1969'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


# ----------------------  Создаем базу данных -------------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120))
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


#  --------------------Домашняя страница-------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Главная')


#  --------------------Страница со списком стихов----------------------------------------------------------------------
@app.route('/verses')
def verses():
    verses = Verses.query.all()
    return render_template('verses.html', title='Стихи', verses=verses)


#  --------------------Страница об авторе------------------------------------------------------------------------------
@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')


#  --------------------Гостевая книга----------------------------------------------------------------------------------
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


#  --------------------Удаляем комментарии-----------------------------------------------------------------------------
@app.route('/guest_edit')
def guest_edit():
    guest = Guest.query.all()
    return render_template('guest_edit.html', title='Редактируем гостевую книгу', guest=guest)


@app.route('/<int:id>/guest_delete', methods=('POST',))
def guest_delete(id):
    guest = Guest.query.get_or_404(id)
    db.session.delete(guest)
    db.session.commit()
    return redirect(url_for('guest_edit'))


#  --------------------Контакты----------------------------------------------------------------------------------------
@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты')


#  --------------------Админка-----------------------------------------------------------------------------------------
@app.route('/admin')
# @login_required
def admin():
    return render_template('admin.html', title='Панель администратора')


#  --------------------Login-------------------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Неверная пара')
            return render_template("login.html")
        if not check_password_hash(user.password, request.form['password']):
            flash('Неверная пара')
            return render_template("login.html")
        return redirect(url_for("admin"))
    return render_template("login.html")


#  --------------------Регистрация-------------------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password_hash = generate_password_hash(request.form["password"])
        register = User(username=username, password=password_hash)
        db.session.add(register)
        db.session.commit()
        flash('Вы успешно зарегистрированы, теперь можете войти в систему!')
        return redirect(url_for("login"))
    return render_template("register.html", title='Регистрация')


#  --------------------Отдельная страница стиха------------------------------------------------------------------------
@app.route('/<int:verse_id>')
def verse(verse_id):
    verse = Verses.query.filter_by(id=verse_id).one()
    return render_template('verse.html', verse=verse)


#  --------------------Страница добавления стиха-----------------------------------------------------------------------
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


#  --------------------Страница редактирования стиха-------------------------------------------------------------------
@app.route('/verses_edit')
def verses_edit():
    verses = Verses.query.all()
    return render_template('verses_edit.html', title='Редактируем', verses=verses)


#  --------------------Редактирем стих---------------------------------------------------------------------------------
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


#  --------------------Удаляем стих------------------------------------------------------------------------------------
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    verse = Verses.query.get_or_404(id)
    db.session.delete(verse)
    db.session.commit()
    return redirect(url_for('verses'))


if __name__ == '__main__':
    app.run()
