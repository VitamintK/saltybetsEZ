from BeautifulSoup import *
with open('statspage','r') as p:
        soup = BeautifulSoup(p.read())
#find all tournaments with 'dream' in their name
tournaments = soup.findAll('a')
for hlink in tournaments:
    for d in hlink:
        print '{0}'.format(d)
