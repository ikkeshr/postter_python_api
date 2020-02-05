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
    

    def fetch_user(self, user_id):
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

    
    #datetime is set to 'now' if not entered
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

    def delete_post(self, _post_id):
        if str(_post_id) != "":
            sql = "DELETE FROM posts WHERE post_id=%s"
            deleted_rows_count = self.db.exec(sql, (_post_id,))
            return deleted_rows_count
        else:
            return -1

    #Note: offset is the starting index, 0 being the first
    #and limit is the length
    #sortby can be 'popular' or 'newest'
    def fetch_posts(self, _user_id=None, _offset=0, _limit=10, _sortby="popular", _viewer_user_id=0):
        for_user = ""
        if _user_id:
            for_user = "AND p.owner_user_id=" + str(_user_id)

        orderby = ""
        if _sortby == "popular":
            orderby = "ORDER BY pce.comments_count DESC"
        elif _sortby == "newest":
            orderby = "ORDER BY p.date DESC"
        
        #query_range = "LIMIT " + str(_offset) + ", " + str(_limit)
        query_range = "LIMIT %s, %s"%(str(_offset), str(_limit))

        #sql = self.get_fetch_post_query()
        #sql = sql + " " + for_user + " " + orderby + " " + query_range
        sql = "%s %s %s %s"%(self.get_fetch_post_query(), for_user, orderby, query_range,)

        data = {"viewer_user_id":_viewer_user_id,}
        posts = self.db.query(sql, data)
        return posts


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

                #Table integrity error
                #May already contain entry
                #or provided post_id or user_id don't exist
                return -2
        else:
            return -1

    
    def dislike_post(self, _user_id, _post_id):
        print ()

    def create_comment(self, _post_id, _owner_user_id, _datetime, _text, _parent_comment=None):
        print ()

    def delete_comment(self, _comment_id):
        print ()


#===============================================================================================================================================
    
    def get_fetch_post_query(self):
        sql = "\
            SELECT      p.post_id, p.owner_user_id, p.text, p.date, \
                        ple.likes_count, pdle.dislikes_count, pce.comments_count,\
                        vlp.if_liked_by_viewer, vdlp.if_disliked_by_viewer, vp.if_own_by_viewer,\
                        u.user_id, u.username, u.profile_pic_url\
            FROM        posts p, users u,\
            (\
                SELECT      p.post_id, COUNT(pl.post_id) as likes_count\
                FROM        posts p LEFT JOIN post_likes pl ON p.post_id=pl.post_id\
                GROUP BY    p.post_id\
            ) as ple,\
            (\
                SELECT      p.post_id, COUNT(pdl.post_id) as dislikes_count\
                FROM        posts p LEFT JOIN post_dislikes pdl ON p.post_id=pdl.post_id\
                GROUP BY    p.post_id\
            ) as pdle,\
            (\
                SELECT      p.post_id, COUNT(pc.post_id) as comments_count\
                FROM        posts p LEFT JOIN post_comments pc ON p.post_id=pc.post_id\
                GROUP BY    p.post_id\
            ) as pce,\
            (\
                SELECT      post_id, IF(owner_user_id=%(viewer_user_id)s, 1, 0) as if_own_by_viewer\
                FROM        posts \
            ) as vp,\
            (\
                SELECT      p.post_id, COUNT(pl.post_id) as if_liked_by_viewer\
                FROM        posts p LEFT JOIN post_likes pl ON p.post_id=pl.post_id AND pl.user_id=%(viewer_user_id)s\
                GROUP BY    p.post_id\
            ) as vlp,\
            (\
                SELECT      p.post_id, COUNT(pdl.post_id) as if_disliked_by_viewer\
                FROM        posts p LEFT JOIN post_dislikes pdl ON p.post_id=pdl.post_id AND pdl.user_id=%(viewer_user_id)s\
                GROUP BY    p.post_id\
            ) as vdlp\
            WHERE       p.post_id = ple.post_id\
            AND         p.post_id = pdle.post_id\
            AND         p.post_id = pce.post_id\
            AND         p.post_id = vlp.post_id\
            AND         p.post_id = vdlp.post_id\
            AND         p.post_id = vp.post_id\
            AND         p.owner_user_id = u.user_id\
            "
        return sql

        
        