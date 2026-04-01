from db.models import (
    Action,
    CompletionCreate,
    EntityType,
    Status,
    Step,
    StepCreate,
    StepUpdate,
    TaskUpdate,
    StoryUpdate,
)
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
from db.orm import Step as StepORM, Task as TaskORM
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .exceptions import InvalidStatus, NotFound


def get_step_by_task_seq(task_id: str, seq: int, engine: Engine) -> Step:
    step = get_step_by_seq(engine, task_id=task_id, seq=seq)
    if step is None:
        raise NotFound(f"Step {seq} not found in task {task_id}")
    return step


def get_next_pending_step(task_id: str, engine: Engine) -> Step:
    step = get_next_step(engine, task_id=task_id)
    if step is None:
        raise NotFound(f"No pending steps in task {task_id}")
    return step


def create_step_for_task(data: StepCreate, engine: Engine) -> Step:
    return create_step(engine, data=data)


def update_step_by_id(step_id: str, data: StepUpdate, engine: Engine) -> Step:
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
                update_story(engine, story_id=story_id, data=StoryUpdate(status=Status.COMPLETED))
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
