#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Braňo Žarnovičan'
SITENAME = u'Braňo Žarnovičan\'s blog'
SITEURL = ''

PATH = 'content'
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)'
ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

TIMEZONE = 'Europe/Prague'

DEFAULT_LANG = u'en'

MD_EXTENSIONS = ['codehilite(noclasses=True,guess_lang=False)', 'extra', 'admonition', 'toc']

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = (
    ('zarnovican@github', 'http://github.com/zarnovican'),
    ('zarnovican@linkedin', 'https://cz.linkedin.com/in/brano-zarnovican-79a5397'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

PLUGIN_PATHS = ['/home/zarnovic/git/pelican-plugins']
PLUGINS = ['tag_cloud']
TAG_CLOUD_SORTING = 'alphabetically'
TAG_CLOUD_STEPS = 2

THEME = '/home/zarnovic/git/pelican-themes/pelican-bootstrap3'
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_TAGS_ON_SIDEBAR = True
BOOTSTRAP_THEME = 'flatly'
CUSTOM_CSS = 'static/custom.css'
STATIC_PATHS = ['static']

