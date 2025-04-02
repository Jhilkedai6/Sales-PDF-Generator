from sqlalchemy import Column, String, Integer, Date, Text
from database import Base


class GoogleUser(Base):

    __tablename__ = "goole_user"

    id = Column(Integer, index=True, primary_key=True)

    user_id = Column(Integer)
    user_email = Column(String)
    username = Column(String)
    user_pic = Column(String)
    first_logged_in = Column(Date)



class RoleTable(Base):

    __tablename__ = "role_table"

    id = Column(Integer, index=True, primary_key=True)


    user_email = Column(String)
    role = Column(String)


class Template(Base):

    __tablename__ = "template_table"

    id = Column(Integer, index=True, primary_key=True)

    template_name = Column(String)
    template = Column(Text)
    added_at = Column(Date)


class Audit(Base):

    __tablename__ = "audit_table"

    id = Column(Integer, index=True, primary_key=True)

    user_id = Column(Integer)
    user_email = Column(String)
    activity = Column(String)
    time = Column(Date)



