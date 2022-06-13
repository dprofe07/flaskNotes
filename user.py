SERVER = True

if SERVER:
    from mysql import connector
else:
    import sqlite3 as connector


class User:
    def __init__(self, login, password, notes):
        self.login = login
        self.password = password
        self.notes = notes

    def write_to_db(self, db_data):
        User.create_table(db_data)
        db_conn = connector.connect(**db_data)
        cur = db_conn.cursor()
        if User.find_by_login(self.login, db_data) is None:
            cur.execute(f"insert into users values ('{self.login}', '{self.password}', '{self.notes}')")
        else:
            cur.execute(
                f"update users "
                f"set Password = '{self.password}', Notes = '{self.notes}' "
                f"where Login = '{self.login}'"
            )
        db_conn.commit()

    @staticmethod
    def get_list(db_data):
        User.create_table(db_data)
        db_conn = connector.connect(**db_data)
        cur = db_conn.cursor()
        cur.execute('SELECT * FROM users')
        res = []
        for u in cur.fetchall():
            res.append(User(*u))
        return res

    @staticmethod
    def find_by_login(login: str, db_data):
        User.create_table(db_data)
        for i in User.get_list(db_data):
            if i.login == login:
                return i
        return None

    @staticmethod
    def create_table(db_data):
        db_conn = connector.connect(**db_data)
        cur = db_conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                Login NVARCHAR(100) UNIQUE PRIMARY KEY NOT NULL,
                Password NVARCHAR(100) NOT NULL,
                Notes NVARCHAR(100)
            )
            """
        )

    @staticmethod
    def save_to_cookies(user, resp):
        resp.set_cookie('user_login', user.login, 60 * 60 * 24 * 365 * 100)
        # on 100 years

    @staticmethod
    def remove_from_cookies(resp):
        resp.set_cookie('user_login', '', 0)
        # on 0 seconds (expire and remove)


