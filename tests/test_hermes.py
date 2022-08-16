# from hermes import Hermes
from bs4 import BeautifulSoup
from src.hermes import Hermes

urls = {
    'https://www.tfrrs.org/teams/PA_college_m_Moravian.html': 'main_moravian.html',
    'https://www.tfrrs.org/teams/PA_college_m_Moravian.html?config_hnd=255': 'moravian_outdoor_2022.html',
    "https://www.tfrrs.org//athletes/6873033/Moravian/Shane__Houghton.html": 'distance.html',
    "https://www.tfrrs.org//athletes/6537261/Moravian/Shane_Mastro.html": 'thrower.html',
    "https://www.tfrrs.org//athletes/7983217/Moravian/Trevor_Gray.html": 'sprinter.html',
    "https://www.tfrrs.org//athletes/7983219/Moravian/Owen_Sabastro.html": 'sprint_jumper.html'
}

class Mock_Hermes(Hermes):
    """
    Mock version of Hermes used for testing.
    For testing we do not want to use requests and instead read from downloaded test html files.
    We want to test with files of the current version of TFRRS because we are webscraping
    """
    def get_soup(self, html):
        """
        This is overriding the super get_soup method in Hermes
        
        Parameters
        ----------
        html : str
            The name of the html file for testing
        """
        print(f'overrdidden: {html}')
        soup = {}
        # if 'https://' in html:
        #     html = f'tests/html_files/{urls[html]}' # if its a url it will just get the file name from url dict
        try:
            with open(f'tests/html_files/{urls[html]}', 'rb') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        except:
            print('html file does not exist')
        return soup 

def test_get_year_keys():
    hermes = Mock_Hermes()
    keys = hermes.get_year_keys('PA', 'Moravian', 'm')
    assert keys == {'2022_Outdoor': '255',
                    '2021-22_Indoor': '240',
                    '2021_Cross_Country': '224',
                    '2021_Outdoor': '216',
                    '2020-21_Indoor': '205',
                    '2020_Cross_Country': '197',
                    '2020_Outdoor': '189',
                    '2019-20_Indoor': '178',
                    '2019_Cross_Country': '169',
                    '2019_Outdoor': '160',
                    '2018-19_Indoor': '148',
                    '2018_Cross_Country': '140',
                    '2018_Outdoor': '131',
                    '2017-2018_Indoor': '125',
                    '2017_Cross_Country': '117',
                    '2017_Outdoor': '110',
                    '2016-2017_Indoor': '104',
                    '2016_Cross_Country': '98',
                    '2016_Outdoor': '93',
                    '2015-2016_Indoor': '85',
                    '2015_Cross_Country': '80',
                    '2015_Outdoor': '74',
                    '2014-2015_Indoor': '67',
                    '2014_Cross_Country': '63',
                    '2014_Outdoor': '56',
                    '2013-2014_Indoor': '49',
                    '2013_Cross_Country': '45',
                    '2013_Outdoor': '42',
                    '2012-2013_Indoor': '31',
                    '2012_Cross_Country': '27',
                    '2012_Outdoor': '23',
                    '2011-12_Indoor': '19',
                    '2011_Outdoor': '15',
                    '2010-11_Indoor': '11',
                    '2010_Outdoor': '7',
                    '2009-10_Indoor': '3'}

def test_get_team_season_html():
    hermes = Mock_Hermes()
    soup = hermes.get_soup('https://www.tfrrs.org/teams/PA_college_m_Moravian.html?config_hnd=255')
    assert hermes.get_team_html('PA', 'Moravian', 'm', '2022_Outdoor') == soup

def test_get_athlete_html():
    hermes = Mock_Hermes()
    athlete = hermes.get_athlete_html('Houghton_Shane', 'PA', 'Moravian', 'm', '2022_Outdoor')
    assert hermes.get_soup("https://www.tfrrs.org//athletes/6873033/Moravian/Shane__Houghton.html") == athlete
    
    athlete = hermes.get_athlete_html('Mastro_Shane', 'PA', 'Moravian', 'm', '2022_Outdoor')
    assert hermes.get_soup("https://www.tfrrs.org//athletes/6537261/Moravian/Shane_Mastro.html") == athlete

    athlete = hermes.get_athlete_html('Gray_Trevor', 'PA', 'Moravian', 'm', '2022_Outdoor')
    assert hermes.get_soup("https://www.tfrrs.org//athletes/7983217/Moravian/Trevor_Gray.html") == athlete

    athlete = hermes.get_athlete_html('Sabastro_Owen', 'PA', 'Moravian', 'm', '2022_Outdoor')
    assert hermes.get_soup("https://www.tfrrs.org//athletes/7983219/Moravian/Owen_Sabastro.html") == athlete
    