import requests, re
from bs4 import BeautifulSoup

class Hermes:
    def __init__(self):
        self.URL = "https://www.tfrrs.org/"
    

    def get_roster(self, state, team_name, gender, season):
        team_html = self.get_team_html(state, team_name, gender, season)
        roster_rows = self.get_roster_table(team_html)
        roster = []
        for athlete_info in roster_rows:
            name = athlete_info.find_all('td')[0].text.strip()
            year = athlete_info.find_all('td')[1].text.strip()
            roster.append({'name':name, 'year':year})
        return roster
    
    def get_athlete_bests(self, name, state, team_name, gender, season):
        athlete_html = self.get_athlete_html(name, state, team_name, gender, season)
        table_bests = athlete_html.find("table", class_="table bests")
        rows = table_bests.find_all("td")
        bests = {}
        for i in range(0,len(rows), 2):
            bests[self.remove_spaces(rows[i].text)] = self.remove_spaces(rows[i+1].text)
        return bests


    def get_athlete_html(self, name, state, team_name, gender, season):
        team_html = self.get_team_html(state, team_name, gender, season)
        roster_rows = self.get_roster_table(team_html)
        for athlete_info in roster_rows: # does a look up of the athlete by name
            if name == athlete_info.find_all('td')[0].text.strip().replace(', ','_'):
                athlete_url = self.URL + athlete_info.find_all('a')[0]['href']
                break
        return self.get_soup(athlete_url)

    def get_soup(self, url): # gets html with beautiful soup
        page = requests.get(url)
        return BeautifulSoup(page.content, "html.parser")

    def get_year_keys(self, state, team_name, gender): # for getting the key "configure_hnd" so we can get the html page from a certain year
        soup = self.get_soup(self.URL + f'teams/{state.upper()}_college_{gender.lower()}_{team_name}.html')
        form_control = soup.find("select", class_="form-control")
        year_info = form_control.find_all("option")
        year_info.pop(0) # dictionary comprehension to get the keys and values for the years
        return {year.text.strip().replace('NCAA','').replace(' ','_').replace('__','_') : str(year).split('"')[1] for year in year_info}
        
    def get_team_html(self, state, team_name, gender, season):
        year_keys = self.get_year_keys(state, team_name, gender)
        page_url = self.URL + f'teams/{state.upper()}_college_{gender.lower()}_{team_name}.html'
        page_url += f'?config_hnd={year_keys[season]}'
        return self.get_soup(page_url)

    def get_roster_table(self, html):
        html_tables = html.find_all("table", class_="tablesaw")
        for table in html_tables: # there are multiple tables on some pages especially with track teams
            if table.find('th').text.strip() == 'NAME': # athlete table has a header with NAME
                roster_table = table
        roster_rows = roster_table.find_all("tr")
        roster_rows.pop(0) # pop the first item in the list because it is just NAME and YEAR
        return roster_rows

     
    def remove_spaces(self, string):
        pattern = re.compile(r'\s+')
        return re.sub(pattern, '', string)

