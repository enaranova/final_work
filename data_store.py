import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker
from config import db_url_object

DSN = db_url_object

Base = declarative_base()

class Vkinder_viewed_id(Base):
    """Создание таблицы для записи просмотренных id"""
    __tablename__ = "vkinder_viewed_id"
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, nullable=False)
    viewed_id = sq.Column(sq.Integer, unique=True)

    """Переопределение print для читаемого вывода"""
    def __str__(self) -> str:
        return (f"таблица 'vkinder_viewed_id': id = {self.id} | "
                f"user_id = {self.user_id} | "
                f"viewed_id = {self.viewed_id}")

"""Функция для создания таблиц"""
def create_tables(engine):
    Base.metadata.create_all(engine)

"""Функция для создания новой записи в таблице Vkinder_viewed_id"""
def insert_data(user_id, viewed_id):
    new_record = Vkinder_viewed_id(
        user_id = user_id,
        viewed_id = viewed_id
    )
    session.add(new_record)
    session.commit()

engine = sq.create_engine(DSN)
create_tables(engine)

"""Создание сессиий для работы с БД"""
Session = sessionmaker(bind=engine)
session = Session()

# """Построчный вывод данных таблицы Vkinder_viewed_id"""
# for item in session.query(Vkinder_viewed_id):
#     print(item)

