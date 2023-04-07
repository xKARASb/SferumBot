import sys
#sys.path.append("D:\works\coding\python\sferum\\")


from models.db import create_db, Session
from models.user import User


def create_database(load_fake_data: bool = True):
    create_db()
    if load_fake_data:
        _load_fake_data(Session())


def _load_fake_data(session: Session):
    user = User(0000000, "434234234235145345", 2000000001, -1001917922644)

    session.add(user)

    session.commit()
    session.close()