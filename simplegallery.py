'''
Created on Apr 2, 2018

@author: kenng
'''
import cgi
import urllib

import os

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.ext import webapp

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from time import sleep

import jinja2
import webapp2



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


DEFAULT_simplegallery_NAME = 'default_simplegallery'


# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def simplegallery_key(simplegallery_name=DEFAULT_simplegallery_NAME):
    """Constructs a Datastore key for a simplegallery entity with simplegallery_name."""
    return ndb.Key('simplegallery', simplegallery_name)
          
class UserData(db.Model):
    user = db.StringProperty()
    blob_key = blobstore.BlobReferenceProperty()

class Greeting(ndb.Model):
    """Models an individual simplegallery entry with author, content, and date."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        greetings_query = Greeting.query(
            ancestor=simplegallery_key(simplegallery_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        link_image = 'images'
        url_image = 'image'
        link_video = 'videos'
        url_video = 'video'
        link_audio = 'audios'
        url_audio = 'audio'
        page = 'index'
        template_values = {
            'page' : page,
            'greetings': greetings,
            'simplegallery_name': urllib.quote_plus(simplegallery_name),
            'url': url,
            'url_linktext': url_linktext,
            'url_video':url_video,
            'url_audio':url_audio,
            'url_image':url_image,
            'link_image':link_image,
            'link_video':link_video,
            'link_audio':link_audio,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class simplegallery(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        greeting = Greeting(parent=simplegallery_key(simplegallery_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'simplegallery_name': simplegallery_name}
        self.redirect('/?' + urllib.urlencode(query_params))



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            user_data = UserData(user=users.get_current_user().user_id(),
                                   blob_key=upload.key())
            db.put(user_data)

            self.redirect('/serve/%s' % upload.key())


        except:
            #self.redirect('/upload_failure.html')
            self.error(404)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    
    def get(self, resource):
        #sleep(0.1)
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class PreviewHandler(webapp.RequestHandler):            
    def get(self, resource):
        print resource
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        preview_key = resource
        if blob_info:
            simplegallery_name = self.request.get('simplegallery_name',
                                              DEFAULT_simplegallery_NAME)
            if users.get_current_user():
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
            else:
                url = users.create_login_url(self.request.uri)
                url_linktext = 'Login'
                
            link_image = 'images'
            url_image = 'image'
            link_video = 'videos'
            url_video = 'video'
            link_audio = 'audios'
            url_audio = 'audio'
            preview = 'preview'
            content_type = blob_info.content_type
            content_type = content_type[0:3]
            preview_key = blob_info.key()
            template_values = {
                'preview' : preview,
                'simplegallery_name': urllib.quote_plus(simplegallery_name),
                'url': url,
                'url_linktext': url_linktext,
                'url_video':url_video,
                'url_audio':url_audio,
                'url_image':url_image,
                'link_image':link_image,
                'link_video':link_video,
                'link_audio':link_audio,
                'preview_key': preview_key,
                'content_type':content_type,
                'blob': blob_info,
            }
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            self.error(404)
            #self.redirect('/page_not_found')
            
class PageNotFoundHandler(webapp.RequestHandler):
    def get(self):

        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        link_image = 'images'
        url_image = 'image'
        link_video = 'videos'
        url_video = 'video'
        link_audio = 'audios'
        url_audio = 'audio'
        page = 'item_not_found'
        template_values = {
            'page' : page,
            'simplegallery_name': urllib.quote_plus(simplegallery_name),
            'url': url,
            'url_linktext': url_linktext,
            'url_video':url_video,
            'url_audio':url_audio,
            'url_image':url_image,
            'link_image':link_image,
            'link_video':link_video,
            'link_audio':link_audio,
            'blobs' : "Item Not Found",
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


    
# Render the upload form page when user hit upload link
class UploadFormHandler(webapp.RequestHandler):
    def get(self):
        #upload_url = blobstore.create_upload_url('/upload')
        upload_url_rpc = blobstore.create_upload_url_async('/upload')
        upload_url = upload_url_rpc.get_result()
        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        link_image = 'images'
        url_image = 'image'
        link_video = 'videos'
        url_video = 'video'
        link_audio = 'audios'
        url_audio = 'audio'
        if users.get_current_user():
            template_values = {
                'upload_url': upload_url,
                'simplegallery_name': urllib.quote_plus(simplegallery_name),
                'url': url,
                'url_linktext': url_linktext,
                'url_video':url_video,
                'url_audio':url_audio,
                'url_image':url_image,
                'link_image':link_image,
                'link_video':link_video,
                'link_audio':link_audio,
            }
            template = JINJA_ENVIRONMENT.get_template('upload.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect(url)
            
            
class imgView( webapp.RequestHandler):
    #blob  = blobstore.BlobInfo.all('WHERE content_type = "image/gif"')
    gqlQuery = blobstore.BlobInfo.gql("WHERE content_type IN ('image/gif', 'image/jpeg', 'image/png') ORDER BY creation DESC")
    blobs = gqlQuery.fetch(1000)
  
    def get(self):

        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        link_image = 'images'
        url_image = 'image'
        link_video = 'videos'
        url_video = 'video'
        link_audio = 'audios'
        url_audio = 'audio'
        template_values = {
            'simplegallery_name': urllib.quote_plus(simplegallery_name),
            'url': url,
            'url_linktext': url_linktext,
            'url_video':url_video,
            'url_audio':url_audio,
            'url_image':url_image,
            'link_image':link_image,
            'link_video':link_video,
            'link_audio':link_audio,
            'blobs' : self.blobs,
        }
        template = JINJA_ENVIRONMENT.get_template('image.html')
        self.response.write(template.render(template_values))
            

class audioView(webapp.RequestHandler):
    gqlQuery = blobstore.BlobInfo.gql("WHERE content_type IN ('audio/mp3', 'audio/AIFF', 'audio/aac', 'audio/wav', 'audio/wma', 'audio/ogg') ORDER BY creation DESC")
    blobs = gqlQuery.fetch(20)
    
    def get(self):
        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        link_image = 'images'
        url_image = 'image'
        link_video = 'videos'
        url_video = 'video'
        link_audio = 'audios'
        url_audio = 'audio'
        template_values = {
            'simplegallery_name': urllib.quote_plus(simplegallery_name),
            'url': url,
            'url_linktext': url_linktext,
            'url_video':url_video,
            'url_audio':url_audio,
            'url_image':url_image,
            'link_image':link_image,
            'link_video':link_video,
            'link_audio':link_audio,
            'blobs' : self.blobs,
        }
        template = JINJA_ENVIRONMENT.get_template('audio.html')
        self.response.write(template.render(template_values))
            
class videoView(webapp.RequestHandler):
    gqlQuery = blobstore.BlobInfo.gql("WHERE content_type IN ('video/mp4', 'video/ogg', 'video/wmv', 'video/avi', 'video/flv','video/mov') ORDER BY creation DESC")
    blobs = gqlQuery.fetch(20)
    
    def get(self):
        simplegallery_name = self.request.get('simplegallery_name',
                                          DEFAULT_simplegallery_NAME)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        link_image = 'images'
        url_image = 'image'
        link_video = 'videos'
        url_video = 'video'
        link_audio = 'audios'
        url_audio = 'audio'
        template_values = {
            'simplegallery_name': urllib.quote_plus(simplegallery_name),
            'url': url,
            'url_linktext': url_linktext,
            'url_video':url_video,
            'url_audio':url_audio,
            'url_image':url_image,
            'link_image':link_image,
            'link_video':link_video,
            'link_audio':link_audio,
            'blobs' : self.blobs,
        }
        template = JINJA_ENVIRONMENT.get_template('video.html')
        self.response.write(template.render(template_values))


            


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', simplegallery),
    ('/upload_form', UploadFormHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/preview', PreviewHandler),
    ('/page_not_found', PageNotFoundHandler),
    ('/upload', UploadHandler),
    ('/image', imgView),
    ('/video' , videoView),
    ('/audio' , audioView),
], debug=True)