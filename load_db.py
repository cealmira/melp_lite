
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
import pandas as pd

meta = MetaData()

# table definition
Restaurants = Table(
   'restaurants', meta, 
   Column('id', String, primary_key = True), 
   Column('rating', Integer), 
   Column('name', String), 
   Column('site', String), 
   Column('email', String), 
   Column('phone', String), 
   Column('street', String), 
   Column('city', String), 
   Column('state', String), 
   Column('lat', Float), 
   Column('lng', Float), 

)
# the name of the database; add path if necessary
db_name = 'melp.db'
# connection to the postgresql database
engine = create_engine('sqlite:///' + db_name, echo = False)

# creation of the table
meta.create_all(engine)

# import the data from the csv file
if __name__ == '__main__':
    data = pd.read_csv('restaurantes.csv')
    conn = engine.connect()

    # if there is data in the table we finish the code
    row_count = 0
    result = conn.execute(Restaurants.select())
    for i in result:
        row_count = row_count + 1
    
    if row_count > 0:
        exit()

    for index, row in data.iterrows():
        rest = Restaurants.insert().values(
            id = row[0],
            rating = row[1],
            name = row[2],
            site = row[3],
            email = row[4],
            phone = row[5],
            street = row[6],
            city = row[7],
            state = row[8],
            lat = row[9],
            lng = row[10]
        )
        result = conn.execute(rest)

    conn.commit()



