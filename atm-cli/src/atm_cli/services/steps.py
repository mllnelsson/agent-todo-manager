from db.models import (
    Action,
    CompletionCreate,
    EntityType,
    Status,
    Step,
    StepCreate,
    StepUpdate,
    StoryUpdate,
    TaskUpdate,
)
from db.orm import Step as StepORM
from db.orm import Task as TaskORM
from db.repo import (
    create_completion,
    create_step,
    get_next_step,
    get_step,
    get_step_by_seq,
    get_story,
    get_task,
    update_step,
    update_story,
    update_task,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .exceptions import InvalidStatus, NotFound


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


def get_next_pending_step(task_id: str, engine: Engine) -> Step:
    """Return the next TODO step for the given task, ordered by sequence number.

    Args:
        task_id: UUID of the task.
        engine: SQLAlchemy engine.

    Returns:
        The next pending Step.

    Raises:
        NotFound: If the task has no pending steps.
    """
    step = get_next_step(engine, task_id=task_id)
    if step is None:
        raise NotFound(f"No pending steps in task {task_id}")
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


def start_step(
    step_id: str,
    agent_name: str,
    session_id: str,
    branch: str | None,
    engine: Engine,
) -> Step:
    """Transition a step from TODO to IN_PROGRESS and record a started completion event.

    Args:
        step_id: UUID of the step to start.
        agent_name: Name of the agent claiming the step.
        session_id: Session identifier for the agent.
        branch: Git branch the agent is working on, if any.
        engine: SQLAlchemy engine.

    Returns:
        The updated Step with status IN_PROGRESS.

    Raises:
        NotFound: If no step with the given ID exists.
        InvalidStatus: If the step is not in TODO status.
    """
    step = get_step(engine, step_id=step_id)
    if step is None:
        raise NotFound(f"Step {step_id} not found")
    if step.status != Status.TODO:
        raise InvalidStatus(f"Step is {step.status}, expected {Status.TODO}")

    update_step(engine, step_id=step_id, data=StepUpdate(status=Status.IN_PROGRESS))
    create_completion(
        engine,
        data=CompletionCreate(
            entity_type=EntityType.STEP,
            entity_id=step_id,
            action=Action.STARTED,
            agent_name=agent_name,
            session_id=session_id,
            branch=branch,
        ),
    )
    # TODO: Might be an anti pattern with the get for te return
    updated = get_step(engine, step_id=step_id)
    assert updated is not None
    return updated


def complete_step(
    step_id: str,
    agent_name: str,
    session_id: str,
    branch: str | None,
    engine: Engine,
) -> Step:
    """Transition a step from IN_PROGRESS to COMPLETED and cascade completion up the hierarchy.

    After marking the step COMPLETED, checks if all steps on the parent task are now complete
    and, if so, marks the task COMPLETED as well. If the task belongs to a story and all tasks
    in that story are then complete, the story is also marked COMPLETED. A completion event is
    recorded at each level that transitions.

    Args:
        step_id: UUID of the step to complete.
        agent_name: Name of the agent completing the step.
        session_id: Session identifier for the agent.
        branch: Git branch the agent worked on, if any.
        engine: SQLAlchemy engine.

    Returns:
        The updated Step with status COMPLETED.

    Raises:
        NotFound: If no step with the given ID exists.
        InvalidStatus: If the step is not in IN_PROGRESS status.
    """
    step = get_step(engine, step_id=step_id)
    if step is None:
        raise NotFound(f"Step {step_id} not found")
    if step.status != Status.IN_PROGRESS:
        raise InvalidStatus(f"Step is {step.status}, expected {Status.IN_PROGRESS}")

    update_step(engine, step_id=step_id, data=StepUpdate(status=Status.COMPLETED))
    create_completion(
        engine,
        data=CompletionCreate(
            entity_type=EntityType.STEP,
            entity_id=step_id,
            action=Action.COMPLETED,
            agent_name=agent_name,
            session_id=session_id,
            branch=branch,
        ),
    )

    with Session(engine) as session:
        orm_step = session.get(StepORM, step_id)
        task_id = str(orm_step.task_id)

    task = get_task(engine, task_id=task_id)
    assert task is not None
    # TODO: This should be handled like other none checks

    if task.steps and all(s.status == Status.COMPLETED for s in task.steps):
        update_task(engine, task_id=task_id, data=TaskUpdate(status=Status.COMPLETED))
        create_completion(
            engine,
            data=CompletionCreate(
                entity_type=EntityType.TASK,
                entity_id=task_id,
                action=Action.COMPLETED,
                agent_name=agent_name,
                session_id=session_id,
                branch=branch,
            ),
        )

        with Session(engine) as session:
            orm_task = session.get(TaskORM, task_id)
            story_id = str(orm_task.story_id) if orm_task.story_id else None

        if story_id:
            story = get_story(engine, story_id=story_id)
            assert story is not None
            if story.tasks and all(t.status == Status.COMPLETED for t in story.tasks):
                update_story(
                    engine, story_id=story_id, data=StoryUpdate(status=Status.COMPLETED)
                )
                create_completion(
                    engine,
                    data=CompletionCreate(
                        entity_type=EntityType.STORY,
                        entity_id=story_id,
                        action=Action.COMPLETED,
                        agent_name=agent_name,
                        session_id=session_id,
                        branch=branch,
                    ),
                )

    updated = get_step(engine, step_id=step_id)
    assert updated is not None
    return updated
