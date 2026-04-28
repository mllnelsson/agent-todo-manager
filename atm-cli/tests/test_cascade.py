"""Tests for the task → story status cascade."""

import uuid

from db.models import Status, StoryUpdate, TaskUpdate
from db.repo import get_story, update_story

from atm_cli.services.stories import update_story_by_id
from atm_cli.services.tasks import (
    complete_task,
    start_task,
    update_task_by_id,
)


AGENT = "test-agent"
SESSION = str(uuid.uuid4())


def test_starting_first_task_promotes_todo_story_to_in_progress(
    engine, story_id, make_task
):
    task_id = make_task(Status.TODO)
    start_task(task_id, AGENT, SESSION, None, engine)
    story = get_story(engine, story_id)
    assert story is not None
    assert story.status == Status.IN_PROGRESS


def test_completing_last_task_completes_story(engine, story_id, make_task):
    a = make_task(Status.TODO)
    b = make_task(Status.TODO)
    start_task(a, AGENT, SESSION, None, engine)
    complete_task(a, AGENT, SESSION, None, engine)
    start_task(b, AGENT, SESSION, None, engine)
    complete_task(b, AGENT, SESSION, None, engine)
    story = get_story(engine, story_id)
    assert story is not None
    assert story.status == Status.COMPLETED


def test_restarting_task_demotes_completed_story_to_in_progress(
    engine, story_id, make_task
):
    a = make_task(Status.TODO)
    start_task(a, AGENT, SESSION, None, engine)
    complete_task(a, AGENT, SESSION, None, engine)
    pre = get_story(engine, story_id)
    assert pre is not None and pre.status == Status.COMPLETED

    update_task_by_id(a, TaskUpdate(status=Status.IN_PROGRESS), engine)
    post = get_story(engine, story_id)
    assert post is not None
    assert post.status == Status.IN_PROGRESS


def test_direct_task_update_to_completed_cascades_to_story(
    engine, story_id, make_task
):
    a = make_task(Status.TODO)
    update_task_by_id(a, TaskUpdate(status=Status.COMPLETED), engine)
    story = get_story(engine, story_id)
    assert story is not None
    assert story.status == Status.COMPLETED


def test_manual_story_status_overridden_when_inconsistent_with_tasks(
    engine, story_id, make_task
):
    make_task(Status.TODO)  # one TODO task

    result = update_story_by_id(
        story_id, StoryUpdate(status=Status.COMPLETED), engine
    )
    assert result.status == Status.TODO


def test_story_with_no_tasks_keeps_manual_status(engine, story_id):
    update_story(engine, story_id=story_id, data=StoryUpdate(status=Status.IN_PROGRESS))
    result = update_story_by_id(
        story_id, StoryUpdate(status=Status.COMPLETED), engine
    )
    assert result.status == Status.COMPLETED


def test_mixed_task_states_yield_in_progress_story(engine, story_id, make_task):
    a = make_task(Status.TODO)
    make_task(Status.TODO)
    start_task(a, AGENT, SESSION, None, engine)
    complete_task(a, AGENT, SESSION, None, engine)
    story = get_story(engine, story_id)
    assert story is not None
    assert story.status == Status.IN_PROGRESS
