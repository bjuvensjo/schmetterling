class AnalyzeState:
    def __init__(self, step, analyzes):
        self.step = step
        self.analyzes = analyzes

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Analyze:
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

    def __init__(
            self,
            project,
            name,
            version,
            path,
            status,
            timestamp,
            **kwargs,
    ):
        self.project = project
        self.name = name
        self.version = version
        self.path = path
        self.status = status
        self.timestamp = timestamp

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
