from flask import Flask, jsonify, request
from hermes import Hermes


app = Flask(__name__)
# header_map = {'Gender':['m', 'f'], "Season":['Outdoor', 'Indoor', 'Cross_Country']}
hermes = Hermes()

class InvalidAPIUsage(Exception):
    status_code = 400
    message = 'Bad request. Check that syntax is correct.'
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
    header_vals = get_header_vals(headers, request)
    if None in header_vals:
        raise InvalidAPIUsage("Headers are incorrect.")
    name, state, team_name, gender, season = header_vals
    try:
        return jsonify(hermes.get_athlete_bests(name, state, team_name, gender, season))
    except:
        raise InvalidAPIUsage()

@app.route("/athlete-results") # not set on the name
def get_athlete_results():
    headers = ['Name','State', 'Team-name', 'Gender', 'Season']
    header_vals = get_header_vals(headers, request)
    if None in header_vals:
        raise InvalidAPIUsage("Headers are incorrect.")
    name, state, team_name, gender, season = header_vals
    try:
        return jsonify(hermes.get_athlete_results(name, state, team_name, gender, season))
    except:
        raise InvalidAPIUsage()


@app.get("/roster")
def get_roster():
    headers = ['State', 'Team-name', 'Gender', 'Season']
    header_vals = get_header_vals(headers, request)
    if None in header_vals:
        raise InvalidAPIUsage("Headers are incorrect.")
    state, team_name, gender, season = header_vals
    try:
        return jsonify(hermes.get_roster(state, team_name, gender, season))
    except:
        raise InvalidAPIUsage()

def get_header_vals(headers, request):
    vals = [request.headers.get(header) for header in headers]
    return tuple(vals)


