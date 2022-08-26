import sqlite3


def sql_start():
    global base, cur
    base = sqlite3.connect("users.db")
    cur = base.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id PRIMARY KEY, user_name TEXT, promise TEXT, deadline date )")
    base.commit()


def promise_check(user_id):
    cur.execute(f"SELECT promise, deadline FROM users where user_id ={user_id}")
    results= cur.fetchall()
    for i in results:
        promise = str(i[0])
        deadline = str(i[1])
    return promise, deadline

async def sql_add(data):
    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", [data['user_id'], data['user_name'], data['promise'], data['deadline']])
    base.commit()



def all_users():
    cur.execute("SELECT user_id from users ")
    return cur.fetchall()



def sql_delete(user_id):
    cur.execute(f"DELETE from users WHERE user_id ={user_id}")
    base.commit()




def check_user(user_id):
    cur.execute(f"SELECT * FROM users where user_id ={user_id}")
    res=cur.fetchone()
    return res