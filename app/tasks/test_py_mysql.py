"""
create by khan.hozin {2018/12/4}
"""
__author__ = 'hozin'

import pymysql
class Pymsql_Search(object):
    def __init__(self):
        self.get_conn()
    def get_conn(self):
        try:
            self.connection = pymysql.connect(host='127.0.0.1',
                                     user='root',
                                     password='wolihi',
                                     db='news',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        except pymysql.cursors.err as e:
            print('Error %s'%e)

    def close_conn(self):
        try:
            if self.connection:
                self.connection.close()
        except pymysql.cursors.err as e:
            print("Error:%s"%e)


    def get_One(self):
        #准备SQL
        #找到cursor
        #值行sql
        #处理数据
        #关闭cursor连接
        sql = "SELECT * FROM `news` WHERE `types` =%s ORDER BY `created_at` DESC ;"
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                # sql = "SELECT  `*` FROM `news` ORDER BY `created_at` DESC"

                cursor.execute(sql,('推荐'))
                # print(cursor.rowcount)
                # print(dir(cursor))#查看使用功能
                rest=dict(zip([k[0] for k in cursor.description],cursor.fetchone()))
                # result = cursor.fetchone()
                # print(cursor.description)
                print(rest['title'])

        finally:
            cursor.close()
            self.close_conn()

    def get_more(self):
        sql = "SELECT * FROM `news` WHERE `types` =%s ORDER BY `created_at` DESC ;"
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                # sql = "SELECT  `*` FROM `news` ORDER BY `created_at` DESC"

                cursor.execute(sql, ('推荐'))
                # print(cursor.rowcount)
                # print(dir(cursor))#查看使用功能
                rest = [dict(zip([k[0] for k in cursor.description], row))
                        for row in  cursor.fetchall()]
                # result = cursor.fetchone()
                # print(cursor.description)
                # print(rest['title'])
                return rest
        finally:
            cursor.close()
            self.close_conn()

    def get_all(self,page,page_size): #增加分页功能
        '''分页查询数据'''
        offset=(page-1)*page_size
        #准备SQL
        sql='SELECT * FROM `news` WHERE `types`= %s ORDER BY `created_at` DESC LIMIT %s,%s'
        #找到cursor
        cursor=self.connection.cursor()
        #值行sql
        cursor.execute(sql,('百家'),offset,page_size)
        #拿到结果
        rest=[dict(zip([k[0] for k in cursor.description],row))
              for row in cursor.fetchall()]
        #处理数据

        #关闭cursor/连接
        cursor.close()
        self.close_conn()
        return rest
    def add_one(self):
        #准备SQL
        try:
            sql="INSERT INTO `news`(`title`,`content`,`types`,`image`,`is_valid`,`author`) VALUE (%s, %s, %s, %s, %s ,%s)"
                # sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"

            #获取连接和cursor
            cursor=self.connection.cursor()
            #值行sql
            cursor.execute(sql,('标题2','新闻内容','推荐','/static/img/news/07.png',1,'wolihi'))
            cursor.execute(sql,('标题5','新闻内容','推荐','/static/img/news/08.png',1,'wolihi'))
            self.connection.commit()
            #提交数据到数据库
            #提交事务
            #关闭cursor和连接
            cursor.close()
        except:
            print('error')
            self.connection.rollback() #如果有一条报错所有都回滚
        self.connection.close()

def main():
    obj=Pymsql_Search()
    # rest=obj.get_more()
    # # print(rest)
    # for item in rest:
    #     print(item)
    #     print('-----------')
    obj=Pymsql_Search()
    obj.add_one()
if __name__ == '__main__':
    main()
