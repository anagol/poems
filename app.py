from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'anatolihalasny1969'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zfroyompsfsaol:7344da5ce14b9b93c2cbf71fce63aa5495c07df4aa630ace92cef9938a089516@ec2-54-217-236-206.eu-west-1.compute.amazonaws.com:5432/d8ifnmcve3nmpm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# ----------------------  Создаем базу данных -------------------------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(250))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r >' % self.username


class Verses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<Title %r >' % self.title


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pub_date = db.Column(db.DateTime(timezone=True), nullable=False, default=func.current_timestamp())
    name = db.Column(db.String(80))
    message = db.Column(db.Text)

    def __init__(self, name, message):
        self.name = name
        self.message = message

    def __repr__(self):
        return '<Name %r >' % self.name


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.errorhandler(401)
def page_not_found(error):
    return redirect(url_for('error_401'))


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
        db.session.flush()
        db.session.commit()
        return redirect(url_for('guest'))
    return render_template('guest.html', title='Гостевая книга', guest=guest)


#  --------------------Удаляем комментарии-----------------------------------------------------------------------------
@app.route('/guest_edit')
@login_required
def guest_edit():
    guest = Guest.query.all()
    return render_template('guest_edit.html', title='Редактируем гостевую книгу', guest=guest)


@app.route('/<int:id>/guest_delete', methods=('POST',))
@login_required
def guest_delete(id):
    guest = Guest.query.get_or_404(id)
    db.session.delete(guest)
    db.session.flush()
    db.session.commit()
    return redirect(url_for('guest_edit'))


#  --------------------Контакты----------------------------------------------------------------------------------------
@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты')


#  --------------------Админка-----------------------------------------------------------------------------------------
@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', title='Панель администратора')


#  --------------------Регистрация-------------------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password_hash = generate_password_hash(request.form["password"])
        register = User(username=username, password=password_hash)
        db.session.add(register)
        db.session.flush()
        db.session.commit()
        flash('Вы успешно зарегистрированы, теперь можете войти в систему!')
        return redirect(url_for("login"))
    return render_template("register.html", title='Регистрация')


#  --------------------Login-------------------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        login_user(user)
        if user is None:
            flash('Неверная пара логин - пароль')
            return render_template("login.html")
        if not check_password_hash(user.password, request.form['password']):
            flash('Неверная пара логин - пароль')
            return render_template("login.html")
        flash(f'Вы успешно авторизованы под именем {username}!')
        return redirect(url_for("admin"))

    return render_template("login.html")


#  --------------------Logout------------------------------------------------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#  --------------------Отдельная страница стиха------------------------------------------------------------------------
@app.route('/<int:verse_id>')
def verse(verse_id):
    verse = Verses.query.filter_by(id=verse_id).one()
    return render_template('verse.html', verse=verse)


#  --------------------Страница добавления стиха-----------------------------------------------------------------------
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        verse = Verses(title=title, content=content)
        db.session.add(verse)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('verses'))
    return render_template('create.html')


#  --------------------Страница редактирования стиха-------------------------------------------------------------------
@app.route('/verses_edit')
@login_required
def verses_edit():
    verses = Verses.query.all()
    return render_template('verses_edit.html', title='Редактируем', verses=verses)


#  --------------------Редактирем стих---------------------------------------------------------------------------------
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    verse = Verses.query.get_or_404(id)
    if request.method == 'POST':
        verse.title = request.form['title']
        verse.content = request.form['content']
        db.session.flush()
        db.session.commit()
        return redirect('/verses')
    else:
        return render_template('edit.html', verse=verse)


#  --------------------Удаляем стих------------------------------------------------------------------------------------
@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    verse = Verses.query.get_or_404(id)
    db.session.delete(verse)
    db.session.flush()
    db.session.commit()
    return redirect(url_for('verses'))


@app.route('/error_401')
def error_401():
    return render_template('401.html', title='ОШИБКА 401')


if __name__ == '__main__':
    app.run()
