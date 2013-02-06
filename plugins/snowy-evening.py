from util import hook, http, text
import json, urllib2
import re

snowy_re = (r'(?:snowy-evening.com/)'
              '([-_a-zA-Z0-9/]+)', re.I)


@hook.regex(*snowy_re)
def snowy(match, nick="", reply=""):
    owner, name, id, blankSpace = match.group(1).split("/")
    soup = http.get_soup("https://snowy-evening.com/%s/%s/%s" % (owner, name, id))

    header = soup.find('section', {'class': 'container'}).header.h2(text=True)[1].split(" ", 1)[1]
    reply("Project {} by {}: Issue #{}: {}".format(name, owner, id, text.truncate_str(header, 150)))
    stats = soup.find('ul', {'id':'stats'}).find_all('strong')
    if len(stats) == 6:
        priority, number, type, status, age, assignee = [i.contents[0].lower() for i in stats]
    else:
        priority, number, type, status, age = [i.contents[0].lower() for i in stats]

    if status == "assigned":
        reply("This issue has a priority of \x02{}\x02. It's age is \x02{}\x02 and it is a \x02{}\x02. This issue is \x02{}\x02 to \x02{}\x02.".format(priority, age, type, status, assignee))
    else:
        reply("This issue has a priority of \x02{}\x02. It's age is \x02{}\x02 and it is a \x02{}\x02. It's status is \x02{}\x02.".format(priority, age, type, status))