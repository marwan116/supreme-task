"""A collection of Nox sessions."""
from dataclasses import dataclass
from typing import List

from nox_poetry import Session, session as noxsession


@dataclass(frozen=True)
class Package:
    """Package specification."""

    base_python: str
    python_versions: List[str]
    pip_version: str
    build_dependencies: List[str]
    test_dependencies: List[str]
    locations: List[str]

package = Package(
    base_python="3.8",
    python_versions=["3.8"],
    pip_version="23.0.1",
    build_dependencies=["poetry-core", "setuptools"],    
    test_dependencies=[
        "coverage[toml]",
        "pytest",
        "pytest-mock",
        "pytest-sugar",
        "time-machine",
    ],
    locations=[
        "src",
        "tests",
    ],
)



@noxsession(python=package.base_python, venv_params=["--pip", package.pip_version])
def black(session: Session) -> None:
    """Format with black."""
    args = session.posargs or ["--check"] + package.locations
    session.install("black")
    session.run("black", *args)


@noxsession(python=package.base_python, venv_params=["--pip", package.pip_version])
def isort(session: Session) -> None:
    """Import sorting with isort."""
    session.install("isort[pyproject]")
    args = session.posargs or ["--check-only"] + package.locations
    session.run("isort", *args)


@noxsession(python=package.base_python, venv_params=["--pip", package.pip_version])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    session.install(*package.build_dependencies)
    args = session.posargs or package.locations
    deps = [
        ".",
        "mypy",
        "nox-poetry",
    ]
    session.install(*deps)
    session.run("mypy", *args, env={"MYPYPATH": "src"})


@noxsession(python=package.python_versions, venv_params=["--pip", package.pip_version])
def test(session: Session) -> None:
    """Run test suite and produce coverage data."""
    session.install(*package.build_dependencies)
    session.install(".", *package.test_dependencies)

    # convenient place to do this check, since we've already built the library
    session.run("pip", "check")

    options = session.posargs or []
    session.run("coverage", "run", "-m", "pytest", *options, "tests")
