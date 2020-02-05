import mysql.connector
import json

#https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html

class Db:
    def __init__(self):
        print ("Db instance created...")
        self.conx = None

    def initConnection(self):
        try:
            # Database credentials
            self.conx = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="",
                database="postter"
            )

            if self.conx.is_connected():
                print("Connection to the database established successfully..")

        except mysql.connector.Error as err:
            print ("Error while connecting to mysql database...")
            print ("Error code: " + str(err.errno))
            print ("Error msg: " + err.msg)

    
    def exec_ret_id(self, query, data=None):
        self.initConnection()
        if self.conx:
            cursor = self.conx.cursor(prepared=True)
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)

            inserted_id = cursor.lastrowid

            self.conx.commit()

            cursor.close()
            self.conx.close()

            if inserted_id:
                return inserted_id
            else:
                print ("Error while executing query: ", query)
                return None




    def exec(self, query, data=None):
        self.initConnection()
        if self.conx:
            cursor = self.conx.cursor(prepared=True)
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)

            affected_rows = cursor.rowcount

            self.conx.commit()
            cursor.close()
            self.conx.close()

            return affected_rows


    
    def query(self, query, data=None):
        self.initConnection()
        if self.conx:
            cursor = self.conx.cursor(dictionary=True)
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            #results = self.fetchJSON(cursor)

            cursor.close()
            self.conx.close()

            return results

    
    def fetchResults(self, cursor):
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows

    def fetchJSON(self, cur):
        row_headers=[x[0] for x in cur.description] #this will extract row headers
        rv = cur.fetchall()
        json_data=[]
        for result in rv:
                json_data.append(dict(zip(row_headers,result)))
        return json.dumps(json_data)

        






