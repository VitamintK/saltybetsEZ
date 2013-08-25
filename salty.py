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
            if word == 'Dream' or word == 'Shaker':
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
            #prettifying 
            responsetest.set_data(responsoup.prettify())
            br.set_response(responsetest)
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

    with open("matches",'w') as p:
        pickle.dump(matchlist,p)

    with open('statspage','w') as p:
        p.write(str(soup))

    print "stats saved!"

def open_matches():
    with open('matches','r') as p:
        matches = pickle.load(p)
    return matches

def matches_ui(case_sensitive = False):
    """An infinite loop for the user to input 2 names to predict the winner  based on W/L, Elo, and previous matchups"""
    matchlist = open_matches()
    elos = open_elos()
    while True:
        name1 = raw_input("enter red name: ")
        name2 = raw_input("enter blue name: ")
        if name1 == 'q' and name2 == 'q':
            break
        find_match(name1,name2,matchlist,elos)
        notes_ui(name1,name2)

def find_match(name1,name2,matchlist=None,elos=None,case_sensitive = False):
    """The main method of this module enter two contestant's names to find out who will win.
    warning: speghetti contained within."""
    if matchlist is None:
        matchlist = open_matches()
    if elos is None:
        elos = open_elos()
    faceoff = False
    firstsecond = ([],[])
    elopair = []
    for match in matchlist:
        #if both contestants have battled previously
        #match = [x.lower() for x in match] #completely lowercase-ise each match
        if name1 in match and name2 in match:
            faceoff = match[2]
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
    print ""
    #print the conclusion based on difference in Elo ratings
    if elopair[0] - elopair[1] > 5:
        print "BET ON RED!"
        print_uq(name2,firstsecond[1],elos,elopair[0] - elopair[1])
        print "(" + str(elopair[0]) + " - " + str(elopair[1]) + " = " + str(elopair[0]-elopair[1]) + " difference in elo)" 
    elif elopair[1] - elopair[0] > 5:
        print "BET ON BLUE!"
        print_uq(name1,firstsecond[0],elos,elopair[1] - elopair[0])
        print "(" + str(elopair[1]) + " - " + str(elopair[0]) + " = " + str(elopair[1]-elopair[0]) + " difference in elo)" 
    else:
        print "TOO CLOSE TO CALL!"
    winprob = 1/(pow(10,(elopair[1]-elopair[0])/400) + 1)
    print "winpercentage of red: " + str(round(100*winprob,2)) + "%"
    print "(not liable for consequences)"
    if name1 == faceoff:
        print "REMATCH: " + faceoff + " WON!  BET ON RED!!!!!!!!!!!!!!!!!"
    elif name2 == faceoff:
        print "REMATCH: " + faceoff + " WON!  BET ON BLUE!!!!!!!!!!!!!!!!!"
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
    
    for match in reversed(matchlist):
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

def get_elo_rank(contestant,elos=None,elolist=None):
    if elolist:
        return elolist.index(contestant)
    elif elos:
        return list(elos).index(contestant)
    else:
        return list(open_elos()).index(contestant)
    
def test_elos(min_diff = 15, max_diff = None, min_elo = None, max_elo = None, min_rank = None, max_rank = None):
    """test the elo min_diff.  5 gives 87.5%.  10 gives 90.3%"""
    elos = open_elos()
    matches = open_matches()
    totals = 0
    corrects = 0
    for match in matches:
        moot = False
        redelo = get_elo(match[0],elos)
        blueelo = get_elo(match[1],elos)
        rmb = redelo-blueelo
        if rmb>min_diff:
            pred_winner = 0
        elif -1*rmb>min_diff:
            pred_winner = 1
        else:
            moot = True
        try:
            if match[0] == match[2]:
                actual_winner = 0
            else:
                actual_winner = 1
        except:
            moot = True
        if moot != True:
            totals+=1
            if actual_winner == pred_winner:
                corrects+=1
        if totals > 5000:
            #this does not change anything
            pass
            #break
    print str(totals) + " valid matches.  (the Elo difference was more than +/-" + str(min_diff)
    print str(corrects) + " matches that were correctly predicted by Elo. (Matches where the player with the higher Elo won.)"
    print float(corrects)/totals

def calculate_probability(elo1=None,elo2=None,name1=None,name2=None):
    """returns winrate probability of the contestant represented by elo1 or by name1"""
    if elo1 and elo2:
        return 1/(pow(10,(elo2-elo1)/400) + 1)
    elif name1 and name2:
        return 1/(pow(10,(get_elo(name2)-get_elo(name1))/400) + 1)
    else:
        return None

def add_notes(contestant1,contestant2 = None):
    """function to add notes for any contestant"""
    pass

def notes_ui(contestant1,contestant2):
    """UI to add notes for 2 contestants"""
    notes1 = raw_input("Add notes for " + contestant1 + ": ")
    notes2 = raw_input("Add notes for " + contestant2 + ": ")
    pass

def open_notes():
    """function to open the notes file"""
    pass

def get_note(contestant, notes = None):
    """function to get a note given the contestant"""
    pass
            
def calculate_lr():
    """Attempting to calculate winrates based off of logistic regression."""
    #AP Stats page 141, 209
    pass

def print_uq(contestant,matches=None,elos=None,diff_min = 5, diff_max = None):
    """print the upset quotient:
        determine the number of times this player has defeated someone with a higher elo than them.
        potential of this contestant to upset a higher ranked character
        used to determine,given that this character has a lower elo than another, what the chances are of an upset"""
    pts = 0
    upsets = 0
    total = 0 #total valid matches, not total overall
    #trivial, but intersting to me: the highest upset differential.  Maybe could be better represented with median/mean
    max_upset = 0
    if matches is None:
        matches = open_matches()
    if elos is None:
        elos = open_elos()
    for match in matches:
        if contestant in match:
            num_con = match.index(contestant)
            num_opp = 1 - num_con
            try:
                num_win = match.index(match[2])
            except:
                print "this match had no winner!"
            else:
                #con_win_perc = calculate_probability(name1=match[num_con],name2=match[num_opp])
                diff = get_elo(match[num_con],elos) - get_elo(match[num_opp],elos)
                #normalized = con_win_perc-.50
                if diff < -1* diff_min:
                    total+=1
                    #print match[0] + str(get_elo(match[0])) + " versus " + match[1] + str(get_elo(match[1]))
                    #print match[num_opp] + " was projected to win!"
                    #print match[2] + " won!"
                    if num_win == num_con:
                        max_upset = max(abs(diff),max_upset)
                        pts += diff * -1
                        upsets+=1
                        #print "UPSET!"
                    else:
                        pts += diff
                        #print "NO UPSET!"
    #print str(pts) + " points.  (algorithm is WIP)" useless stat for now
    print contestant + " won " + str(upsets) + " times when not favored to win"
    print contestant + " had " + str(total) + " times not favored to win"
    print "Highest difference in Elo upset: " + str(round(max_upset,2))

#def get_upsetted_quotient(contestant,matches=None):
 #   """determint the number of times this player has been defeated by someone with a lower elo than them"""
  #  pass

def get_all_upsets():
    pass

def run():
    matches_ui()
