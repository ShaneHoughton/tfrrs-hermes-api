from flask import Flask, jsonify, request
from src.hermes import Hermes, NoAthleteFoundException, NoTeamFoundException



app = Flask(__name__)
hermes = Hermes()

class InvalidAPIUsage(Exception):
    status_code = 400
    message = 'Bad request. Check that syntax is correct and information was entered correctly.'
    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['error'] = self.status_code
        return rv

@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code

@app.route("/athlete-bests")
def get_athlete_bests():
    headers = ['Name','State', 'Team-name', 'Gender', 'Season']
    return perform_request(hermes.get_athlete_bests, headers)

@app.route("/athlete-results") # not set on the name
def get_athlete_results():
    headers = ['Name','State', 'Team-name', 'Gender', 'Season']
    return perform_request(hermes.get_athlete_results, headers)

@app.get("/roster")
def get_roster():
    headers = ['State', 'Team-name', 'Gender', 'Season']
    return perform_request(hermes.get_roster, headers)

@app.get("/top-performances")
def get_top_perfs():
    headers = ['State', 'Team-name', 'Gender', 'Season']
    return perform_request(hermes.get_top_performances, headers)

@app.get("/meets")
def get_meets():
    return perform_request(hermes.get_meets)

@app.get("/meet-results")
def get_meet_results():
    headers = ['Meet-name', 'Gender']
    return perform_request(hermes.get_meet_results, headers)


def get_arg_vals(headers, request):
    vals = [request.args.get(header) for header in headers]
    return tuple(vals)

def perform_request(method, headers=None):
    header_vals = []
    if headers is not None:
        header_vals = get_arg_vals(headers, request)
    if None in header_vals:
        raise InvalidAPIUsage("Check that headers are correct.")
    try:
        print(header_vals)
        return jsonify(method(*header_vals))
    except NoAthleteFoundException as e:
        raise InvalidAPIUsage(message=e.message, status_code=404)
    except NoTeamFoundException as e:
        raise InvalidAPIUsage(message=e.message, status_code=404)
    # except:
    #     InvalidAPIUsage("IDK")


