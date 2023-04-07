import sqlite3

class UserDB:
  def __init__(self):
    self.conn = sqlite3.connect("bot.db")
    self.cursor = self.conn.cursor()
    self.cursor.execute('''
  CREATE TABLE IF NOT EXISTS auto_answer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE,
    answer TEXT
  )
''')
    self.conn.commit()

  def get_all_words(self):
    self.cursor.execute("SELECT * FROM auto_answer")
    return self.cursor.fetchall()

  def add_word(self, word, answer):
    self.cursor.execute("INSERT INTO auto_answer (word, answer) VALUES (?,?)", (word,answer))
    self.conn.commit()
    return True

  def get_word(self, word="", id=0):
    if word:
      self.cursor.execute("SELECT * FROM auto_answer WHERE word=?", (word,))
    else:
      self.cursor.execute("SELECT * FROM auto_answer WHERE id=?", (id,))
    return self.cursor.fetchall()

  def del_word(self, word="", id=0):
    if word:
      self.cursor.execute("DELETE FROM auto_answer WHERE word=?", (word,))
    else:
      self.cursor.execute("DELETE FROM auto_answer WHERE id=?", (id,))
    self.conn.commit()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.conn.commit()
    if self.conn:
      self.conn.close()