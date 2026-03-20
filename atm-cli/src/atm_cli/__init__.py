from db.model import Task

task = Task(id="1")


def main() -> None:
    print("Hello from atm-cli!")
    print(f"This is the first task {task}")
