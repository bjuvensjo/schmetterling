class BuildStatusState:
    def __init__(self, step, repos):
        self.step = step
        self.repos = repos

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Repo:
    STATUS_SUCCESS = 'success'
    STATUS_FAILURE = 'failure'

    def __init__(self, project, name, path, commit_id, build_url, status):
        self.project = project
        self.name = name
        self.path = path
        self.commit_id = commit_id
        self.build_url = build_url
        self.status = status

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
