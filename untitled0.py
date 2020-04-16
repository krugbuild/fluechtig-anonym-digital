#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 11:18:00 2020

@author: op
"""

#movies = [["citizen kane", 1941], ["Spirited Away", 2001], ["LotR", 2001]]
movies = [{"title":"citizen kane", "year":1941}
, {"title":"Spirited Away", "year":2001}
, {"title":"LotR", "year":2001}]

#pre2k = [(title, year) for [title, year] in movies if year > 2000 and title == "Spirited Away"]
pre2k = [str(year) for [title, year] in movies]# if year > 2000 and title == "Spirited Away"]

print(pre2k)

#a = {2: 'Turtle Doves', 3: 'French Hens', 4: 'Colly Birds', 5: 'Gold Rings', 6: 'Geese-a-Laying'}
#
#xyz = [0, 12, 4, 6, 242, 7, 9]
#
#known_things = sorted(set(a.iterkeys()).intersection(xyz))



#>>> unknown_things = sorted(set(xyz).difference(a.iterkeys()))
#>>>
#>>> for thing in known_things:
#...     print 'I know about', a[thing]
#...
#I know about Camel Books
#I know about Colly Birds
#I know about Geese-a-Laying
#I know about Swans-a-Swimming
#I know about Ladies Dancing
#>>> print '...but...'
#...but...
#>>>
#>>> for thing in unknown_things:
#...     print "I don't know what happened on the {0}th day of Christmas".format(thing)
#...
#I don't know what happened on the 12th day of Christmas
#I don't know what happened on the 242th day of Christmas