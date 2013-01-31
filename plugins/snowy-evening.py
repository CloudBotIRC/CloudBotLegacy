from util import hook, http, text
import json, urllib2
import re
from bs4 import BeautifulSoup

snowy_re = (r'(?:snowy-evening.com/)'
              '([-_a-zA-Z0-9/]+)', re.I)

			  
def stripStrongTags(text):
	return text.replace("<strong>", "").replace("</strong>", "")

			  
@hook.regex(*snowy_re)
def snowy(match, nick="", reply=""):
	try:
		
		soup = http.get_soup("https://snowy-evening.com/" + match.group(1))
		header = ''.join([unicode(tag) for tag in (soup.h2)]).replace("<span>Issue Details</span>", "")
		print(tag for tag in soup.find_all('p'))
		info = ''.join([unicode(tag) for tag in soup.find_all('p')[0]])
		if info.isspace() or not info or info == "":
			info = "No details found"
		stuff = soup.find_all('li', {'id':'proj-current'})[-1]
		owner, name = stuff.find_all('a')[-1]['href'].replace("https://snowy-evening.com/", '').split('/')
		reply("Project %s by %s: Issue %s - %s" % (name, owner, header, text.truncate_str(info, 150)))
		stats = soup.find_all('ul', {'id':'stats'}, text=True)
		priority, number, type, status, age, name = soup.find_all('strong', text=True)[:6]
		data = {
		"priority" : stripStrongTags(''.join(priority)),
		"number" : stripStrongTags(''.join(number)),
		"type" : stripStrongTags(''.join(type)),
		"status" : stripStrongTags(''.join(status)),
		"age" : stripStrongTags(''.join(age)),
		"name" : stripStrongTags(''.join(name))
		}
		reply("This issue has a priority of \x02{priority}\x02. It's age is \x02{age}\x02 and it is a \x02{type}\x02 and was created by \x02{name}\x02. It's status is \x02{status}\x02.".format(**data))	
	except Exception:
		raise