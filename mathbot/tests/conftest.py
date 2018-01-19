import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-automata",
        action = "store_true",
        default = False,
        help = "Run tests reliant on the automata"
    )
    parser.addoption(
        "--run-automata-human",
        action = "store_true",
        default = False,
        help = "Run tests reliant on the automata and human interaction"
    )

