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
            event = self.remove_spaces(rows[i].text)
            mark = self.remove_spaces(rows[i+1].text).strip('\\"').replace('m', 'm ') #hackish way of spacing metric and standard
            if event != "" or mark != "":
                bests[event] = mark
        return bests

    def get_athlete_results(self, name, state, team_name, gender, season):
        info_keys = ['event', 'result', 'place', 'final']
        meet_results  = []
        athlete_html = self.get_athlete_html(name, state, team_name, gender, season)
        meet_results_table = athlete_html.find(id="meet-results").find_all("div")
        for meet in meet_results_table:
            # there are some divs in athlete results to specify whether they transferred or not, resulting in a None.
            if meet.find("thead") is not None:
                title = meet.find("thead").text.strip().replace('\xa0\xa0\xa0', '')
                meet_name, date = title.split('\n')
                meet_info = {}
                meet_info['meet_name'] = meet_name
                meet_info['date'] = date
                table_row = meet.find_all("tr")
                meet_info['performances'] = []
                for perf in table_row:
                    perf_info = {}
                    table_data = perf.find_all("td")
                    if table_data != []:
                        table_data = [data.text.strip() for data in table_data]
                        for i in range(len(table_data)):
                            perf_info[info_keys[i]] = table_data[i].replace('\xa0\n', '').replace('\n',' ').strip('\\"')
                        meet_info['performances'].append(perf_info)
                meet_results.append(meet_info)
        return meet_results

    def get_soup(self, url): # gets html with beautiful soup
        page = requests.get(url)
        return BeautifulSoup(page.content, "html.parser")

    def get_athlete_html(self, name, state, team_name, gender, season):
        team_html = self.get_team_html(state, team_name, gender, season)
        roster_rows = self.get_roster_table(team_html)
        for athlete_info in roster_rows: # does a look up of the athlete by name
            if name == athlete_info.find_all('td')[0].text.strip().replace(', ','_'):
                athlete_url = self.URL + athlete_info.find_all('a')[0]['href']
                break
        return self.get_soup(athlete_url) # TODO: raise exception if html not found, athlete dne or is not on the roster this season

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
