######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'ayyylmao'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '***REMOVED***1'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out', top_users=getTopScoreUsers())

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		email = request.form.get('email')
		birth_date = request.form.get('birth_date')
		hometown = request.form.get('hometown')
		gender = request.form.get('gender')
		password = request.form.get('password')

		# Do something here :XXXXXXXXXXXXXXXXXXXXXXXXx



	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test = isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (first_name, last_name, email, birth_date, hometown, gender, password, score)"
							 "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(first_name, last_name, email, birth_date, hometown, gender, password, 0)))

		# Remember to edit this ^^^^ print statement for the insert!!!!!!!!!!!

		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!', top_users=getTopScoreUsers())
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	conn.cursor()
	cursor.execute("SELECT P.imgdata, P.photo_id, P.caption, P.num_likes FROM Photos P WHERE P.user_id = '{0}'".format(uid))
	test = cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
	return test

def getUsersAlbums(uid):
	conn.cursor()
	cursor.execute("SELECT A.albums_id, A.name FROM ALbums A WHERE A.user_id = '{0}'".format(uid))
	test = cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
	return test


def getPhotosFromAlbumId(album_id):
	conn.cursor()
	cursor.execute("SELECT P.imgdata, P.photo_id, P.caption, P.num_likes FROM Photos P WHERE P.albums_id = '{0}'".format(album_id))
	test = cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
	return test

def getAllAlbumNames():
	conn.cursor()
	cursor.execute("SELECT A.name, A.albums_id FROM Albums A ")
	test = cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
	return test

def getAlbumNameFromAlbumId(album_id):
	conn.cursor()
	cursor.execute("SELECT A.name FROM Albums A WHERE A.albums_id = '{0}'".format(album_id))
	test = cursor.fetchall()[0][0] #NOTE list of tuples, [(imgdata, pid), ...]
	return test

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def getAllTagNames():
	conn.cursor()
	cursor.execute("SELECT T.name, T.tag_id FROM Tags T ORDER BY T.num_photos DESC")
	test = cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
	return test

def getTagIdFromTagName(tag_name):
	cursor = conn.cursor()
	cursor.execute("SELECT T.tag_id FROM Tags T WHERE T.name = '{0}'".format(tag_name))
	return cursor.fetchall()[0][0]

def getTagNameFromTagId(tag_id):
	cursor = conn.cursor()
	cursor.execute("SELECT T.name FROM Tags T WHERE T.tag_id = '{0}'".format(tag_id))
	return cursor.fetchall()[0][0]

def getUserNameFromUserId(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, U.last_name FROM Users U WHERE U.user_id = '{0}'".format(user_id))
	test = cursor.fetchall()[0]
	full_name = test[0] + " " + test[1]
	return full_name

def getEmailFromUserId(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT U.email FROM Users U WHERE U.user_id = '{0}'".format(user_id))
	email = cursor.fetchall()[0][0]
	return email

def getLikeUsersFromPhotoId(photo_id):
	conn.cursor()
	cursor.execute("SELECT L.user_id FROM Likes L WHERE L.photo_id = '{0}'".format(photo_id))
	users = cursor.fetchall()
	user_names = []
	for user in users:
		user_names += [getUserNameFromUserId(user[0])]
	return user_names

def getAllPhotoLikes():
	conn.cursor()
	cursor.execute("SELECT P.photo_id FROM Photos P")
	photo_ids = cursor.fetchall()
	photo_likes = []
	for photo_id in photo_ids:
		photo_id = photo_id[0]
		cursor.execute("SELECT COUNT(*) FROM Likes L WHERE (L.photo_id = '{0}')".format(photo_id))
		num_likes = cursor.fetchall()[0][0]
		users = getLikeUsersFromPhotoId(photo_id)
		photo_likes += [(photo_id, num_likes, users)]
	return photo_likes

def getSecondAttribute(x):
	return x[1]

def increaseScore(uid):
	cursor.execute("SELECT U.score FROM Users U WHERE U.user_id = '{0}'".format(uid))
	user_score = cursor.fetchall()[0][0]
	cursor.execute("UPDATE Users SET score = '{0}' WHERE user_id = '{1}'".format(user_score + 1, uid))
	conn.commit()
	return

def getTopScoreUsers():
	conn.cursor()
	cursor.execute("SELECT U.score, U.first_name, U.last_name FROM Users U WHERE NOT U.user_id = -1 ORDER BY U.score DESC")
	top_users = cursor.fetchall()[:2]
	return top_users

# def getPhotoIdsFromTagId(tag_id, user_id=None):
# 	conn.cursor()
# 	if user_id == None:
# 		cursor.execute("SELECT T.photo_id FROM Tagged T WHERE T.tag_id = '{0}'".format(tag_id))
# 		return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]
# 	else:
# 		cursor.execute("SELECT T.photo_id FROM Tagged T WHERE (T.tag_id = '{0}' AND T.".format(tag_id))
# 		return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

# def getPhotosFromTagId(tag_id, user_id=None):
# 	photo_ids = getPhotoIdsFromTagId(tag_id, user_id)
# 	photos = []
# 	conn.cursor()
# 	for photo_id in photo_ids:
# 		cursor.execute("SELECT P.imgdata, P.photo_id, P.caption FROM Photos P WHERE P.photo_id = '{0}'".format(photo_id))
# 	photos += cursor.fetchall()[0]  # NOTE list of tuples, [(imgdata, pid), ...]
# 	return photos

def getPhotosFromTagId(tag_id, user_id=None):
	conn.cursor()
	if user_id == None:
		cursor.execute("SELECT P.imgdata, P.photo_id, P.caption, P.num_likes FROM Tagged T, Photos P WHERE (P.photo_id = T.photo_id AND T.tag_id = '{0}')".format(tag_id))
		photos = cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]
		return photos
	else:
		cursor.execute("SELECT P.imgdata, P.photo_id, P.caption, P.num_likes FROM Tagged T, Photos P "
						"WHERE (P.photo_id = T.photo_id AND T.tag_id = '{0}' AND P.user_id = '{1}')".format(tag_id, user_id))
		photos = cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]
		return photos

