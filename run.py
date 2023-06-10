from prefect import flow
from prefect.filesystems import LocalFileSystem
from supreme_task.tasks import task

# run-time type checking


@task()
def add(x: int, y: int) -> int:
    return x + y


print(add.on_failure)


@flow(
    result_storage=LocalFileSystem(basepath="flows"),
    persist_result=True,
    result_serializer="json",
)
def my_flow() -> None:
    out = add(x=1, y="2")
    print("test")


my_flow()


# task_run_context.result_factory = ResultFactory(
#     persist_result=False,
#     cache_result_in_memory=True,
#     serializer=JSONSerializer(type='json', jsonlib='json', object_encoder='prefect.serializers.prefect_json_object_encoder', object_decoder='prefect.serializers.prefect_json_object_decoder', dumps_kwargs={}, loads_kwargs={}),
#     storage_block_id=UUID('2ecf83e8-3563-4be8-8715-c9ec4bc62b75'),
#     storage_block=LocalFileSystem(basepath='flows'),
#     storage_key_fn=<function DEFAULT_STORAGE_KEY_FN at 0x10cdf3d30>
# )
