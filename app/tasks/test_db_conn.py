import pymysql.cursors
import pymysql

# pymysql.install_as_MySQLdb()
connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='wolihi',
                             db='news',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
try:
    # with connection.cursor() as cursor:
    #     # Create a new record
    #     sql = "SELECT * FROM news ORDER BY created_at DESC"
    #     cursor.execute(sql, ('webmaster@python.org', 'very-secret'))
    #
    # # connection is not autocommit by default. So you must commit to save
    # # your changes.
    # connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
        # sql = "SELECT  `*` FROM `news` ORDER BY `created_at` DESC"
        sql = "SELECT * FROM `news`"
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
finally:
    connection.close()

