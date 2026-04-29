from db.models import Step, StepCreate, StepUpdate
from db.repo import (
    create_step,
    delete_step,
    get_step_by_seq,
    update_step,
)
from sqlalchemy.engine import Engine

from .exceptions import NotFound


def get_step_by_task_seq(task_id: str, seq: int, engine: Engine) -> Step:
    """Fetch a step by its task-scoped sequence number.

    Args:
        task_id: UUID of the task the step belongs to.
        seq: Task-scoped sequence number of the step.
        engine: SQLAlchemy engine.

    Returns:
        The matching Step.

    Raises:
        NotFound: If no step with the given sequence number exists in the task.
    """
    step = get_step_by_seq(engine, task_id=task_id, seq=seq)
    if step is None:
        raise NotFound(f"Step {seq} not found in task {task_id}")
    return step


def create_step_for_task(data: StepCreate, engine: Engine) -> Step:
    """Create a new step under the task specified in data.

    Args:
        data: Step creation payload including task_id, title, and description.
        engine: SQLAlchemy engine.

    Returns:
        The newly created Step.
    """
    return create_step(engine, data=data)


def update_step_by_id(step_id: str, data: StepUpdate, engine: Engine) -> Step:
    """Apply partial updates to the step with the given ID.

    Args:
        step_id: UUID of the step to update.
        data: Fields to update; None values are ignored.
        engine: SQLAlchemy engine.

    Returns:
        The updated Step.

    Raises:
        NotFound: If no step with the given ID exists.
    """
    step = update_step(engine, step_id=step_id, data=data)
    if step is None:
        raise NotFound(f"Step {step_id} not found")
    return step


def delete_step_by_task_seq(task_id: str, seq: int, engine: Engine) -> None:
    step = get_step_by_seq(engine, task_id=task_id, seq=seq)
    if step is None:
        raise NotFound(f"Step {seq} not found in task {task_id}")
    delete_step(engine, step_id=step.id)
