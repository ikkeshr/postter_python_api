from db_connect import Db
from werkzeug.security import generate_password_hash, check_password_hash
from api import Postter

# _password = "ikkesh"
# _hashed_password = generate_password_hash(_password)
# print("pwhash: ", _hashed_password)

# input_password = input("Enter your password: ")
# if check_password_hash(_hashed_password, input_password):
#     print ("You guessed right...")
# else:
#     print ("Wrong password...")

# db = Db()

# username = "Tom"
# passw = "1234"
# picture_link = "https://clipartart.com/images/default-profile-picture-clipart-3.jpg"

# _hashed_password = generate_password_hash(passw)

# data = (username, _hashed_password, picture_link)

# sql = "INSERT INTO users (username, password, profile_pic_url) VALUES (%s, %s, %s)"

# sql2 = "SELECT * FROM users WHERE user_id=%s"

# data2 = ('3')

# sql3 = "SELECT * FROM users"

# #result = db.query(sql3)

# #print(result)

p = Postter()
r = p.like_post(1, 3)
print(r)








