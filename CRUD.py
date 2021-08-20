from config import Config
import psycopg2
from psycopg2 import Error
from app.models import Pool
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

'''Base = declarative_base()

DATABASE_URI = Config.DATABASE_URI

engine = create_engine(DATABASE_URI)

#pour créer de nouvelle table
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

session = Session()

testfevrier = session.query(Pool).filter(Pool.name=='Pool CDL').first()
print(testfevrier)
session.commit()
session.close()'''


ajout_contrainte = """ALTER TABLE pool
                    ALTER test SET DEFAUlT 'test';"""
efface_column = """ALTER TABLE pool
                    DROP COLUMN test"""

try:
    conn = psycopg2.connect(user="vxicqjptlseyhf",
                            password="cd21e72dea74a3782f2d01347ac47cb347ffbce95359da40a3a346e6a628359f",
                            host="ec2-3-231-241-17.compute-1.amazonaws.com",
                            port="5432",
                            database="d7uv3bk2kvbm8")
    cursor = conn.cursor()
    cursor.execute(efface_column)
    conn.commit()
    print('success')
    print(test)
except (Exception, Error) as error:
    print('error', error)
finally:
    if conn:
        cursor.close()
        conn.close()
        print('connection close')