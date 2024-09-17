# database.py

import sqlite3

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(f'{self.db_name}.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            assigned_date TEXT,
            task TEXT,
            status TEXT,
            completion_date TEXT,
            issue TEXT,
            remark TEXT,
            test_result_path TEXT,
            assigned_to TEXT,
            priority TEXT,
            progress_percentage INTEGER
        )
        ''')
        self.conn.commit()

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()

    def insert_data(self, data):
        self.execute_query('''
        INSERT INTO tasks (assigned_date, task, status, completion_date, issue, remark, test_result_path, assigned_to, priority, progress_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)

    def update_data(self, data):
        self.execute_query('''
        UPDATE tasks
        SET assigned_date = ?, task = ?, status = ?, completion_date = ?, issue = ?, remark = ?, test_result_path = ?, assigned_to = ?, priority = ?, progress_percentage = ?
        WHERE id = ?
        ''', data)
        self.notify_change()

    def delete_data(self, task_id):
        self.execute_query('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.notify_change()

    def fetch_data(self):
        self.cursor.execute('SELECT * FROM tasks')
        return self.cursor.fetchall()

    def notify_change(self):
        pass

    def close(self):
        self.conn.close()
