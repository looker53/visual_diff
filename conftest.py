import pytest

from visual import Eye


@pytest.fixture(scope='session')
def eye():
    return Eye()