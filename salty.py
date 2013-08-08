import requests
import mechanize
from BeautifulSoup import *
br = mechanize.Browser()
import cookielib
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
url = "http://saltybet.com/authenticate?signin=1"

br.open(url)

"""payload = {'AnSwEr0001':'0.1'}
r = requests.post(url, payload)
with open("requests_results.html", "w") as f:
    f.write(r.content)
"""
br.select_form(nr=0)
br.form['email'] = ''
br.form['pword'] = ''
returns = br.submit()
returns.read()
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
