import psycopg2 as pg
import os

class Singleton:
  def __init__(self, klass):
    self.klass = klass
    self.instance = None
  def __call__(self, *args, **kwds):
    if self.instance == None:
      self.instance = self.klass(*args, **kwds)
    return self.instance

@Singleton
class Connector():
    connection = None
    def __init__(self, region):
        self.region = region

    def get_connection(self, env='prod'):



        CONN_STRING = "host='{}' dbname='{}' port={} user='{}'".format(os.environ['DB_HOST'], 'noble_primary', os.environ['PORT'], os.environ['DB_USER'])
        READ_ONLY_CONN_STRING = CONN_STRING + ' password= ' + os.environ['DB_USER_PASS']


        if self.connection is None:
            self.connection = pg.connect(READ_ONLY_CONN_STRING)
        return self.connection

    def close(self):
        self.connection.close()