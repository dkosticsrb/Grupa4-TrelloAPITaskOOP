import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# kreiranje klase za konekciju sa bazom i definisanje CRUD metoda
class DBConnection:
    def __init__(self, url):
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine)

    def create(self, db_object):
        session = self.Session()
        try:
            session.add(db_object)
            session.commit()
            return "Successfully added an object to the table " + db_object.__tablename__
        except sqlalchemy.exc.IntegrityError as ie:
            return "Error: " + ie.__repr__()
        except sqlalchemy.exc.InvalidRequestError as ir:
            return "Error: " + ir.__repr__()
        finally:
            session.close()

    def read(self, db_object, **query_filter):
        session = self.Session()
        try:
            if query_filter:
                result = session.query(db_object).filter_by(**query_filter).all()
            else:
                result = session.query(db_object).all()
            return result
        except sqlalchemy.exc.DataError as de:
            return "Error: " + de.__repr__()
        finally:
            session.close()

    def update(self, db_object, value, **query_filter):
        session = self.Session()
        try:
            result = session.query(db_object).filter_by(**query_filter).all()
            row = result[0]
            row.name = value
            session.commit()
            return "Successfully updated an object in the table " + db_object.__tablename__
        except sqlalchemy.exc.DataError as de:
            return "Error: " + de.__repr__()
        finally:
            session.close()

    def delete(self, db_object, **query_filter):
        session = self.Session()
        try:
            session.query(db_object).filter_by(**query_filter).delete()
            session.commit()
            return "Successfully deleted an object from the table " + db_object.__tablename__
        except sqlalchemy.exc.DataError as de:
            return "Error: " + de.__repr__()
        finally:
            session.close()
