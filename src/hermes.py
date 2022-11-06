import requests, re
from bs4 import BeautifulSoup
from src.errors import NoAthleteFoundException

class Hermes:
    def __init__(self):
        """
        A class used to webscrape TFRRS. It has various methods for retrieving important information
        regarding XC/TF teams and athletes.

        Attributes
        ----------
        URL : str
            The url for tffrs which will be added to depending on a specific method being used.
        """
        self.URL = "https://www.tfrrs.org/"
    

    def get_roster(self, state, team_name, gender, season):
        """
        This will scrape through the html and retrieve the roster for a specified team.
        Will call the get_team_html method given, the state, team_name, gender, and season.

        Parameters
        ----------
        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        season : str
            the season for the roster (*year*_Cross_Country, *year*_Indoor, or *year*_Outdoor)

        Returns
        -------
        list
            List of dictionaries containing athlete information
        """
        team_html = self.get_team_html(state, team_name, gender, season)
        roster_table = self.get_table_by_heading(team_html, 'NAME')
        roster = get_table_data(roster_table)[1:]
        return roster

    def get_top_performances(self, state, team_name, gender, season):
        """
        This will retrieve top performances from the team html
        Parameters
        ----------
        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        season : str
            the season for the roster (*year*_Cross_Country, *year*_Indoor, or *year*_Outdoor)

        Returns
        -------
        list
            list of dictionaries containing list of performances
        """
        team_html = self.get_team_html(state, team_name, gender, season)
        table = self.get_table_by_heading(team_html, 'EVENT') #getting top performance table by the EVENT heading, hackish ik.
        performances = get_table_data(table)
        performances.pop(0)
        return performances
    
    def get_athlete_bests(self, name, state, team_name, gender, season):
        """
        This will scrape through the html of the athlete and return their personal bests for any event they do.
        Will call get_athlete_html method to retrieve the html.

        Parameters
        ----------
        name : str
            The name of the athlete (Last_First)

        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        season : str
            the season for the roster (*year*_Cross_Country, *year*_Indoor, or *year*_Outdoor)

        Returns
        -------
        dict
            A dictionary of the athlete's best marks
        """
        athlete_html = self.get_athlete_html(name, state, team_name, gender, season)
        table_bests = athlete_html.find("table", class_="table bests")
        rows = table_bests.find_all("td")
        bests = {}
        for i in range(0,len(rows), 2):
            event = remove_whitespace(rows[i].text)
            mark = remove_whitespace(rows[i+1].text).strip('\\"').replace('m', 'm ') #hackish way of spacing metric and standard
            if event != "" or mark != "":
                bests[event] = mark
        return bests

    def get_athlete_results(self, name, state, team_name, gender, season):
        """
        This will scrape through the html of the athlete and return history of performances.
        This will return the information on when and where the performance was and the mark and placement for the athlete.
        Will call get_athlete_html method to retrieve the html.

        Parameters
        ----------
        name : str
            The name of the athlete (Last_First)
            
        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        season : str
            the season for the roster (*year*_Cross_Country, *year*_Indoor, or *year*_Outdoor)
        
        Returns
        -------
        list
            list of dictionaries containing meet dates, names, and lists of performance results
        """

        info_keys = ['event', 'result', 'place']
        meet_results  = []
        athlete_html = self.get_athlete_html(name, state, team_name, gender, season)
        meet_results_tables = athlete_html.find(id="meet-results").find_all("table")
        for meet_table in meet_results_tables:
            # there are some divs in athlete results to specify whether they transferred or not, resulting in a None.
            if meet_table.find("thead") is not None:
                title = meet_table.find("thead").text.strip().replace('\xa0\xa0\xa0', '')
                meet_name, date = title.split('\n')
                meet_info = {}
                meet_info['meet_name'] = meet_name
                meet_info['date'] = date
                meet_info['performances'] = get_table_data(meet_table, info_keys)[1:] #set the keys manually because these tables do not have headers
                meet_results.append(meet_info)
        return meet_results

    def get_meets(self): #can this use general get data function?
        info_keys = ['date', 'meet_name', 'sport', 'state']
        meets_html = self.get_soup(self.URL+'results_search.html')
        meets_table = meets_html.find("table")
        meets = get_table_data(meets_table)[1:]
        return meets

    def get_meet_results(self, meet_name, gender):
        meets_html = self.get_soup(self.URL+'results_search.html') # because this page has very limited results it will not be able to find every meet
        rows = meets_html.find_all("tr")[1:]
        link = ''
        for row in rows:
            row_data = row.find_all('td')
            if row_data[1].text.strip() == meet_name:
                link = row.find('a')['href'].strip()
                break
        link = link.split('NCAA')
        meet_html = self.get_soup(f'http:{link[0]}{gender}/{link[1]}') # reformatting the url to get the gender we want
        table_containers = meet_html.find_all('div', class_='col-lg-12')
        events = []
        for table_cont in table_containers:
            event = {}
            event_name = table_cont.find('div', class_='custom-table-title').text.strip().split('\n')
            event['name'] = f'{event_name[0]} {event_name[1]}' # doing this so we don't lose info on whether its a final or prelim
            table = table_cont.find('table')
            event['results'] = get_table_data(table, same_size=True) # set same_size to true bc we don't want fouls or what happened on field event attempts
            events.append(event)
        return events

    def get_soup(self, url): # gets html with beautiful soup
        """
        This will use the requests library to retrieve the html from a url.
        The BeautifulSoup library will parse the html to be processed.

        Parameters
        ----------
        url : str
            the url to a webpage

        Returns
        -------
        soup obj
            the soup obj of the webpage html
        """
        page = requests.get(url)
        return BeautifulSoup(page.content, "html.parser")

    def get_athlete_html(self, name, state, team_name, gender, season):
        """
        This will retrieve the html for a particular athlete on the Tfrrs website.
        An athlete needs to be looked up by their team first, so their team html is first retrieved.

        Parameters
        ----------
        name : str
            The name of the athlete (Last_First)
            
        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        season : str
            the season for the roster (*year*_Cross_Country, *year*_Indoor, or *year*_Outdoor)

        Returns
        -------
        soup obj
            the soup obj of the webpage html
        """
        team_html = self.get_team_html(state, team_name, gender, season)
        roster_rows = self.get_table_by_heading(team_html, 'NAME')
        athlete_url = ''
        for athlete_info in roster_rows('td'): # does a look up of the athlete by name
            if name == remove_whitespace(athlete_info.text).replace(',', '_'):
                athlete_url = self.URL + athlete_info('a')[0]['href']
                return self.get_soup(athlete_url)  
                
        raise NoAthleteFoundException(name)
        
    def get_year_keys(self, state, team_name, gender): # for getting the key "configure_hnd" so we can get the html page from a certain year
        """
        This method is essential for finding the team on a given year. Tffrs has values for each team and their corresponding
        season. ie (2022_Cross_Country : 330)
        This method first gets the most recent html page for a team and then finds a previous season and its value then
        will return dictionary of the seasons and their values.
        Parameters
        ----------
        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        Returns
        -------
        dict
            Season and its values
        """
       
        soup = self.get_soup(self.URL + f'teams/{state.upper()}_college_{gender.lower()}_{team_name}.html')
        form_control = soup.find("select", class_="form-control")
        if form_control is None:
            raise NoTeamFoundException(team_name)
        year_info = form_control.find_all("option")
        year_info.pop(0) # dictionary comprehension to get the keys and values for the years
        return {year.text.strip().replace('NCAA','').replace(' ','_').replace('__','_') : str(year).split('"')[1] for year in year_info}
        
        
    def get_team_html(self, state, team_name, gender, season):
        """
        This will retrieve the html for a particular season for a team on the Tfrrs website.

        Parameters
        ----------
        state : str
            state where the school is located. (There can be multiple universities with the same name)
        
        team_name : str
            the name of the school
        
        gender : str
            specifies whether we are trying to retrieve men or women's team

        season : str
            the season for the roster (*year*_Cross_Country, *year*_Indoor, or *year*_Outdoor)

        Returns
        -------
        soup obj
            the soup obj of the webpage html
        """
        try:
            page_url = self.URL + f'teams/{state.upper()}_college_{gender.lower()}_{team_name}.html'
            year_keys = self.get_year_keys(state, team_name, gender) # retrieve the value for the season we want to find
            page_url += f'?config_hnd={year_keys[season]}'
            return self.get_soup(page_url)
        except NoTableFoundException:
            raise NoTeamFoundException(team_name)

    def get_table_by_heading(self, html, heading):# TODO: update docs
        """ 
        Returns the table rows for a table given team page html and a heading.

        Parameters
        ----------
        html : soup obj
            The html of a specified team page

        Returns
        -------
        list
            list of table rows
        """
        
        html_tables = html.find_all("table", class_="tablesaw")
        for table in html_tables: # there are multiple tables on some pages especially with track teams
            if table.find('th').text.strip() == heading: # we are identifying the table by a header definitely a hack
                return table
        raise NoTableFoundException(heading)


