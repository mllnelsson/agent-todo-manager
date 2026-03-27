from db.models import Completion, Project


class ProjectDetail(Project):
    completions: list[Completion] = []
