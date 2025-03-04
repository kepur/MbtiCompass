#coding"utf8
from flask import Blueprint

bp= Blueprint("main",__name__,)
from datetime import datetime
from flask import request, render_template

from app.main.csrf_form import NameForm


#获取浏览器信息
@bp.route('/')
def hello_world():
    user_agent=request.headers.get("User-Agent")
    return render_template('user.html',name=user_agent,current_time=datetime.utcnow())


#表单
@bp.route('/form/',methods=['GET','POST'])
def name_form():
    name=None
    form = NameForm()
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
    return render_template('form.html',form=form,name=name)


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500




