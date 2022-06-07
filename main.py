from flask import Flask, render_template, request, redirect, flash

from user import User

app = Flask(__name__)
db_name = 'static/users_db.db'
app.config['current_user'] = None
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        app.config['current_user'] = None
    return render_template('index.html', user=app.config['current_user'], hide_home_link=True)


@app.route('/save', methods=['POST'])
def save():
    notes = request.form['notes']
    if app.config['current_user'] is not None:
        app.config['current_user'].notes = notes
        app.config['current_user'].write_to_db(db_name)
    return redirect('/', 301)


@app.errorhandler(404)
def err404(e):
    return render_template('error.html', error_message='Страница не найдена')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if app.config['current_user'] is not None:
        return redirect('/', 301)
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.find_by_login(login, db_name)
        if user is not None:
            if password == user.password:
                app.config['current_user'] = user
                flash('Вы успешно вошли', 'success')
                return render_template('auth.html', redirect_timeout=1000, redirect_address='/')
            else:
                flash(f'Неверный пароль для пользователя "{login}"', 'error')
                return render_template('auth.html', login=login, password=password)
        else:
            flash(f'Пользователь с именем "{login}" не найден.', 'error')
            return render_template('auth.html', login=login, password=password)
    else:
        return render_template('auth.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash(f'Пароли не совпадают', 'error')
            return render_template('singup.html', login=login, password=password)

        elif User.find_by_login(login, db_name) is not None:
            flash(f'Пользователь с именем "{login}" уже существует.', 'error')
            return render_template('singup.html', login=login, password=password, password2=password2)

        else:
            user = User(login, password, '')
            user.write_to_db(db_name)

            app.config['current_user'] = user

            flash('Вы успешно зарегистрированы', 'success')
            return render_template('singup.html', redirect_timeout=1000, redirect_address='/')
    else:
        return render_template('singup.html')


if __name__ == '__main__':
    app.run('192.168.0.200', 5000, True)
