#!/usr/bin/env python
#
# Copyright 2010 drikin.com

import os
import os.path
import re
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from xml.etree import ElementTree

import simplejson as json
import flickrapi

api_key = os.environ.get('FLICKR_API', "")
# flickr = flickrapi.FlickrAPI(api_key)
flickr = flickrapi.FlickrAPI(api_key, format='etree')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/" + "index" + ".html")

class SlideShowHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/" + "slideshow" + ".html")

class RedirectUserHandler(tornado.web.RequestHandler):
    def get(self):
        src = self.get_argument("src")
        user = flickr.urls_lookupuser(url=src)
        id = user[0].attrib['id']

        size = self.get_argument("size")
        if not size:
        	size = 'm'

        try:
            photoset_id = self.get_argument("photoset_id")
            if photoset_id:
                photoset_url = "&photoset_id=" + photoset_id
            else:
                photoset_url = ''
        except:
            photoset_url = ''

        if id:
            if settings["debug"]:
                url = "http://127.0.0.1:8080/?query=" + id + "&size=" + size + photoset_url
            else:
                url = "http://flickr2tag.drikin.com/?query=" + id + "&size=" + size + photoset_url
            self.redirect(url)

class RedirectGroupHandler(tornado.web.RequestHandler):
    def get(self):
        src = self.get_argument("src")
        group = flickr.urls_lookupgroup(url=src)
        id = group[0].attrib['id']

        size = self.get_argument("size")
        if not size:
        	size = 'm'

        if id:
            if settings["debug"]:
                url = "http://127.0.0.1:8080/?query=" + id + "&size=" + size
            else:
                url = "http://flickr2tag.drikin.com/?query=" + id + "&size=" + size
            self.redirect(url)

class RedirectPhotoSetHandler(tornado.web.RequestHandler):
    def get(self):
        src = self.get_argument("src")
        user = flickr.urls_lookupuser(url=src)
        id = user[0].attrib['id']

        size = self.get_argument("size")
        if not size:
        	size = 'm'

        if id:
            if settings["debug"]:
                url = "http://127.0.0.1:8080/?query=" + id + "&size=" + size
            else:
                url = "http://flickr2tag.drikin.com/?query=" + id + "&size=" + size
            self.redirect(url)

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        photoset_id = self.get_argument("photoset_id", None)
        query = self.get_argument("query")
        page = self.get_argument("page", 1)
        p_size = self.get_argument("size", 'Medium')

        if photoset_id:
            photos = flickr.photosets_getPhotos(photoset_id=photoset_id, per_page='10', page=page, extras='description')
            print(photos)
        elif re.match(r'^\d+@N\d+$', query):
            try:
                photos = flickr.photos_search(user_id=query, per_page='10', page=page, extras='description')
            except:
                photos = flickr.photos_search(group_id=query, per_page='10', page=page, extras='description')
        else:
            photos = flickr.photos_search(text=query, per_page='10', page=page)
        
        responses = []
        for photo in photos[0]:
            id = photo.attrib['id']
            title = photo.attrib['title']
            try:
                description = photo.find('description').text
            except:
                description = None
            sizes = flickr.photos_getsizes(photo_id=id)
            for size in sizes[0]:
                if size.attrib['label'] == p_size:
                    try:
                        # print size.attrib['source']
                        resp = {}
                        resp['id']            = id
                        resp['title']        = title
                        resp['description']    = description
                        resp['width']   = size.attrib['width']
                        resp['height']  = size.attrib['height']
                        resp['label']        = size.attrib['label']
                        resp['url']            = size.attrib['url']
                        resp['source']     = size.attrib['source']
                        responses.append(resp)
                    except:
                        pass

        self.write(json.dumps(responses))
        

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "xsrf_cookies": True,
    "debug": True if os.path.exists("/Users") else False,
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/slideshow.html", SlideShowHandler),
    (r"/api/redirectuser", RedirectUserHandler),
    (r"/api/redirectgroup", RedirectGroupHandler),
    (r"/api/redirectphotoset", RedirectPhotoSetHandler),
    (r"/api/search", SearchHandler),
], **settings)

if settings["debug"]:
    define("port", default=8080, help="run on the given port", type=int)
else:
    define("port", default=51001, help="run on the given port", type=int)

def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":
    main()
