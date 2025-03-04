from flask_script import Manager
from app import db
from app import blogs

from flask_migrate import Migrate
magrate = Migrate(blogs,db)

manage=Manager(blogs)
manage.add_command('db',Migrate)

@manage.command()
def init_databases():
    db.drop_all()
    db.create_all()



