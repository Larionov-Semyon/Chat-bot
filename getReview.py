import sqlite3

def StartDatabase(init):
    if(init == False):
        conn = sqlite3.connect('reviews.sqlite')
        cur = conn.cursor()
        print('Создание новой БД')
        cur.executescript('''
        DROP TABLE IF EXISTS NCOs;
        DROP TABLE IF EXISTS Reviews;
        DROP TABLE IF EXISTS Regions;
        DROP TABLE IF EXISTS Cities;
        DROP TABLE IF EXISTS Topics;
        CREATE TABLE NCOs (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE
        );
        CREATE TABLE Reviews (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        nco_id INTEGER,
        region_id INTEGER,
        city_id INTEGER,
        topic_id INTEGER,
        review TEXT NOT NULL
        );
        CREATE TABLE Regions (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE
        );
        CREATE TABLE Cities (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE
        );
        CREATE TABLE Topics (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE
        );''')

def uploadReview(nco, region, city, topic, review):
    conn = sqlite3.connect('reviews.sqlite')
    print(conn)
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO NCOs (name) VALUES (?)
        ''', (nco,))
    cur.execute('SELECT id FROM NCOs WHERE name = ?', (nco,))
    nco_id = cur.fetchone()[0]

    cur.execute('''
        INSERT OR IGNORE INTO Regions (name) VALUES (?)
        ''', (region,))
    cur.execute('SELECT id FROM Regions WHERE name = ?', (region,))
    region_id = cur.fetchone()[0]

    cur.execute('''
        INSERT OR IGNORE INTO Cities (name) VALUES (?)
        ''', (city,))
    cur.execute('SELECT id FROM Cities WHERE name = ?', (city,))
    city_id = cur.fetchone()[0]

    cur.execute('''
        INSERT OR IGNORE INTO Topics (name) VALUES (?)
        ''', (topic,))
    cur.execute('SELECT id FROM Topics WHERE name = ?', (topic,))
    topic_id = cur.fetchone()[0]

    cur.execute('''
        INSERT INTO Reviews (nco_id, region_id, city_id, topic_id, review) VALUES (?, ?, ?, ?, ?)
        ''', (nco_id, region_id, city_id, topic_id, review))
    conn.commit()

if __name__ == '__main__':
    # conn = sqlite3.connect('reviews.sqlite')

    nco = input('Укажите НКО, на которую хотите написать отзыв: ')
    region = input('Укажите ваш регион: ')
    topic = input('Укажите тематику отзыва: ')
    review = input('Ваш отзыв: ')
    init = input('Создать базу данны1х заново? ')
    uploadReview(nco, region, topic, review)
