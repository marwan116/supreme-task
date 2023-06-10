import datetime
from copy import deepcopy
from functools import partial
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    overload,
    TypeVar,
    Union,
)

from prefect.client.schemas.objects import TaskRun
from prefect.context import TaskRunContext
from prefect.results import ResultFactory, ResultSerializer, ResultStorage
from prefect.states import State
from prefect.tasks import Task as _Task
from typeguard import typechecked
from typing_extensions import ParamSpec

T = TypeVar("T")  # Generic type var for capturing the inner return type of async funcs
R = TypeVar("R")  # The return type of the user's function
P = ParamSpec("P")  # The parameters of the task


def get_inputs_storage_key(task_name: str, start_time: str) -> str:
    return f"inputs/{task_name}/{start_time}"


def create_input_factory_from_result_factory(
    result_factory: ResultFactory,
    task_name: str,
    start_time: str,
) -> ResultFactory:
    """Create an input factory from a result factory."""
    input_factory = deepcopy(result_factory)

    input_factory.storage_key_fn = partial(
        get_inputs_storage_key,
        task_name=task_name,
        start_time=start_time,
    )

    return input_factory


def store_task_run_inputs_on_failure(
    task: "Task[P, R]", task_run: TaskRun, state: State[R]
) -> None:
    """Print the task run inputs on failure."""
    task_run_context = TaskRunContext.get()

    if task_run_context is None:
        raise RuntimeError("Task run context is not set.")

    input_factory = create_input_factory_from_result_factory(
        result_factory=task_run_context.result_factory,
        task_name=task.name,
        start_time=task_run_context.start_time.strftime("%Y-%m-%dT%H-%M-%S%z"),
    )

    inputs = task_run_context.parameters
    print(f"Inputs for {task.name} are {inputs=}")

    input_factory.create_result(inputs)  # type: ignore


class Task(_Task[P, R]):
    def __init__(
        self,
        fn: Callable[P, R],
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        version: Optional[str] = None,
        cache_key_fn: Optional[
            Callable[[TaskRunContext, Dict[str, Any]], Optional[str]]
        ] = None,
        cache_expiration: Optional[datetime.timedelta] = None,
        task_run_name: Optional[Union[Callable[[], str], str]] = None,
        retries: Optional[int] = None,
        retry_delay_seconds: Optional[
            Union[float, int, List[float], Callable[[int], List[float]]]
        ] = None,
        retry_jitter_factor: Optional[float] = None,
        persist_result: Optional[bool] = None,
        result_storage: Optional[ResultStorage] = None,
        result_serializer: Optional[ResultSerializer] = None,
        result_storage_key: Optional[str] = None,
        cache_result_in_memory: bool = True,
        timeout_seconds: Optional[Union[int, float]] = None,
        log_prints: Optional[bool] = False,
        refresh_cache: Optional[bool] = None,
        store_inputs: Literal["on_failure", "on_completion", "never"] = "on_failure",
        on_completion: Optional[
            List[Callable[["Task[P, R]", TaskRun, State[R]], None]]
        ] = None,
        on_failure: Optional[
            List[Callable[["Task[P, R]", TaskRun, State[R]], None]]
        ] = None,
    ):
        runtime_checked_fn = typechecked(fn)

        if on_failure is None:
            on_failure = []

        if on_completion is None:
            on_completion = []

        if store_inputs == "on_failure":
            on_failure.append(store_task_run_inputs_on_failure)

        if store_inputs == "on_completion":
            on_completion.append(store_task_run_inputs_on_failure)

        super().__init__(
            fn=runtime_checked_fn,
            name=name,  # type: ignore
            description=description,  # type: ignore
            tags=tags,  # type: ignore
            version=version,  # type: ignore
            cache_key_fn=cache_key_fn,  # type: ignore
            cache_expiration=cache_expiration,  # type: ignore
            task_run_name=task_run_name,
            retries=retries,
            retry_delay_seconds=retry_delay_seconds,
            retry_jitter_factor=retry_jitter_factor,
            persist_result=persist_result,
            result_storage=result_storage,
            result_serializer=result_serializer,
            result_storage_key=result_storage_key,
            cache_result_in_memory=cache_result_in_memory,
            timeout_seconds=timeout_seconds,  # type: ignore
            log_prints=log_prints,
            refresh_cache=refresh_cache,
            on_completion=on_completion,  # type: ignore
            on_failure=on_failure,  # type: ignore
        )


