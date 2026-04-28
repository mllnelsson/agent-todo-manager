from db.models import (
    Action,
    CompletionCreate,
    EntityType,
    Status,
    StoryUpdate,
)
from db.repo import create_completion, get_story, update_story
from sqlalchemy.engine import Engine


def _derive_story_status(task_statuses: list[Status]) -> Status | None:
    if not task_statuses:
        return None
    if all(s == Status.COMPLETED for s in task_statuses):
        return Status.COMPLETED
    if all(s == Status.TODO for s in task_statuses):
        return Status.TODO
    return Status.IN_PROGRESS


def reconcile_story_status(
    engine: Engine,
    story_id: str,
    agent_name: str | None = None,
    session_id: str | None = None,
    branch: str | None = None,
) -> None:
    """Recompute story.status from its tasks. Idempotent.

    Rules:
      - tasks empty → leave story as-is (manual override stands)
      - all tasks COMPLETED → story COMPLETED
      - all tasks TODO → story TODO
      - otherwise (mixed or any IN_PROGRESS) → story IN_PROGRESS

    When the status changes and audit context (agent_name + session_id) is
    provided, a completion event is recorded: STARTED for IN_PROGRESS,
    COMPLETED for COMPLETED. TODO transitions are not audited.
    """
    story = get_story(engine, story_id=story_id)
    if story is None:
        return
    target = _derive_story_status([t.status for t in story.tasks])
    if target is None or target == story.status:
        return

    update_story(engine, story_id=story_id, data=StoryUpdate(status=target))

    if not (agent_name and session_id):
        return
    action_for_target = {
        Status.IN_PROGRESS: Action.STARTED,
        Status.COMPLETED: Action.COMPLETED,
    }
    action = action_for_target.get(target)
    if action is None:
        return
    create_completion(
        engine,
        data=CompletionCreate(
            entity_type=EntityType.STORY,
            entity_id=story_id,
            action=action,
            agent_name=agent_name,
            session_id=session_id,
            branch=branch,
        ),
    )
