import pdb
import urllib2
from bs4 import BeautifulSoup

class PlayByPlayEvent:
    """ Represents a single event occurring during gameplay """
    home_players = {}
    away_players = {}
    event_type = ""
    event_details = ""
    period = ""
    event_number = ""
    time_elapsed = ""
    time_remaining = ""
    strength = ""

    def __str__(self):
        s = "Event number: " + self.event_number + "\nPeriod: " + self.period
        s += "\nStrength: " + self.strength + "\nTime remaining: " + self.time_remaining
        s += "\nTime elapsed: " + self.time_elapsed + "\nEvent Type: " + self.event_type
        s += "\nDetails: " + self.event_details + "\nHome players: \n"
        for key in self.home_players.keys():
            s += "(" + key + ") : " + self.home_players[key] + "\n"
        s += "Away players: \n"
        for key in self.away_players.keys():
            s += "(" + key + ") : " + self.away_players[key] + "\n" 
        return s

class PlayByPlayScraper:
    """ Scrape and nhl.com play by play sheet to extract that data in a meaningful fashion. """

    def parseOnIce(self, elem):
        rows = elem.findChildren("font")

        players = {}
        for row in rows:
            player_number = row.contents[0].encode('utf-8').strip()
            player_details = row["title"].encode('utf-8').strip()
            players[player_number] = player_details
        return players

    def parseEventDetails(self, elem):
        """ For now, just return the string.  In the future, get smart. """
        return elem.contents[0].encode('utf-8').strip()

    def parseEventType(self, elem):
        """ For now, just return the string. In the future, do real work here. """
        return elem.contents[0].encode('utf-8').strip()

    def parseEventRow(self, row):
        event = PlayByPlayEvent()
        #print row.prettify()
        elems = row.findChildren("td", { "class" : " + bborder"})
        # even number.
        event_number = elems[0].contents[0].encode('utf-8').strip()
        event.event_number = event_number
        # period.
        period = elems[1].contents[0].encode('utf-8').strip()
        event.period = period

        # strength
        strength = elems[2].contents[0].encode('utf-8').strip()
        event.strength = strength

        # time elapsed
        time_elapsed = elems[3].contents[0].encode('utf-8').strip()
        time_remaining = elems[3].findChildren("br")[0].contents[0].encode('utf-8').strip()
        event.time_elapsed = time_elapsed
        event.time_remaining = time_remaining

        event_type = self.parseEventType(elems[4])
        event.event_type = event_type

        event_details = self.parseEventDetails(elems[5])
        event.event_details = event_details

        hoi_elem = row.findChildren("td", { "class" : " + bborder + rborder"})[0]
        home_on_ice = self.parseOnIce(hoi_elem)
        event.home_players = home_on_ice

        away_on_ice = self.parseOnIce(elems[6])
        event.away_players = away_on_ice

        return event

    def scrape(self, url):
        """ 
            Here's the general algorithm...
            - perform these actions for EACH <table> within <body>
            - hit each <tr class="evenColor">
        """
        events = []
        soup = BeautifulSoup(urllib2.urlopen(url).read())

        # this .findChildren is giving off way too many false positives. must be a better call here. [todo]
        tables = soup.findChildren("table")
        data_tables = []
        for table in tables:
            if table.findParent("table") is None:
                data_tables.append(table)
        print "count: ", len(data_tables)
        print "other count: ", len(tables)

        # parse out individual rows.
        for table in data_tables:
            rows = table.findAll("tr", { "class" : "evenColor"})
            print "row count: ", len(rows)
            for row in rows:
                event = self.parseEventRow(row)
                print event
                events.append(event)
                #pdb.set_trace()

        return events

if __name__ == '__main__':
    scraper = PlayByPlayScraper()
    events = scraper.scrape("http://www.nhl.com/scores/htmlreports/20132014/PL030316.HTM")
    #print contents