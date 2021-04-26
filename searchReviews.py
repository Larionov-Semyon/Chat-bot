import sqlite3
conn = sqlite3.connect('reviews.sqlite')
cur = conn.cursor()
# вывод всех отзывов для указанных региона и тематики
def printAll(region, topic):
    cur.execute('''
    SELECT NCOs.name, Reviews.review FROM NCOs JOIN Reviews JOIN Regions JOIN Cities JOIN Topics ON NCOs.id = Reviews.nco_id AND Regions.id = Reviews.region_id AND Cities.id = Reviews.city_id AND Topics.id = Reviews.topic_id WHERE Regions.name = ? AND Topics.name = ? ORDER BY NCOs.name
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
    SELECT NCOs.name FROM NCOs JOIN Reviews JOIN Regions JOIN Cities JOIN Topics ON NCOs.id = Reviews.nco_id AND Regions.id = Reviews.region_id AND Cities.id = Reviews.city_id AND Topics.id = Reviews.topic_id WHERE Regions.name = ? AND Topics.name = ?
    ''', (region, topic) )
    result = cur.fetchall()
    lresult = list()
    for nco in result:
        lresult.append(nco[0])
    print(lresult)

def adaptiveSearch(nco, region, city, topic):
    conn = sqlite3.connect('reviews.sqlite')
    cur = conn.cursor()
    if len(region) > 0 or len (city) > 0 or len(topic) > 0:
        if len(nco) > 0:
            cur.execute('''
            SELECT NCOs.name, Reviews.review FROM NCOs JOIN Reviews JOIN Regions JOIN Cities JOIN Topics ON NCOs.id = Reviews.nco_id AND Regions.id = Reviews.region_id AND Cities.id = Reviews.city_id AND Topics.id = Reviews.topic_id WHERE CASE WHEN ? = "" THEN TRUE ELSE Regions.name = ? END AND CASE WHEN ? = "" THEN TRUE ELSE Cities.name = ? END AND CASE WHEN ? = "" THEN TRUE ELSE Topics.name = ? END
            ''', (region, region, city, city, topic, topic) )
            result = cur.fetchall()
            sresult = '\n Отзывы организации {}: \n'.format(nco)
            k = 1
            for nco_ in result:
                if k > 0:
                    k = 0
                # else:
                    # sresult += '\n'
                if nco_[0] == nco:
                    sresult += '\n -- ' + nco_[1] + '\n'
                # sresult += " + ".join(nco)
        else:
            cur.execute('''
            SELECT NCOs.name FROM NCOs JOIN Reviews JOIN Regions JOIN Cities JOIN Topics ON NCOs.id = Reviews.nco_id AND Regions.id = Reviews.region_id AND Cities.id = Reviews.city_id AND Topics.id = Reviews.topic_id WHERE CASE WHEN ? = "" THEN TRUE ELSE Regions.name = ? END AND CASE WHEN ? = "" THEN TRUE ELSE Cities.name = ? END AND CASE WHEN ? = "" THEN TRUE ELSE Topics.name = ? END
            ''', (region, region, city, city, topic, topic) )
            result = cur.fetchall()
            sresult = ''
            k = 1
            for nco in result:
                if k > 0:
                    k = 0
                else:
                    sresult += '\n'
                sresult += nco[0]
        return sresult
    else:
        return'Укажите регион и/или город и/или тематику'


if __name__ == '__main__':
    # глобальные переменные для введённых региона и тематики
    g_nco = input('Укажите НКО, если известно: ')
    g_region = input('Укажите ваш регион: ')
    g_city = input('Укажите ваш город: ')
    g_topic = input('Укажите тематику отзыва: ')

    adaptiveSearch(g_nco, g_region, g_city, g_topic)
