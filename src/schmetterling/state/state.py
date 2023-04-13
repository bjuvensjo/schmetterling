class StateState:
    def __init__(self, step, file_path):
        self.step = step
        self.file_path = file_path

    def __repr__(self):
        return self.__class__.__name__ + ": " + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
