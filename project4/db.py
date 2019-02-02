import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class University(Base):
    __tablename__ = 'university'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return
        {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }


class Department(Base):
    __tablename__ = 'department'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    dhod = Column(String(80))
    university_id = Column(Integer, ForeignKey('university.id'))
    university = relationship(University)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return
        {
            'id': self.id,
            'name': self.name,
            'dhod': self.dhod,
        }
engine = create_engine('sqlite:///databasewithusers.db')
Base.metadata.create_all(engine)
