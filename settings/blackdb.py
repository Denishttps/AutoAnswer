import sqlite3

class BlackListDB:
  def __init__(self):
    self.conn = sqlite3.connect("bot.db")
    self.cursor = self.conn.cursor()
    self.cursor.execute('''
  CREATE TABLE IF NOT EXISTS black_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    first_name TEXT,
    username TEXT
  )
''')
    self.conn.commit()

  def get_all_users(self):
    self.cursor.execute("SELECT * FROM black_list")
    return self.cursor.fetchall()

  def get_user(self, id=0, user_id=0):
    if user_id:
      self.cursor.execute("SELECT EXISTS(SELECT 1 FROM black_list WHERE user_id=?)", (user_id,))
    else:
      self.cursor.execute("SELECT EXISTS(SELECT 1 FROM black_list WHERE user_id=?)", (user_id,))
    return self.cursor.fetchone()[0] 

  def add_user(self, user_id, first_name, username):
    self.cursor.execute("INSERT INTO black_list (user_id, first_name, username) VALUES (?,?,?)", (user_id, first_name, username))
    self.conn.commit()
    return True

  def del_user(self, user_id=0, id=0):
    if user_id:
      self.cursor.execute("DELETE FROM black_list WHERE user_id=?", (user_id,))
    else:
      self.cursor.execute("DELETE FROM black_list WHERE id=?", (id,))
    self.conn.commit()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.conn.commit()
    if self.conn:
      self.conn.close()