@overload
def task(__fn: Callable[P, R]) -> Task[P, R]:
    ...


@overload
def task(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    version: Optional[str] = None,
    cache_key_fn: Optional[
        Callable[["TaskRunContext", Dict[str, Any]], Optional[str]]
    ] = None,
    cache_expiration: Optional[datetime.timedelta] = None,
    task_run_name: Optional[Union[Callable[[], str], str]] = None,
    retries: Optional[int] = None,
    retry_delay_seconds: Optional[
        Union[
            float,
            int,
            List[float],
            Callable[[int], List[float]],
        ]
    ] = None,
    retry_jitter_factor: Optional[float] = None,
    persist_result: Optional[bool] = None,
    result_storage: Optional[ResultStorage] = None,
    result_storage_key: Optional[str] = None,
    result_serializer: Optional[ResultSerializer] = None,
    cache_result_in_memory: bool = True,
    timeout_seconds: Optional[Union[int, float]] = None,
    log_prints: Optional[bool] = None,
    refresh_cache: Optional[bool] = None,
    store_inputs: Literal["on_failure", "on_completion", "never"] = "on_failure",
    on_completion: Optional[List[Callable[["Task", TaskRun, State], None]]] = None,  # type: ignore [type-arg] # noqa: E501
    on_failure: Optional[List[Callable[["Task", TaskRun, State], None]]] = None,  # type: ignore [type-arg] # noqa: E501
) -> Callable[[Callable[P, R]], Task[P, R]]:
    ...


