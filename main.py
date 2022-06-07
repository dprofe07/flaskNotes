import sqlite3

from flask import Flask, render_template, url_for, request, redirect

from user import User

app = Flask(__name__)
db_name = 'static/users_db.db'
current_user = None
information = []


@app.route('/')
def index():
    return render_template('index.html', user=current_user, hide_home_link=True)


@app.route('/save', methods=['POST'])
def save():
    notes = request.form['notes']
    if current_user is not None:
        current_user.notes = notes
        current_user.write_to_db(db_name)
    return redirect('/', 301)


@app.route('/logout')
def logout():
    global current_user
    current_user = None
    return redirect('/', 301)


@app.route('/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']
    user = User.find_by_login(login, db_name)
    if user is not None:
        if password == user.password:
            global current_user
            current_user = user
            return redirect('/', 301)
        else:
            information.append({
                'forpage': 'auth',
                'small_text': f'Неверный пароль для пользователя "{login}"',
                'small_text_color': 'red',
                'login': login,
                'password': password,
            })
            return redirect('/auth', 301)
    else:
        information.append({
            'forpage': 'auth',
            'small_text': f'Пользователь с именем "{login}" не найден.',
            'small_text_color': 'red',
            'login': login,
            'password': password,
        })
        return redirect('/auth', 301)


@app.route('/auth')
def auth():
    dct = {}
    for i in range(len(information)):
        if information[i]['forpage'] == 'auth':
            dct = information[i]
            information.pop(i)
            break

    return render_template('auth.html', **dct)


@app.route('/create_account', methods=['POST'])
def create_account():
    login = request.form['login']
    password = request.form['password']
    information.append({
        'forpage': 'signup',
    })
    if User.find_by_login(login, db_name) is not None:
        information[-1].update({
            'small_text': f'Пользователь с именем "{login}" уже существует.',
            'small_text_color': 'red',
            'login': login,
        })
    else:
        user = User(login, password, '')
        user.write_to_db(db_name)

        global current_user
        current_user = user

        information[-1].update({
            'small_text': 'Вы успешно зарегистрированы',
            'small_text_color': 'dark-green',
            'redirect_timeout': 3000,
            'redirect_address': '/'
        })
    return redirect('/signup', 301)


@app.route('/signup')
def signup():
    dct = {}
    for i in range(len(information)):
        if information[i]['forpage'] == 'signup':
            dct = information[i]
            information.pop(i)
            break

    return render_template('singup.html', **dct)


if __name__ == '__main__':
    app.run(debug=True)
