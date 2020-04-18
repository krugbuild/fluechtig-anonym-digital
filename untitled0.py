#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 11:17:06 2020

@author: op
"""

import csv
import ast

#def writeDataCSV(data, path, header):
#    with open(path, 'w', newline='') as csvfile:
#        writer = csv.writer(csvfile)
#        print("schreibe .. " + csvfile.name)
#        writer.writerow(header)
#        for line in data:
#            writer.writerow(line)
#
#def readDataCSV(path):
#    with open(path, 'r', newline='') as csvfile:
#        reader = csv.reader(csvfile)
#        header = next(reader)
#        print("lese .. " + csvfile.name + " - header: " + str(header))
#        data = [[row[0], ast.literal_eval(row[1]), row[2]] for row in reader]
##        data = list()
##        for row in reader:
##            data.append([row[0], ast.literal_eval(row[1]), row[2]])
#        return data
#
#liste = [['stefan', {"en":1,}, "user"], ['sören', {"en":1, "zh":1}, "user"],['stefan', {"en":1,}, "user"], ['sören', {"en":1, "zh":1}, "user"]]
#
#print(liste[0][1].get("zh", 0))
#
#zh = "de"
#stuff = {zh:1, "en":1}
#
#for item in liste:
#    if item[1]["en"] == 1:
#        zh = "en"
#        item[1][zh] = 0
#        
#print(liste)
#
#writeDataCSV(liste, "dicttest.csv", ["name", "lang", "type"])
#
#
#list2 = readDataCSV("dicttest.csv")
#
#print(list2)





languages = [{'zh': 1}, {'en': 1}, {'en': 1}, {'zh': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'zh': 1}, {'en': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'en': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}, {'zh': 1}]

lang1 = {'en':1}
en = lang1.get('en', 0)
zh = lang1.get('zh', 0)

#
for item in languages:
    en += item.get('en', 0)
    zh += item.get('zh', 0)
    
lang1 = {'en': en, 'zh': zh}

langvalue = lang1.get('en', 0) / (lang1.get('en', 0) + lang1.get('zh', 0))
if langvalue > 0.5:
    print("blue")





















