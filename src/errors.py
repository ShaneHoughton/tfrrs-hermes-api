class NoAthleteFoundException(Exception):
    def __init__(self, name, message="Athlete could not be found"):
        self.name = name
        self.message = message
        super().__init__(self.message)

class NoTeamFoundException(Exception):
    def __init__(self, name, message="Team could not be found"):
        self.name = name
        self.message = message
        super().__init__(self.message)