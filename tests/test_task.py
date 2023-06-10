"""Test the task decorator."""
import pytest
from prefect import flow
from prefect.filesystems import LocalFileSystem
from typeguard import TypeCheckError

from supreme_task.tasks import task


def test_raises_type_error_for_arguments_of_wrong_type():
    """Test TypeError is raised when a task is called with arguments of wrong type."""

    @task
    def add(x: int, y: int) -> int:
        return x + y

    with pytest.raises(TypeCheckError):
        add.fn(x="1", y="2")  # type: ignore

    with pytest.raises(TypeCheckError):
        add.fn(x=1, y="2")  #   type: ignore

    with pytest.raises(TypeCheckError):
        add.fn(x="1", y="2")  # type: ignore


def test_inputs_persisted_on_failure_by_default(tmpdir):
    """Test that inputs are persisted on failure by default."""

    @task(persist_result=True)
    def faulty_add(x: int, y: int) -> int:
        if x == 1:
            raise ValueError("x is 1")
        return x + y

    @flow(result_storage=LocalFileSystem(basepath=str(tmpdir)))
    def my_flow() -> None:
        faulty_add(x=1, y=2)

    with pytest.raises(ValueError):
        my_flow()

    assert (tmpdir / "inputs").exists()
