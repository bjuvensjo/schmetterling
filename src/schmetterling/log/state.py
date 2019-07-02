class LogState:
    def __init__(self, step, log_file):
        self.step = step
        self.log_file = log_file

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
