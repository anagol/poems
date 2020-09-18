import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'anatolihalasny1969'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_verse(verse_id):
    conn = get_db_connection()
    verse = conn.execute('SELECT * FROM verses WHERE id = ?', (verse_id,)).fetchone()
    conn.close()
    if verse is None:
        abort(404)
    return verse


def get_guest(guest_id):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE id = ?', (guest_id,)).fetchone()
    conn.close()
    if guest is None:
        abort(404)
    return guest


@app.route('/index')
def index():
    return render_template('index.html', title='Главная')


@app.route('/verses')
def verses():
    conn = get_db_connection()
    verse = conn.execute('SELECT * FROM verses').fetchall()
    conn.close()
    return render_template('verses.html', title='Стихи', verses=verse)


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')


@app.route('/guest')
def guest():
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests').fetchall()
    conn.close()
    return render_template('guest.html', title='Гостевая книга', guests=guest)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты')


@app.route('/admin')
def admin():
    return render_template('admin.html', title='Панель администратора')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Панель входа', form=form)


@app.route('/<int:verse_id>')
def verse(verse_id):
    verse = get_verse(verse_id)
    return render_template('verse.html', verse=verse)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Вы не ввели название стиха')

        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO verses (title, content) VALUES(?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('verses'))

    return render_template('create.html')


@app.route('/guest_book', methods=['GET', 'POST'])
def guest_book():
    if request.method == 'POST':
        guestname = request.form['guestname']
        messagecontent = request.form['messagecontent']

        if not guestname:
            flash('Вы не ввели имя!')

        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO guests (guestname, messagecontent) VALUES(?, ?)', (guestname, messagecontent))
            conn.commit()
            conn.close()
            return redirect(url_for('guest'))
    return render_template('guest.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    verse = get_verse(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Вы не ввели название стиха')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE verses SET title=?, content=?' ' WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('verses'))
    return render_template('edit.html', verse=verse)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    verse = get_verse(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM verses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Стих "{}" удален!'.format(verse['title']))
    return redirect(url_for('verses'))


if __name__ == '__main__':
    app.run()
