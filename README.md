# A prefect extension giving prefect tasks super powers

## Motivation

Prefect tasks plus added functionality to enforce type checking and help in debugging helping to reduce negative engineering!

## How to setup

Using pip:

```bash
pip install supreme_task
```

## How to use

Simply swap out `prefect` for `supreme_task` when importing the `task` decorator.

i.e.

```python
from supreme_task import task
```

instead of

```python
from prefect import task
```

and you're good to go!

### Runtime type checking

Get runtime type checking thanks to [typeguard](http) by importing the `@task` decorator from `supreme_task` instead of `prefect`.

See the example `run.py` file:

```python run.py
from supreme_task import task

@task
def add(x: int, y: int) -> int:
    return x + y

add.fn(x="1", y=2)
```

Running `python run.py` will raise the following exception:

```python
Traceback (most recent call last):
  File "run.py", line 9, in <module>
    add.fn(x="1", y=2)
  File "run.py", line 5, in add
    def add(x: int, y: int) -> int:
  File "supreme-task-py38/lib/python3.8/site-packages/typeguard/_functions.py", line 135, in check_argument_types
    check_type_internal(value, annotation, memo)
  File "supreme-task-py38/lib/python3.8/site-packages/typeguard/_checkers.py", line 761, in check_type_internal
    raise TypeCheckError(f"is not an instance of {qualified_name(origin_type)}")
typeguard.TypeCheckError: argument "x" (str) is not an instance of int
```

### Persistence of flow run inputs

Get persistence of flow run inputs by importing the `@task` decorator from `supreme_task` instead of `prefect` to help with debugging.

i.e. given a file `run.py`:

```python run.py
from supreme_task import task
from prefect import flow
from prefect.filesystems import LocalFileSystem

@task
def faulty_add(x: int, y: int) -> int:
    if x == 1:
        raise ValueError("x is 1")
    return x + y

@flow(result_storage=LocalFileSystem(basepath="results/"))
def my_flow() -> None:
    faulty_add(x=1, y=2)

my_flow()
```

We update our prefect configuration to enable result persistence:

```bash
prefect config set PREFECT_RESULTS_PERSIST_BY_DEFAULT=true
```

We then run the flow by running `python run.py`

We now inspect the results directory:

```bash
$ tree results
results
├── 514aaa4ae0134405a639cbd9a17365da
├── b662c63ff9854b0e9383d7f6cf0a5b76
└── inputs
    └── faulty_add
        └── 2023-06-10T10-47-04+0000
```

The inputs for failed task runs are saved under `results/inputs/<task_name>/<start_run_time>`.
