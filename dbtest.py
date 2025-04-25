from WebApp import db, app
from WebApp.models import User, Post

app.app_context().push()

john = User(username="john", email="john@uni-pannon.hu")
john.set_password("qweasd")
bob = User(username="bob", email="bob@uni-pannon.hu")
bob.set_password("qweasd")
db.session.add(john)
db.session.add(bob)
db.session.commit()


john.posts.append(Post(message = "Lorem ipsum by John 1", user_id=john.id))
john.posts.append(Post(message = "Lorem ipsum by John 2", user_id=john.id))
john.posts.append(Post(message = "Lorem ipsum by John 3", user_id=john.id))
bob.posts.append(Post(message = "Lorem ipsum by Bob 1", user_id=bob.id))
bob.posts.append(Post(message = "Lorem ipsum by Bob 2", user_id=bob.id))
db.session.commit()