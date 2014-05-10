#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
			       autoescape = True)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
	self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

    def render(self, template, **kw):
	self.write(self.render_str(template, **kw))

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
	self._render_text = self.content.replace('\n', <br>)
	return render_str("post.html", p = self)

class Permalink(BlogHandler):
    def get(self, post_id):
	print post_id
	post = Post.get_by_id(int(post_id))
	self.render("front.html", posts=[post])

class NewPostHandler(BlogHandler):
    def render_newpost(self, subject="", content="", error=""):
	self.render("newpost.html", subject=subject, content=content, error=error)
  
    def get(self):
	self.render_newpost()

    def post(self):
	subject = self.request.get("subject")
	content = self.request.get("content")
	
	if subject and content:
	    post = Post(subject=subject, content=content)
	    key = post.put()
	    print int(post.key().id())
	    self.redirect("/blog/%s" % post.key().id())
	else:
	    error = "subject and content, please!"
	    self.render_newpost(subject, content, error)

class MainPage(BlogHandler):  
    def render_latestposts(self, posts=""):
	self.render("front.html", posts=posts)

    def get(self):
	posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
	self.render_latestposts(posts)

app = webapp2.WSGIApplication([('/blog', MainPage),
			       ('/blog/newpost', NewPostHandler),
			       (r'/blog/(\d+)', Permalink)],
				debug=True)
