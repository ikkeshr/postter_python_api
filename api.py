from db_connect import Db
from werkzeug.security import generate_password_hash, check_password_hash
import time
import re
import mysql.connector

class Postter:
    def __init__(self):
        self.db = Db()

    def username_exists(self, _username):
        if _username.strip() != "":
            sql = "SELECT COUNT(1) as ifexists FROM users WHERE username=%s"
            exists = self.db.query(sql, (_username,))[0]['ifexists']
            if exists == 1:
                return True
            else:
                return False
        else:
            return False

    def create_user(self, username, password, profile_pic_url=None):
        if username.strip() != "" and password != "" and (not self.username_exists(username)):
            _hashed_password = generate_password_hash(password)
            if profile_pic_url:
                sql = "INSERT INTO users (username, password, profile_pic_url)\
                        VALUES (%s, %s, %s)"
                data = (username, _hashed_password, profile_pic_url)
            else:
                sql = "INSERT INTO users (username, password)\
                        VALUES (%s, %s)"
                data = (username, _hashed_password)
            
            user_id = self.db.exec_ret_id(sql, data)
            return user_id
        else:
            #input not valid
            return -1

    
    def check_user(self, _username, _password):
        if _username.strip() != "" and _password != "":
            sql = "SELECT username, password FROM users WHERE username=%s"
            row_user = self.db.query(sql, (_username,))
            
            if len(row_user) == 1:
                #user exists
                hashed_password = row_user[0]['password']
                if check_password_hash(hashed_password, _password):
                    return True
                else:
                    #wrong password
                    return False
            else:
                #user don't exist
                return False
        else:
            #input not valid
            return False
    

    def load_user(self, user_id):
        if str(user_id) != "":
            sql = "SELECT user_id, username, profile_pic_url\
                FROM users\
                WHERE user_id=%s"
            try:
                user = self.db.query(sql, (user_id,))[0]
            except IndexError:
                #Invalid user id
                return -2
            return user
        else:
            #input not valid
            return -1

    
    #datetime is set to now if not entered
    def create_post(self, _user_id, _text, _datetime=time.strftime('%Y-%m-%d %H:%M:%S')):
        mysql_datetime_pattern = re.compile("^([0-9]{2,4})-([0-1][0-9])-([0-3][0-9])(?:( [0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?(.[0-9]{1,6})?$")
        if str(_user_id) != "" and mysql_datetime_pattern.match(_datetime) and _text != "":
            sql = "INSERT INTO posts (text, date, owner_user_id)\
                    VALUES (%s, %s, %s)"
            data = (_text, _datetime, _user_id)
            
            post_id = self.db.exec_ret_id(sql, data)
            return post_id
        else:
            #invalid input
            return -1

    def delete_post(self, post_id):
        if str(post_id) != "":
            sql = "DELETE FROM posts WHERE post_id=%s"
            deleted_rows_count = self.db.exec(sql, (post_id,))
            return deleted_rows_count
        else:
            return -1

    #Note: offset is the starting index, 0 being the first
    #and limit is the length
    #sortby can be 'popular' or 'newest'
    def load_all_posts(self, offset=0, limit=10, sortby="popular"):
        print ()


    def like_post(self, _post_id, _user_id):
        if str(_user_id) != "" and str(_post_id) != "":
            #first check if the user disliked the post
            #and delete the entry from post_dislikes table if it exists
            sql = "SELECT COUNT(1) as ifdisliked \
                    FROM post_dislikes\
                    WHERE post_id=%s AND user_id=%s"
            
            if_disliked = self.db.query(sql, (_post_id, _user_id,))[0]['ifdisliked']
            #print ("if_disliked:",if_disliked)

            #delete entry if it exists
            if if_disliked > 0:
                sql = "DELETE FROM post_dislikes WHERE post_id=%s AND user_id=%s"
                deleted_rows_count = self.db.exec(sql, (_post_id, _user_id,))
                
            #now insert like entry in post_likes
            sql = "INSERT INTO post_likes (post_id, user_id)\
                VALUES (%s, %s)"
            try:
                inserted_rows_count = self.db.exec(sql, (_post_id, _user_id,))
                return inserted_rows_count
            except mysql.connector.IntegrityError as err:
                print("Error Code:", err.errno)
                print("SQLSTATE:", err.sqlstate)
                print("Message:", err.msg)
                return -2
        else:
            return -1
        

        
        