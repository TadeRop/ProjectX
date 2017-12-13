#!/usr/bin/env python
from google.appengine.api import users
import os
import jinja2
import webapp2
import json
from models import Message
from google.appengine.api import urlfetch

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        params = {}

        if user:
            logout_url = users.create_logout_url('/')
            params["logged_in"] = True
            params["email"] = user.email()
            params["logout_url"] = logout_url
        else:
            login_url = users.create_login_url('/main')
            params["logged_in"] = False
            params["email"] = "Anonymous"
            params["login_url"] = login_url

        return self.render_template("hello.html", params=params)

class LoggedInHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        params = {}

        email = user.email()
        params["email"] = user.email()
        logout_url = users.create_logout_url('/')
        params["logout_url"] = logout_url


        return self.render_template("main.html", params=params)

class MessengerHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        params = {}
        email = user.email()
        params["email"] = user.email()
        logout_url = users.create_logout_url('/')
        params["logout_url"] = logout_url

        return self.render_template("messenger.html", params=params)

    def post(self):
        user = users.get_current_user()

        params = {}

        author = user.nickname()
        email = user.email()
        to = self.request.get("to")
        message = self.request.get("message")

        msg_object = Message(author_name=author, email=email, message=message, to=to)
        msg_object.put()

        logout_url = users.create_logout_url('/')
        params["logout_url"] = logout_url

        return self.redirect_to("messenger")

class InboxHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        sent_list = Message.query(Message.to == user.email()).fetch()
        params = {"sent_list": sent_list}

        logout_url = users.create_logout_url('/')
        params["logout_url"] = logout_url

        return self.render_template("inbox.html", params=params)

class SentHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        sent_list = Message.query(Message.to != user.email()).fetch()
        params = {"sent_list": sent_list}

        logout_url = users.create_logout_url('/')
        params["logout_url"] = logout_url

        return self.render_template("sent.html", params=params)

class WeatherHandler(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=Maribor&units=metric&appid=2b9448f3b7960c3e992c3d62064c5f19"

        result = urlfetch.fetch(url)

        podatki = json.loads(result.content)

        params = {"podatki": podatki}

        logout_url = users.create_logout_url('/')
        params["logout_url"] = logout_url

        self.render_template("weather.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/main', LoggedInHandler),
    webapp2.Route('/messenger', MessengerHandler, name="messenger"),
    webapp2.Route('/inbox', InboxHandler),
    webapp2.Route('/sent', SentHandler),
    webapp2.Route('/weather', WeatherHandler),
], debug=True)
