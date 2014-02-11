# -*- coding: utf-8 -*-
import mechanize
from mechanize import ParseResponse
from BeautifulSoup import BeautifulSoup
import re
import sqlite3
import sys

#datenbank öffnen
conn = sqlite3.connect('items.db')
c = conn.cursor()

def fetch_data():
	#Cookie holen
	request  = mechanize.Request("http://www.lachschon.de/site/login/")

	#HTML Forms auslesen
	response = mechanize.urlopen("http://www.lachschon.de/site/login/")

	forms = ParseResponse(response, backwards_compat=False)
	form  = forms[1]

	#Login Daten einsetzen
	form.set_value("BigBANG", name="login_username")
	form.set_value("******", name="login_password")

	#Absetzen des Formulars
	request  = form.click()
	response = mechanize.urlopen(request)
	#~ print(response.read())


	response=mechanize.urlopen("http://www.lachschon.de/admin/item/councilHistory/");

	soup = BeautifulSoup(response)

	soup = soup.findAll("div", {"class": "item"})


	for item in soup:
		datum = ""
		titel = ""
		einsender = ""
		rdw = []
		rdw_names = []
		for element in item:
			if "<label>Titel</label>" in unicode(element):
				count = 0
				for line in element:
					if count == 2:
						titel += line
						titel = titel.replace("\t", "").replace("\n", "").encode("utf-8")
						# print(titel)
						break
					count = count + 1
			
			elif "<label>Einsender</label>" in unicode(element):
				count = 0
				for line in element:
					if count == 2:
						einsender += line
						einsender = einsender.replace("\t", "").replace("\n", "").replace(" (registrierter Benutzer)", "").encode("utf-8")
						# print(einsender)
						break
					count = count + 1
			
			elif "<label>RDW-Votes</label>" in unicode(element):
				count = 0
				for line in element:
					if count == 3:
						rdw = line.contents
						rdw = [str(rdw[1]), str(rdw[3]), str(rdw[5])]
						regex = re.compile('<a.*">')
						
						for name in rdw:
							name = name.replace("</a>", "")
							pattern = re.search(regex, name)
							if pattern:
								name = name.replace(pattern.group(0), "")
						
							# print(name)
							rdw_names.append(name)
						
						break
					count = count + 1
					
			elif "<label>Eingesendet am</label>" in unicode(element):
				count = 0
				for line in element:
					if count == 3:
						datum += line.string.replace("<div>", "").replace("</div>", "").encode("utf-8")
						# print(datum)
						break
					count = count + 1
		
		c.execute('SELECT * FROM items WHERE date = \"' + datum + "\"")

		if c.fetchone() is None:
			dates.append(datum)
			titles.append(titel)
			submitter.append(einsender)
			rdws.append(rdw_names)
			
	


def post_data_in_thread():
	#Cookie holen
	request  = mechanize.Request("http://www.lachschon.de/site/login/")

	#HTML Forms auslesen
	response = mechanize.urlopen("http://www.lachschon.de/site/login/")

	forms = ParseResponse(response, backwards_compat=False)
	form  = forms[1]

	#Login Daten einsetzen
	form.set_value("LachBot", name="login_username")
	form.set_value("******", name="login_password")

	#Absetzen des Formulars
	request  = form.click()
	response = mechanize.urlopen(request)
	#~ print(response.read())


	response=mechanize.urlopen("http://www.lachschon.de/forum/thread/show/49975/");

	forms = ParseResponse(response, backwards_compat=False)
	form = forms[1]
	form.set_value(forum_post, id="id_post")
	request = form.click()
	response = mechanize.urlopen(request)



dates = []
titles = []
submitter = []
rdws = []

sql_commands = []

forum_post = ""

fetch_data()


if len(dates) != 0:

	for i in xrange(len(dates)):
		sql_commands.append("INSERT INTO items VALUES ('" + dates[i] + "','" + titles[i] + "','" + submitter[i] + "','" + rdws[i][0] + "','" + rdws[i][1] + "','" + rdws[i][2] + "')");
		forum_post += "\n"
		forum_post += "[b]Einsendung:[/b] \"" + titles[i] + "\" "
		forum_post += "[b]am[/b] " + dates[i] + "\n"
		forum_post += "[b]von:[/b] " + submitter[i] + "\n"
		forum_post += "[b]wurde gelöscht von:[/b]" + "\n"
		forum_post += rdws[i][2] + "\n"
		forum_post += rdws[i][1] + "\n"
		forum_post += rdws[i][0] + "\n"
		
	
	print("creating new post")
	post_data_in_thread()
	
	for cmd in sql_commands:
		c.execute(cmd)
		conn.commit()
	
else:
	print("didnt even join lol")


print("done!")

