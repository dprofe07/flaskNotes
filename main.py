from flask import Flask, render_template, request, redirect, flash, make_response

from user import User, SERVER


app = Flask(__name__)
# hahaha
if SERVER:
    db_data = {
        'host': 'dprofe.mysql.pythonanywhere-services.com',
        'user': 'dprofe',
        'password': '<HIDDEN>',
        'database': 'dprofe$users',
    }
else:
    db_data = {
        'database': 'static/users_db.db'
    }
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'


@app.route('/', methods=['GET', 'POST'])
def index():
    if False:
        global expire_user
        if request.method == 'POST':
            resp = make_response()
            expire_user = request.cookies.get('user_login')
            User.remove_from_cookies(resp)

            return resp
        else:
            print('NOT NONE')

            print('USER:', user)
            try:
                if user.login == expire_user:
                    expire_user = ''
                    return redirect('/', 301)
            except AttributeError:
                pass
            resp = make_response(render_template('index.html', user=user, hide_home_link=True))
            return resp

    user = User.find_by_login(request.cookies.get('user_login'), db_data)
    return render_template('index.html', user=user, hide_home_link=True)


@app.route('/logout')
def logout():
    resp = redirect('/', 302)
    User.remove_from_cookies(resp)
    return resp


@app.route('/save', methods=['POST'])
def save():
    notes = request.form['notes']
    login = request.cookies.get('user_login')
    if login is not None:
        user = User.find_by_login(login, db_data)
        user.notes = notes
        user.write_to_db(db_data)

    return redirect('/', 302)


@app.errorhandler(404)
def err404(e):
    return render_template('error.html', error_message='Страница не найдена')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.cookies.get('user_login') is not None:
        return redirect('/', 302)
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.find_by_login(login, db_data)
        if user is not None:
            if password == user.password:
                flash('Вы успешно вошли', 'success')

                resp = make_response(render_template('auth.html', redirect_timeout=1000, redirect_address='/'))
                User.save_to_cookies(user, resp)

                return resp
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
    if request.cookies.get('user_login') is not None:
        return redirect('/', 302)
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash(f'Пароли не совпадают', 'error')
            return render_template('singup.html', login=login, password=password)

        elif User.find_by_login(login, db_data) is not None:
            flash(f'Пользователь с именем "{login}" уже существует.', 'error')
            return render_template('singup.html', login=login, password=password, password2=password2)

        else:
            user = User(login, password, '')
            user.write_to_db(db_data)

            flash('Вы успешно зарегистрированы', 'success')

            resp = make_response(render_template('singup.html', redirect_timeout=1000, redirect_address='/'))
            User.save_to_cookies(user, resp)
            return resp
    else:
        return render_template('singup.html')


if __name__ == '__main__':
    app.run('192.168.0.200', 5000, not SERVER)