def getPhotoFromPhotoId(photo_id):
	conn.cursor()
	cursor.execute("SELECT P.imgdata, P.photo_id, P.caption, P.num_likes "
				   "FROM Photos P WHERE (P.photo_id = '{0}')".format(photo_id))
	return cursor.fetchall()[0]

def getAllComments():
	conn.cursor()
	cursor.execute("SELECT C.user_id, C.text, C.photo_id FROM Comments C")
	all_comms = cursor.fetchall()
	comms = []
	for com in all_comms:
		full_name = getUserNameFromUserId(com[0])
		print("~~~~~~~~~~~~~~~~~~~~~~~~~")
		print(full_name)
		print("~~~~~~~~~~~~~~~~~~~~~~~~~")
		comms += [(full_name, com[1], com[2])]

	return comms

def getUserIdFromPhotoId(photo_id):
	conn.cursor()
	cursor.execute("SELECT P.user_id FROM Photos P WHERE P.photo_id = '{0}'".format(photo_id))
	test = cursor.fetchall()[0][0]
	return test

# def getPhotosFromMutliTagId(tag_ids, user_id=None):
# 	conn.cursor()
# 	num_tags = len(tag_ids)
# 	for i in range(num_tags):
# 		if user_id == None:
# 			cursor.execute("SELECT P.imgdata, P.photo_id, P.caption FROM Tagged T, Photos P WHERE (P.photo_id = T.photo_id AND T.tag_id = '{0}')".format(tag_id))
# 			photos = cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]
#
# 		else:
# 			cursor.execute("SELECT P.imgdata, P.photo_id, P.caption FROM Tagged T, Photos P "
# 							"WHERE (P.photo_id = T.photo_id AND T.tag_id = '{0}' AND P.user_id = '{1}')".format(tag_id, user_id))
# 			photos = cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]



@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id,
						   message="Here's your profile", top_users=getTopScoreUsers())

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# creates an album with the given album name and returns the album id.
# only returns the album id if the album has already been created.
def create_album(album_name):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT A.name FROM Albums A WHERE (A.name = '{0}' AND A.user_id = '{1}')".format(album_name, user_id) )
	alb_name = cursor.fetchall()
	if not alb_name:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums (user_id, name) VALUES ('{0}', '{1}')".format(user_id, album_name))
		conn.commit()
	cursor.execute("SELECT A.albums_id FROM Albums A WHERE (A.name = '{0}' AND A.user_id = '{1}')".format(album_name, user_id) )
	alb_id = cursor.fetchall()[0][0]
	# print(alb_id)
	return alb_id

# creates a tag with the given and returns the tag id.
# only returns the tag id if the tag has already been created.
def create_tag(tag_name):
	cursor = conn.cursor()
	cursor.execute("SELECT T.name FROM Tags T WHERE T.name = '{0}'".format(tag_name))
	t_name = cursor.fetchall()
	if not t_name:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Tags (name, num_photos) VALUES ('{0}', '{1}')".format(tag_name, 0))
		conn.commit()
	cursor.execute("SELECT T.tag_id FROM Tags T WHERE T.name = '{0}'".format(tag_name))
	tag_id = cursor.fetchall()[0][0]
	# print(alb_id)
	return tag_id