class NoAthleteFoundException(Exception):
    def __init__(self, name):
        self.message = f"Athlete: {name}, could not be found"
        super().__init__(self.message)

class NoTeamFoundException(Exception):
    def __init__(self, team_name):
        self.message = f"Team: {team_name}, could not be found"
        super().__init__(self.message)


class NoTableFoundException(Exception):
    def __init__(self, heading):
        self.message = f"Table with heading: {heading}, could not be found"
        super().__init__(self.message)


def remove_whitespace(string):
    """
    removes whitespace characters like \n and \t 

    Paramters
    ---------
    string : str
        string we want to remove white space from

    Returns
    -------
    str
        string stripped of whitespace
    """
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', string)


def get_table_data(table, keys=None, same_size=False): # general function idea
    collection = []
    table_head = table.find('thead') 
    if keys is None:
        headers = table_head.find_all('th')
        keys = [remove_whitespace(header.text).lower() for header in headers]

    rows = table.find_all("tr")
    for row in rows:
        info = {}
        row = row.find_all("td")
        for i in range(len(row)): # should this be zip?
            info[keys[i]] = row[i].text.replace('\xa0\n', '').replace('\n',' ').replace('           ', ' ').strip('\\"').strip()
        if ((same_size and len(row) == len(keys)) or not same_size): #same size enforces that the data found and the keys we want need to be the same size. This is helpful for avoiding information on tables you dont want.
            collection.append(info)
    return collection
