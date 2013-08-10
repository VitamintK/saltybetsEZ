import config as cf
import requests
import mechanize
from BeautifulSoup import *
br = mechanize.Browser()
import cookielib
import pickle
#tool to find matchup odds

online = True

"""technical stuff"""
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)
 
# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
"""end technical stuff"""

if online:
    url = "http://saltybet.com/authenticate?signin=1"
    resp = br.open(url)
    #use BeautifulSoup to prettify the html before running it through mechanize
    soup = BeautifulSoup(resp.get_data())
    resp.set_data(soup.prettify())
    br.set_response(resp)
    br.select_form(nr=0)
    br['email'] = cf.email
    br['pword'] = cf.pword
    returns = br.submit()
    url = "http://saltybet.com/stats"
    resp = br.open(url)
    #use BeautifulSoup to prettify the html before running it through mechanize
    soup = BeautifulSoup(resp.get_data())
    resp.set_data(soup.prettify())
    br.set_response(resp)
#assuming all tournaments with 'dream' in their name are mugen ai
else:
    with open('statspage','r') as p:
        soup = BeautifulSoup(p.read())
#find all tournaments with 'dream' in their name
tournaments = soup.findAll('a')
dreams = []
for hlink in tournaments:
    #print list(hlink.contents)[0] <-- for some reason this takes forever
    #print '{0}'.format(hlink.contents[0]) <-- for some reason this works!?!?!
    tourneyname = '{0}'.format(hlink.contents[0])
    for word in tourneyname.split():
        if word == 'Dream':
            print hlink
            print tourneyname
            dreams.append(hlink)
            break
#for dream in dreams:
for link in br.links():
    print link.text
    
#print soup
if online:
    #saves soup to file.  unneeded.
    with open('statspage','w') as p:
        p.write(str(soup))
if False:
    i = .01
    while i < 1:
        br.select_form(nr=0)
        br.form['AnSwEr0001']=str(i)
        rq = br.form.click("submitAnswers")
        asdf = br.open(rq)
        #print asdf.read()
        soup1 = BeautifulSoup(asdf.read())
        try:
            #print soup1.prettify()
            resul = soup1.find(None,"ResultsWithError")
            print resul
        except:
            print "ASDOFIJASDKJKJLOUDNOISES ASD;FOAJS;DLFKJAS;LDKFJ"
        i=i*1.009
        print i
else:
    pass
    #print returns
    """return
    for ans in SF.findAns([1,2,4,5,11]):
        br.select_form(nr=0)
        br.form['AnSwEr0001']=str(ans)
        rq = br.form.click("submitAnswers")
        asdf = br.open(rq)
        #print asdf.read()
        soup1 = BeautifulSoup(asdf.read())
        try:
            #print soup1.prettify()
            resul = soup1.find(None,"ResultsWithError")
            print resul
        except:
            print "ASDOFIJASDKJKJLOUDNOISES ASD;FOAJS;DLFKJAS;LDKFJ"
        print ans
"""
