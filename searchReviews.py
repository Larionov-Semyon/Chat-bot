import sqlite3
conn = sqlite3.connect('reviews.sqlite')
cur = conn.cursor()
# вывод всех отзывов для указанных региона и тематики
def printAll(region, topic):
    cur.execute('''
    SELECT NCOs.name, Reviews.review FROM NCOs JOIN Reviews JOIN Regions JOIN Topics ON NCOs.id = Reviews.nco_id AND Regions.id = Reviews.region_id AND Topics.id = Reviews.topic_id WHERE Regions.name = ? AND Topics.name = ? ORDER BY NCOs.name
    ''', (region, topic) )
    result = cur.fetchall()

    print(f'Найдено {len(result)} отзывов:')
    n = 1
    for rev in result:
        print(f'{n})НКО: {rev[0]} | Отзыв: {rev[1]}')
        n += 1
    
# вывод всех НКО для указанных региона и тематики
def printNCOs(region, topic):
    cur.execute('''
    SELECT NCOs.name FROM NCOs JOIN Reviews JOIN Regions JOIN Topics ON NCOs.id = Reviews.nco_id AND Regions.id = Reviews.region_id AND Topics.id = Reviews.topic_id WHERE Regions.name = ? AND Topics.name = ?
    ''', (region, topic) )
    result = cur.fetchall()
    lresult = list()
    for nco in result:
        lresult.append(nco[0])
    print(lresult)


if __name__ == '__main__':
    # глобальные переменные для введённых региона и тематики
    g_region = input('Укажите ваш регион: ')
    g_topic = input('Укажите тематику отзыва: ')

printNCOs(g_region, g_topic)