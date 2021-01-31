import pandas as pd
import pyodbc


class AspenConn:
    def __init__(self, server, username):
        self.server = server
        self.username = username
        self.conn = self.get_conn()

    def get_conn(self):
        '''Establish OPC Connection to Aspen Server'''
        conn = pyodbc.connect(
            f'DRIVER={{AspenTech SQLplus}};HOST={self.server}')
        return conn

    def start_end(self, tag_list, start_datetime, end_datetime, request=1):
        '''Query the Aspen db from the start time to the end time'''
        tag_list = self.parse_tag_list(tag_list)

        sql_query = f'''
        SELECT *
        FROM HISTORY
        WHERE NAME IN {tag_list} AND
        TS BETWEEN TIMESTAMP'{start_datetime}' AND TIMESTAMP'{end_datetime}' AND
        REQUEST = {request}
        '''

        df = (pd.read_sql(sql_query, self.conn).pivot(index='TS',
                                                      columns='NAME',
                                                      values='VALUE'))

        return df

    def current(self, tag_list, mins=30, hours=0, days=0, request=1):
        '''Query the Aspen db from the current time back'''
        tag_list = self.parse_tag_list(tag_list)

        duration = 10 * 60 * (mins + 60 * hours + 24 * 60 * days)

        sql_query = f'''
        SELECT *
        FROM HISTORY
        WHERE NAME IN {tag_list} AND
        TS BETWEEN CURRENT_TIMESTAMP - {duration} AND CURRENT_TIMESTAMP AND
        REQUEST = {request}
        '''

        df = (pd.read_sql(sql_query, self.conn).pivot(index='TS',
                                                      columns='NAME',
                                                      values='VALUE'))

        return df

    def ip_analog(self, tag_list=None):
        tag_list = self.parse_tag_list(tag_list)

        sql_query = f'''
        SELECT *
        FROM IP_AnalogDef
        WHERE NAME LIKE '%{tag_list}%'
        '''

        df = pd.read_sql(sql_query, self.conn)

        return df

    def iogethistdef(self, tag_list=None, iogethistdef=''):
        tag_list = self.parse_tag_list(tag_list)

        sql_query = f'''
        SELECT NAME, IO_TAGNAME, "IO_VALUE_RECORD&&FLD"
        FROM IOGetHistDef
        WHERE "IO_VALUE_RECORD&&FLD" LIKE '{tag_list}' AND
        NAME LIKE '%{iogethistdef}%'
        '''

        df = pd.read_sql(sql_query, self.conn)

        return df

    def iostatus(self):
        '''Get the IOGetHistDef table overview of good and bad tags from the different sources
        '''
        sql_query = f'''
        SELECT *
        FROM IOGetHistDef
        '''
        df = pd.read_sql(sql_query, self.conn)

        return df

    def query(self, query):
        df = pd.read_sql(query, self.conn)
        return df

    def parse_tag_list(self, tag_list):
        if tag_list is None:
            tag_list = '%'
        elif type(tag_list) == str:
            tag_list = f"%{tag_list}%"
        else:
            tag_list = f"{tuple(tag_list)}"

        return tag_list
