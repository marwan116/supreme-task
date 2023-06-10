# An prefect extension giving prefect tasks super powers

## Motivation
Prefect tasks plus added functionality to enforce type checking and help in debugging helping to reduce negative engineering!

## How to setup

Using pip:

```bash
pip install supreme_task
```

## How to use

### Runtime type checking

Get runtime type checking thanks to [typeguard](http) by importing the `@task` decorator from `supreme_task` instead of `prefect`. 

Running `python run.py` will give the following output:

```bash
Traceback (most recent call last):
  File "run.py", line 11, in <module>
    add(1, "2")
  File "supreme_task/supreme_task/task.py", line 15, in wrapper
    raise TypeError(f"Argument {i} to {func.__name__} has incompatible type {type(arg)}; expected {type(annotations[arg_name])}")
TypeError: Argument 2 to add has incompatible type <class 'str'>; expected <class 'int'>
```

### Persistence of flow run inputs

Get persistence of flow run inputs by importing the `@task` decorator from `supreme_task` instead of `prefect` to help with debugging.

i.e. given a file `run.py`:

```python
from supreme_task import task
from supreme_task.triggers import on_failure
from prefect import flow
from prefect.filesystems import LocalFileSystem

def default_input_storage_key_fn(task):
    """Returns input__{task_name}__{timestamp}.pkl"""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S%z")
    return f"input__{task.name}__{timestamp}.pkl"

@task( # this is the default behaviour for supreme tasks
    persist_input=on_failure,
    input_storage_key_fn=default_input_storage_key_fn,
) 
def add(x: int, y: int) -> int:
    if x == 1:
        raise ValueError("x cannot be 1")
    return x + y

@flow(result_storage=LocalFileSystem(basepath="prefect-results"))
def my_flow():
    add(1, 2)
    add(1, 3)
```

Running `python run.py` will show the inputs stored in the following location:

```bash
$ tree prefect-results/
|-- 2020-07-30T14-42-00.000000-00-00
|   |-- add-1-2.pkl
|   `-- add-1-3.pkl
```

### Updating prefect runtime context