@app.route('/upload', methods=['GET'])
@flask_login.login_required
def upload():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('upload.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid))

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		# print("\n \n \n \n \n")
		# print("user_id = " + str(uid))
		# print("caption = " + caption)
		album_name = request.form.get('album')
		# print("album_name = " + album_name)
		album_id = create_album(album_name)
		# print("album_id = " + str(album_id))
		photo_data = base64.b64encode(imgfile.read()).decode('ascii')
		# print(type(photo_data))
		# # photo_data = "FILLER"
		# print(type(imgfile))
		# print("\n \n \n \n \n")
		try:
			conn.cursor()
			cursor.execute("INSERT INTO Photos (caption, imgdata, albums_id, user_id, num_likes) "
						   "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(caption, photo_data, album_id, uid, 0))
			conn.commit()
			increaseScore(uid)
			return render_template('hello.html', message='Photo uploaded!',
								   photos=getUsersPhotos(uid), base64=base64, top_users=getTopScoreUsers())
		except:
			return render_template('upload.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid) )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('upload.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid))

@app.route('/upload/delete-file', methods=['GET', 'POST'])
@flask_login.login_required
def delete_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		photo_id = request.form.get('photo_id')
		conn.cursor()
		cursor.execute("DELETE FROM Photos P WHERE P.photo_id = '{0}'".format(photo_id))
		conn.commit()

		return render_template('hello.html', message='Photo deleted!',
							   photos=getUsersPhotos(uid), base64=base64, top_users=getTopScoreUsers() )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('upload.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid))

@app.route('/upload/delete-album', methods=['GET', 'POST'])
@flask_login.login_required
def delete_album():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_id = request.form.get('album_id')
		conn.cursor()
		cursor.execute("DELETE FROM Albums A WHERE A.albums_id = '{0}'".format(album_id))
		conn.commit()

		return render_template('hello.html', message='Photo deleted!',
							   photos=getUsersPhotos(uid), base64=base64, top_users=getTopScoreUsers() )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('upload.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid))
#end photo uploading code

@app.route("/friends", methods=['GET'])
@flask_login.login_required
def friends():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	conn.cursor()
	cursor.execute("SELECT F.user_id2 FROM Friends F WHERE F.user_id1 = '{0}'".format(str(user_id) ) )
	friendid_query = cursor.fetchall()
	friend_ids = [friend[0] for friend in friendid_query]
	friend_query = []
	for id in friend_ids:
		cursor.execute("SELECT U.email FROM Users U WHERE U.user_id = '{0}'".format(id))
		friend_query += cursor.fetchall()[0]

	conn.commit()
	return render_template('friends.html', friend_query=friend_query)

@app.route("/friends", methods=['POST'])
@flask_login.login_required
def find_friend():
	try:
		friend_id = getUserIdFromEmail(request.form.get('friend_email'))

	except:
		print("couldn't find all tokens")
		return render_template('friends.html', message="Email empty or not found.")
	conn.cursor()
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if friend_id == user_id:
		return render_template('friends.html', message="You can't add yourself!")
	else:
		try:
			print(cursor.execute("INSERT INTO Friends (user_id1, user_id2)"
							 "VALUES ('{0}', '{1}')".format(user_id, friend_id)))
			conn.commit()
			return render_template('friends.html', message="Friend added!")
		except:
			return render_template('friends.html', message="Already friends with this person.")

@app.route("/friends/get-rec", methods=['POST'])
@flask_login.login_required
def friend_rec():
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		conn.cursor()
		cursor.execute("SELECT F.user_id2 FROM Friends F WHERE F.user_id1 = '{0}'".format(uid))
		own_friends_bad = cursor.fetchall()
		if own_friends_bad == ():
			return render_template('friends.html', message="You need friends to get recommendations!")
		own_friends = []
		for own_friend in own_friends_bad:
			own_friends += [own_friend[0]]
		rec_friends = []
		for own_friend in own_friends:
			print(own_friend)
			print(own_friends)
			cursor.execute("SELECT F.user_id2 FROM Friends F WHERE (F.user_id1 = '{0}' "
						   "AND NOT F.user_id2 = '{1}')".format(own_friend, uid))
			their_friends = cursor.fetchall()
			for their_friend in their_friends:
				their_friend = their_friend[0]
				if not their_friend in own_friends:
					rec_friends += [their_friend]
		final_rec = []
		for friend in rec_friends:
			num_recs = rec_friends.count(friend)
			temp = (friend, num_recs)
			if not temp in final_rec:
				final_rec += [temp]
		final_rec.sort(key=getSecondAttribute, reverse=True)
		for i in range(len(final_rec)):
			full_name = getUserNameFromUserId(final_rec[i][0])
			email = getEmailFromUserId(final_rec[i][0])
			final_rec[i] = (full_name, email)

		return render_template('friends.html', message="Found recommendations!", recs=final_rec)
	except:
		return render_template('friends.html', message="Recommendation not possible!")


@app.route("/photos", methods=['GET'])
def photos():
	return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(), likes=getAllPhotoLikes())


@app.route("/photos", methods=['POST'])
def show_album():
	album_id = request.form.get('album_id')
	# print("\n \n \n \n")
	# print(album_id)
	# print("\n \n \n \n")
	photos = getPhotosFromAlbumId(album_id)
	album_name = getAlbumNameFromAlbumId(album_id)
	# print("\n \n \n \n")
	# print(photos)
	# print("\n \n \n \n")
	return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(), photos=photos,
						   album_name=album_name, likes=getAllPhotoLikes(),
						   photo_message="Here are the photos in album ", comments=getAllComments())

@app.route("/photos/show-tag", methods=['POST'])
def show_tag():
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		view_all = request.form.get('view_all')
	except:
		view_all = "True"
	tag_id = request.form.get('tag_id')
	tag_name = getTagNameFromTagId(tag_id)
	if (view_all == "True"):
		photos = getPhotosFromTagId(tag_id)
	else:
		photos = getPhotosFromTagId(tag_id, user_id=uid)
	# print("\n \n \n \n")
	# print(photos)
	# print("\n \n \n \n")
	return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(), photos=photos,
						   album_name=tag_name, likes=getAllPhotoLikes(), photo_message="Here are the photos with tag ", comments=getAllComments())

