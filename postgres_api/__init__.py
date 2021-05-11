import psycopg2
from psycopg2 import Error
from configparser import ConfigParser
import sys
import logging

def config(filename='./configuration/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db



logger = logging.getLogger("postgres")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.FileHandler('./logs/app_logs/app.log')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


try:
    # read connection parameters
    params = config()
    #print(params)
    # connect to the PostgreSQL server
    logger.info('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)

    # create a cursor
    cur = conn.cursor()
except (Exception, Error) as error:
    logger.critical("Error while working with PostgreSQL: ", error)
    sys.exit(1)
#finally:
 #       if conn is not None:
  #          conn.close()
   #         print('Database connection closed.')
