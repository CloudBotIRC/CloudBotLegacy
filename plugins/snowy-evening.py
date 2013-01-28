from util import hook, http, text
import json, urllib2
import re

snowy_re = (r'(?:snowy-evening.com/)'
              '([-_a-zA-Z0-9/]+)', re.I)

			  
def stripStrongTags(text):
	return text.replace("<strong>", "").replace("</strong>", "")

			  
@hook.regex(*snowy_re)
def snowy(match, nick="", reply=""):
	try:
	
		owner, name, id, nothing = match.group(1).split("/")
		soup = http.get_soup("https://snowy-evening.com/%s/%s/%s" % (owner, name, id))
		header = ''.join([unicode(tag) for tag in (soup.h2)])
		header = header.replace("<span>Issue Details</span>", "").replace("#%s " % id, "")
		info = soup.find_all('p', text=True)[0]
		info = ''.join([unicode(tag) for tag in info])
		if info.isspace():
			info = "No details found"
	
		reply("Project %s by %s: Issue #%s: %s - %s" % (name, owner, id, header, text.truncate_str(info, 150)))
		stats = soup.find_all('ul', {'id':'stats'}, text=True)
	
		priority, number, type, status, age, other = soup.find_all('strong', text=True)
	
		data = {
		"priority" : stripStrongTags(''.join(priority)),
		"number" : stripStrongTags(''.join(number)),
		"type" : stripStrongTags(''.join(type)),
		"status" : stripStrongTags(''.join(status)),
		"age" : stripStrongTags(''.join(age))
		}
		reply("This issue has a priority of \x02{priority}\x02. It's age is \x02{age}\x02 and it is a \x02{type}\x02. It's status is \x02{status}\x02.".format(**data))	
	except Exception:
		reply("An error occured while trying to retrieve the data.")
		raise