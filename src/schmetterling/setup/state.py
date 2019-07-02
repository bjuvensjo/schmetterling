class SetupState:
    def __init__(self, step, repos):
        self.step = step
        self.repos = repos

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Repo:
    STATUS_UNCHANGED = 'unchanged'
    STATUS_UPDATED = 'updated'

    def __init__(
            self,
            project,
            name,
            clone_url,
            path,
            branches,
            setup_branch,
            status,
    ):
        self.project = project
        self.name = name
        self.clone_url = clone_url
        self.path = path
        self.branches = branches
        self.setup_branch = setup_branch
        self.status = status

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Branch:
    def __init__(self, name, is_default, head):
        self.name = name
        self.is_default = is_default
        self.head = head

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