def task(
    __fn: Optional[Callable[P, R]] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    version: Optional[str] = None,
    cache_key_fn: Optional[
        Callable[["TaskRunContext", Dict[str, Any]], Optional[str]]
    ] = None,
    cache_expiration: Optional[datetime.timedelta] = None,
    task_run_name: Optional[Union[Callable[[], str], str]] = None,
    retries: Optional[int] = None,
    retry_delay_seconds: Optional[
        Union[
            float,
            int,
            List[float],
            Callable[[int], List[float]],
        ]
    ] = None,
    retry_jitter_factor: Optional[float] = None,
    persist_result: Optional[bool] = None,
    result_storage: Optional[ResultStorage] = None,
    result_storage_key: Optional[str] = None,
    result_serializer: Optional[ResultSerializer] = None,
    cache_result_in_memory: bool = True,
    timeout_seconds: Optional[Union[int, float]] = None,
    log_prints: Optional[bool] = None,
    refresh_cache: Optional[bool] = None,
    store_inputs: Literal["on_failure", "on_completion", "never"] = "on_failure",
    on_completion: Optional[
        List[Callable[[Task[P, R], TaskRun, State[R]], None]]
    ] = None,
    on_failure: Optional[List[Callable[[Task[P, R], TaskRun, State[R]], None]]] = None,
) -> Union[Callable[[Callable[P, R]], Task[P, R]], Task[P, R]]:
    """
    Decorator to designate a function as a task in a Prefect workflow.

    This decorator may be used for asynchronous or synchronous functions.

    Args:
        name: An optional name for the task; if not provided, the name will be
            inferred from the given function.
        description: An optional string description for the task.
        tags: An optional set of tags to be associated with runs of this task.
            These tags are combined with any tags defined by a `prefect.tags`
            context at task runtime.
        version: An optional string specifying the version of this task
            definition
        cache_key_fn: An optional callable that, given the task run context and
            call parameters, generates a string key; if the key matches a
            previous completed state, that state result will be restored instead
            of running the task again.
        cache_expiration: An optional amount of time indicating how long cached
            states for this task should be restorable; if not provided, cached
            states will never expire.
        task_run_name: An optional name to distinguish runs of this task; this
            name can be provided as a string template with the task's keyword
            arguments as variables, or a function that returns a string.
        retries: An optional number of times to retry on task run failure
        retry_delay_seconds: Optionally configures how long to wait before
            retrying the task after failure. This is only applicable if
            `retries` is nonzero. This setting can either be a number of seconds,
            a list of retry delays, or a callable that, given the total number of
            retries, generates a list of retry delays. If a number of seconds,
            that delay will be applied to all retries. If a list, each retry will
            wait for the corresponding delay before retrying. When passing a
            callable or a list, the number of configured retry delays cannot
            exceed 50.
        retry_jitter_factor: An optional factor that defines the factor to which
            a retry can be jittered in order to avoid a "thundering herd".
        persist_result: An optional toggle indicating whether the result of this
            task should be persisted to result storage. Defaults to `None`,
            which indicates that Prefect should choose whether the result should
            be persisted depending on the features being used.
        result_storage: An optional block to use to persist the result of this
            task. Defaults to the value set in the flow the task is called in.
        result_storage_key: An optional key to store the result in storage at
            when persisted. Defaults to a unique identifier.
        result_serializer: An optional serializer to use to serialize the result
            of this task for persistence. Defaults to the value set in the flow
            the task is called in.
        timeout_seconds: An optional number of seconds indicating a maximum
            runtime for the task. If the task exceeds this runtime, it will be
            marked as failed.
        log_prints: If set, `print` statements in the task will be redirected to
            the Prefect logger for the task run. Defaults to `None`, which
            indicates that the value from the flow should be used.
        refresh_cache: If set, cached results for the cache key are not used.
            Defaults to `None`, which indicates that a cached result from a
            previous execution with matching cache key is used.
        on_failure: An optional list of callables to run when the task enters a
            failed state.
        on_completion: An optional list of callables to run when the task enters
            a completed state.

    Returns:
        A callable `Task` object which, when called, will submit the task for
        execution.
    """
    if __fn:
        return cast(
            Task[P, R],
            Task(
                fn=__fn,
                name=name,
                description=description,
                tags=tags,
                version=version,
                cache_key_fn=cache_key_fn,
                cache_expiration=cache_expiration,
                task_run_name=task_run_name,
                retries=retries,
                retry_delay_seconds=retry_delay_seconds,
                retry_jitter_factor=retry_jitter_factor,
                persist_result=persist_result,
                result_storage=result_storage,
                result_storage_key=result_storage_key,
                result_serializer=result_serializer,
                cache_result_in_memory=cache_result_in_memory,
                timeout_seconds=timeout_seconds,
                log_prints=log_prints,
                refresh_cache=refresh_cache,
                store_inputs=store_inputs,
                on_completion=on_completion,
                on_failure=on_failure,
            ),
        )
    else:
        return cast(
            Callable[[Callable[P, R]], Task[P, R]],
            partial(
                task,
                name=name,
                description=description,
                tags=tags,
                version=version,
                cache_key_fn=cache_key_fn,
                cache_expiration=cache_expiration,
                task_run_name=task_run_name,
                retries=retries,
                retry_delay_seconds=retry_delay_seconds,
                retry_jitter_factor=retry_jitter_factor,
                persist_result=persist_result,
                result_storage=result_storage,
                result_storage_key=result_storage_key,
                result_serializer=result_serializer,
                cache_result_in_memory=cache_result_in_memory,
                timeout_seconds=timeout_seconds,
                log_prints=log_prints,
                refresh_cache=refresh_cache,
                store_inputs=store_inputs,
                on_completion=on_completion,
                on_failure=on_failure,
            ),
        )
