from flask import render_template, url_for,redirect
from app.models.user_model import News

from flask import Blueprint
home=Blueprint('home',__name__)
#博客的首页
@home.route('/')
def index():
    news_list=News.query.filter_by(is_valid=1)
    return render_template('index.html',news_list=news_list)

#博客的类别
@home.route('/cat/<name>/')
def cat(name):
    #查询类别为name的数据
    news_list=News.query.filter(News.type==name)
    return render_template('cat.html',name=name,news_list=news_list)
#帖子详情页
@home.route('/detail/<int:pk>')
def detail(pk=None):
    if pk is None:
       pk=1

    #博客帖子详情页
    obj=News.query.get(pk)
    if not obj:
        return redirect(url_for('index'))
    return render_template('detail.html',obj=obj)

@home.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

@home.errorhandler(500)
def internal_server_error(e):
    return "服务器搬家了"

#数据库提交测试
# ew_obj = News(
#     title = '标题',
#     content = '内容',
#     type = '百家',
# )
# db.session.add(ew_obj)
# db.session.commit()

