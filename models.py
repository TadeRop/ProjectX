from google.appengine.ext import ndb


class Message(ndb.Model):
    author_name = ndb.StringProperty()
    email = ndb.StringProperty()
    message = ndb.TextProperty()
    to = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
