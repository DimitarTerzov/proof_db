import sqlite3

def get_db_data():
    database_connection = sqlite3.connect('C:/sqlite/proof_db/proof.db')
    db_data = None
    with database_connection:
        cursor = database_connection.cursor()
        query = 'SELECT * FROM proof'
        db_data = cursor.execute(query)
        db_data = db_data.fetchall()

    return db_data


def update_db(id_, column, value):
    database_connection = sqlite3.connect('proof.db')
    with database_connection:
        cursor = database_connection.cursor()
        query = 'UPDATE proof SET \"{0}\"=? WHERE Id=?'.format(column)
        cursor.execute(query, (value, id_))

