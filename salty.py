# -*- coding: cp1252 -*-
import config as cf
import requests
import mechanize
from BeautifulSoup import *
br = mechanize.Browser()
import cookielib
import pickle
from collections import OrderedDict
#tool to find matchup odds

online = True

def save_stats():
    """Retrieves all match stats from given illuminati account and saves them to statspage."""
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

    #find all tournaments with 'dream' in their name

    dreams = []
    for link in br.links():
        tourneyname = link.text
        for word in tourneyname.split():
            if word == 'Dream':
                print tourneyname
                dreams.append(link)
                break

    #iterate through each dream casino to create data
    matchlist = []
    for dream in dreams:
        responsetest = br.follow_link(dream)
        #I should really stop using infinite loops
        while True:
            responsoup = BeautifulSoup(responsetest.get_data())
            matches = responsoup.findAll('tr')
            for match in matches:
                span = match.findAll('span')
                try:
                    matchlist.append((span[0].text, span[1].text, span[2].text))
                except:
                    try:
                        matchlist.append((span[0].text, span[1].text))
                    except:
                        print span
            print "PRINTING LINKS"
            print ""
            #prettifying 
            responsetest.set_data(responsoup.prettify())
            br.set_response(responsetest)
            #if "Next" in (link.text for link in br.links()):
            #    print 'good shit'
            try:
                responsetest = br.follow_link(text='Next')
                print ""
                print "NEXT PAGE NEXT PAGE NEXT PAGE NEXT PAGE NEXT PAGE"
                print ""
            except:
                print ""
                print "NO MORE NO MORE NO MORE NO MOREN O MORE NO MORE NO MORE NORE MO"
                print ""
                break
                
            #THERES MORE PAGES
                    #THERES MORE PAGES
                    #THERES MORE PAGES
                    #NEXT BUTTON

    with open("matches",'w') as p:
        pickle.dump(matchlist,p)

    with open('statspage','w') as p:
        p.write(str(soup))

    print "stats saved!"

def open_matches():
    with open('matches','r') as p:
        matches = pickle.load(p)
    return matches

def find_matches(case_sensitive = False):
    matchlist = open_matches()
    elos = open_elos()
    while True:
        name1 = raw_input("enter first name: ")
        name2 = raw_input("enter second name: ")
        if name1 == 'q' and name2 == 'q':
            break
        faceoff = False
        firstsecond = ([],[])
        elopair = []
        for match in matchlist:
            #if both contestants have battled previously
            if name1 in match and name2 in match:
                faceoff = True
                print match[2] + " won!!!!!!!!!!!!!!"
                firstsecond[0].append(match)
                firstsecond[1].append(match)
            elif name1 in match:
                firstsecond[0].append(match)
            elif name2 in match:
                firstsecond[1].append(match)
        #if both contestants have not battled previously
        if faceoff is False:
            print "-------------"
            print name1 + " has not fought " + name2 + "."
        for i in 0,1:
            print "------------"
            wins = 0
            contestant = (name1,name2)[i]
            for match in firstsecond[i]:
                try:
                    if match[0] == match[2]:
                        winner = 0
                    else:
                        winner = 1
                    if match[winner] == contestant:
                        wins+=1
                    print match[2] + " beat " + match[1-winner]
                except:
                    print match
            try:
                winpercent = round(float(wins)/len(firstsecond[i]),1)
                rndelo = round(get_elo(contestant,elos),2)
            except:
                print contestant + " is new!"
                winpercent = -1
                rndelo = 1600
            print str(wins) + "/" + str(len(firstsecond[i])) + " : " + str(winpercent)
            print contestant + "'s ELO RATING: " + str(rndelo)
            elopair.append(rndelo)
        #print the conclusion based on difference in Elo ratings
        if elopair[0] - elopair[1] > 5:
            print "BET ON RED!"
        elif elopair[1] - elopair[0] > 5:
            print "BET ON BLUE!"
        else:
            print "TOO CLOSE TO CALL!"
        print "(not liable for consequences)"
        print ""
        
def elo_matches():
    """
    The ELO System:

    All new players start out with a base rating of 1600
    WinProbability = 1/(10^(( Opponent’s Current Rating–Player's Current Rating)/400) + 1)
    ScoringPt = 1 point if they win the match, 0 if they lose, and 0.5 for a draw.
    Player's New Rating = Player's Old Rating + (K-Value * (ScoringPt–Player's Win Probability))
    """
    kval = 16
    playerlist = {}
    matchlist = open_matches()
    
    for match in matchlist:
        for i in 0,1:
            player = match[i]
            if player not in playerlist:
                playerlist[player] = 1600
        for i in 0,1:
            player = match[i]
            winprob = 1/(pow(10,(playerlist[match[1-i]]-playerlist[player])/400) + 1)
            try:
                if player == match[2]:
                    scoringpt = 1
                else:
                    scoringpt = 0
            except:
                scoringpt = .5
            playerlist[player] = playerlist[player] + (kval * (scoringpt - winprob))
            #print player + " new rating is " + str(playerlist[match[i]])
    return playerlist

def save_elos():
    elos = elo_matches()
    sorted_elos = OrderedDict(sorted(elos.items(),key = lambda x: x[1]))
    with open("elos",'w') as p:
        pickle.dump(sorted_elos,p)
    print "elos saved!"

def open_elos():
    with open("elos",'r') as p:
        elos = pickle.load(p)
    return elos

def print_elos(batches = 100):
    try:
        sorted_elos = open_elos()
    except:
        save_elos()
        sorted_elos = open_elos()
    j = 0
    for i in reversed(sorted_elos):
        j+=1
        print i + ": " + str(round(sorted_elos[i],2))
        if j%batches == 0:
            if raw_input('go on?') == 'n':
                break

def get_elo(contestant,elos=None):
    if elos is None:
        elos = open_elos()
    return elos[contestant]

def find_elos():
    elos = open_elos()
    while True:
        contestant = raw_input('Contestant name? ')
        print contestant + ": " + str(round(elos[contestant],2))

def save_all():
    save_stats()
    save_elos()
