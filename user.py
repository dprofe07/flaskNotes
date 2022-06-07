import sqlite3


class User:
    def __init__(self, login, password, notes):
        self.login = login
        self.password = password
        self.notes = notes

    def write_to_db(self, db_name):
        db_conn = sqlite3.connect(db_name)
        cur = db_conn.cursor()
        if User.find_by_login(self.login, db_name) is None:
            cur.execute(f"insert into users values ('{self.login}', '{self.password}', '{self.notes}')")
        else:
            cur.execute(
                f"update users "
                f"set Password = '{self.password}', Notes = '{self.notes}' "
                f"where Login = '{self.login}'"
            )
        db_conn.commit()

    @staticmethod
    def get_list(db_name):
        db_conn = sqlite3.connect(db_name)
        cur = db_conn.cursor()
        cur.execute('SELECT * FROM users')
        res = []
        for u in cur.fetchall():
            res.append(User(*u))
        return res

    @staticmethod
    def find_by_login(login: str, db_name):
        for i in User.get_list(db_name):
            if i.login == login:
                return i
        return None
