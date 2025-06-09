import os
from peewee import *
from dotenv import load_dotenv

load_dotenv()

db = SqliteDatabase(os.getenv('DB_NAME', 'members.db'))

class BaseModel(Model):
    class Meta:
        database = db

class Member(BaseModel):
    user_id = IntegerField(unique=True)
    chat_id = IntegerField()
    name = CharField()
    address = CharField()
    birth_date = CharField()
    function = CharField()
    status = CharField(default='Ativo')
    registration_date = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    
    class Meta:
        table_name = 'members'

def initialize_db():
    db.connect()
    db.create_tables([Member], safe=True)
    db.close()

if __name__ == '__main__':
    initialize_db()