@app.route("/photos/show-multi-tag", methods=['POST'])
def show_multi_tag():
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		view_all = request.form.get('view_all')
	except:
		view_all = "True"
	tag_names = request.form.get('tag_names')
	tag_names = tag_names.split(", ")
	tag_ids = []
	try:
		for tag in tag_names:
			tag_ids += [getTagIdFromTagName(tag)]
	except:
		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
							   message="That tag doesn't exists!")

	photos = []
	for tag_id in tag_ids:
		if (view_all == "True"):
			photos.append(getPhotosFromTagId(tag_id))
		else:
			photos.append(getPhotosFromTagId(tag_id, user_id=uid))

	compare_set = []
	final_photos = []
	tag_name = ""

	if len(tag_ids) > 1:
		for i in range(len(photos[0])):
			compare_set += [photos[0][i][1]]
		for k in range(1, len(photos)):
			for i in range(len(photos[k])):
				if ((photos[k][i][1] in compare_set) and (photos[k][i] not in final_photos)):
					final_photos += [photos[k][i]]

		for tag in tag_names:
			tag_name += tag + ", "
	else:
		tag_name = tag_names[0]
		final_photos = photos[0]

	return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
						   photos=final_photos, album_name=tag_name, likes=getAllPhotoLikes(),
						   photo_message="Here are the photos with tags ", comments=getAllComments())

# adds a tag to a chosen picture
@app.route("/upload/add-tag", methods=['POST'])
@flask_login.login_required
def add_tag():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_id = request.form.get('photo_id')
	tag_name = request.form.get('tag_name')
	tag_id = create_tag(tag_name)
	try:
		conn.cursor()
		cursor.execute("INSERT INTO Tagged (photo_id, tag_id, user_id) VALUES ('{0}', '{1}', '{2}')".format(photo_id, tag_id, uid) )
		conn.commit()
		cursor.execute("SELECT T.num_photos FROM Tags T WHERE T.name = '{0}'".format(tag_name))
		t_photoVal = cursor.fetchall()[0][0]
		cursor.execute("UPDATE Tags SET num_photos = '{0}' WHERE name = '{1}'".format(t_photoVal + 1, tag_name))
		conn.commit()
		return render_template('hello.html', message="Tag added!", top_users=getTopScoreUsers())
	except:
		return render_template('upload.html', photos=getUsersPhotos(uid), albums=getUsersAlbums(uid), likes=getAllPhotoLikes() )

