from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import University, Base, Department, User
engine = create_engine('sqlite:///databasewithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user = User(name="ramana", email="venkataramanayenamandra@gmail.com")
session.add(user)
session.commit()


# Details of Swarnandhra college
university1 = University(name="Swarnandhra", user_id=1)

session.add(university1)
session.commit()

department1 = Department(name="Computer Science", dhod="Srinivas",
                         university=university1, user_id=1)

session.add(department1)
session.commit()

department2 = Department(name="Electronics", dhod="Mahesh",
                         university=university1, user_id=1)
session.add(department2)
session.commit()

department3 = Department(name="Mechanical", dhod="Gopichand",
                         university=university1, user_id=1)
session.add(department3)
session.commit()

department4 = Department(name="civil", dhod="shekar",
                         university=university1, user_id=1)
session.add(department4)
session.commit()

# Details of Srinikethan College
university2 = University(name="Srinikethan", user_id=1)
session.add(university2)
session.commit()

department1 = Department(name="Computer Science", dhod="karthik",
                         university=university2, user_id=1)

session.add(department1)
session.commit()

department2 = Department(name="Electronics", dhod="Mahesh kumar",
                         university=university2, user_id=1)
session.add(department2)
session.commit()

department3 = Department(name="Mechanical", dhod="Chandu",
                         university=university2, user_id=1)
session.add(department3)
session.commit()

department4 = Department(name="civil", dhod="koushik",
                         university=university2, user_id=1)
session.add(department4)
session.commit()

print ("added menu items successfully")
