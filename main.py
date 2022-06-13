import os

from flask import Flask, render_template, request, redirect, flash, make_response

from user import User, SERVER


app = Flask(__name__)


if SERVER:
    db_data = {
        'host': 'dprofe.mysql.pythonanywhere-services.com',
        'user': 'dprofe',
        'password': '',
        'database': 'dprofe$users',
    }
else:
    db_data = {
        'database': os.path.dirname(os.path.abspath(__file__)) + '/static/users_db.db'
    }

app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'


@app.route('/', methods=['GET', 'POST'])
def index():
    user = User.find_by_login(request.cookies.get('user_login'), db_data)
    return render_template('index.html', user=user, hide_home_link=True)


@app.route('/logout')
def logout():
    resp = redirect('/', 302)
    User.remove_from_cookies(resp)
    return resp


@app.route('/remove_account')
def remove_account():
    return render_template('remove_account.html')


@app.route('/remove_account_confirmed')
def remove_account_confirmed():
    user = User.get_from_cookies(request, db_data)
    resp = redirect('/', 302)
    if user is not None:
        user.remove_from_cookies(resp)
        user.remove_from_db(db_data)
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


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'GET':
        return render_template('change_password.html')
    else:
        old_password = request.form['old_password']
        password = request.form['password']
        password2 = request.form['password2']
        user = User.get_from_cookies(request, db_data)
        if user.password != old_password:
            flash('Старый пароль не верен', 'error')
            return render_template(
                'change_password.html',
                old_password=old_password, password=password, password2=password2
            )
        if password != password2:
            flash('Пароли не совпадают', 'error')
            return render_template(
                'change_password.html',
                old_password=old_password,
                password=password
            )

        user.password = password
        user.write_to_db(db_data)
        flash('Пароль успешно изменён', 'success')
        return render_template(
            'change_password.html'
        )


@app.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'GET':
        return render_template('password_recovery.html')
    else:
        login = request.form['login']
        keyword = request.form['keyword']

        user = User.find_by_login(login, db_data)
        if user is None:
            flash(f'Пользователь с логином "{login}" не найден', 'error')
            return render_template('password_recovery.html', login=login, keyword=keyword)
        if user.keyword != keyword:
            flash(f'Неверное ключевое слово', 'error')
            return render_template('password_recovery.html', login=login, keyword=keyword)
        password = user.password
        resp = make_response(render_template('password_recovery.html', login=login, keyword=keyword, password=password))
        user.save_to_cookies(resp)
        return resp


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
        keyword = request.form['keyword']

        if password != password2:
            flash(f'Пароли не совпадают', 'error')
            return render_template('singup.html', login=login, password=password)

        elif User.find_by_login(login, db_data) is not None:
            flash(f'Пользователь с именем "{login}" уже существует.', 'error')
            return render_template('singup.html', login=login, password=password, password2=password2)
        else:
            user = User(login, password, '', keyword)
            user.write_to_db(db_data)

            flash('Вы успешно зарегистрированы', 'success')

            resp = make_response(render_template('singup.html', redirect_timeout=1000, redirect_address='/'))
            User.save_to_cookies(user, resp)
            return resp
    else:
        return render_template('singup.html')


if __name__ == '__main__':
    app.run(port=5000, debug=not SERVER)
