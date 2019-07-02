class TagState:
    def __init__(self, step, repos):
        self.step = step
        self.repos = repos

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Repo:

    def __init__(self, project, name, path, tag):
        self.project = project
        self.name = name
        self.path = path
        self.tag = tag

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Tag:
    def __init__(self, tag, commit):
        self.tag = tag
        self.commit = commit

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