# adds a comment on the chosen picture
@app.route("/photos/leave-comment", methods=['POST'])
def leave_comment():
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
	except:
		uid = -1
	photo_id = request.form.get('photo_id')
	comment = request.form.get('comment')
	if uid == getUserIdFromPhotoId(photo_id):
		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
							   message="You can't comment on your own photos, silly!", likes=getAllPhotoLikes(), comments=getAllComments())
	try:
		conn.cursor()
		cursor.execute("INSERT INTO Comments (user_id, photo_id, text) VALUES ('{0}', '{1}', '{2}')".format(uid, photo_id, comment) )
		conn.commit()
		increaseScore(uid)
		return render_template('hello.html', message="Comment successfully made!", top_users=getTopScoreUsers())
	except:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
								message="Comment failed.", likes=getAllPhotoLikes(), comments=getAllComments())

@app.route("/photos/like-photo", methods=['POST'])
@flask_login.login_required
def like_photo():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_id = request.form.get('photo_id')
	try:
		conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM Likes L WHERE (L.photo_id = '{0}' AND L.user_id = '{1}')".format(photo_id, uid))
		if (cursor.fetchall()[0][0] == 0):
			cursor.execute("INSERT INTO Likes (user_id, photo_id) VALUES ('{0}', '{1}')".format(uid, photo_id))
			conn.commit()
			cursor.execute("SELECT P.num_likes FROM Photos P WHERE P.photo_id = '{0}'".format(photo_id))
			t_likeVal = cursor.fetchall()[0][0]
			cursor.execute("UPDATE Photos SET num_likes = '{0}' WHERE photo_id = '{1}'".format(t_likeVal + 1, photo_id))
			conn.commit()
			return render_template('hello.html', message="Photo has been liked!", top_users=getTopScoreUsers())
		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
							   message="Photo already Liked.")
	except:
		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
							   message="Like failed.", likes=getAllPhotoLikes())

@app.route("/photos/search-comments", methods=['POST'])
def search_comments():
	search_comment = request.form.get('search_comment')
	conn.cursor()
	cursor.execute("SELECT C.user_id FROM Comments C WHERE (C.text = '{0}' AND NOT C.user_id = -1)".format(search_comment))
	user_ids = cursor.fetchall()
	user_count = []

	for user_id in user_ids:
		user_id = user_id[0]
		cursor.execute("SELECT COUNT(*) FROM Comments C WHERE C.user_id = '{0}'".format(user_id))
		temp = (user_id, cursor.fetchall()[0][0])
		if temp not in user_count:
			user_count += [temp]
	user_count.sort(key=getSecondAttribute, reverse=True)
	comment_users = []
	if (user_ids != []):
		for user in user_count:
			comment_users += [getUserNameFromUserId(user[0])]

	return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
								likes=getAllPhotoLikes(), comment_users=comment_users)

@app.route("/photos/photo-rec", methods=['POST'])
@flask_login.login_required
def photo_rec():
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		conn.cursor()
		cursor.execute("SELECT T.tag_id, COUNT(*) FROM Tagged T WHERE T.user_id = '{0}' "
					   "GROUP BY T.tag_id ORDER BY COUNT(*) DESC".format(uid))
		tag_id_count = cursor.fetchall()[:5]
		cursor.execute("SELECT T.tag_id, COUNT(*) FROM Tags T WHERE T.tag_id = -1 "
					   "GROUP BY T.tag_id")
		filler_tag = cursor.fetchall()
		while(len(tag_id_count) < 5):
			tag_id_count += filler_tag

		print("2~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		cursor.execute("SELECT * FROM ((SELECT T.photo_id, COUNT(*) AS count_top_5 FROM Tagged T "
					   "WHERE (T.tag_id = '{0}' OR T.tag_id = '{1}' OR T.tag_id = '{2}' OR T.tag_id = '{3}' OR T.tag_id = '{4}')"
					   "GROUP BY T.photo_id) AS counter1 NATURAL JOIN"
						"(SELECT T.photo_id, COUNT(*) AS count_total FROM Tagged T "
						"GROUP BY T.photo_id) AS counter2) ORDER BY count_top_5 DESC, count_total ASC".format(tag_id_count[0][0], tag_id_count[1][0], tag_id_count[2][0], tag_id_count[3][0],
							   tag_id_count[4][0]))
		print("3~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		photo_tag_count = cursor.fetchall()
		print(photo_tag_count)

		photos = []
		for photo in photo_tag_count:
			photos += [getPhotoFromPhotoId(photo[0])]

		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
							   likes=getAllPhotoLikes(), photos=photos, photo_message="Recommended photos: ", comments=getAllComments())
	except:
		return render_template('photos.html', albums=getAllAlbumNames(), tags=getAllTagNames(),
							   likes=getAllPhotoLikes(), photo_message="Recommendation failed... Try adding tags to your photos!")



#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare', top_users=getTopScoreUsers())


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
