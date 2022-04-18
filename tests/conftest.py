import pytest
from unittest.mock import MagicMock
from postmanager.manager import PostManager


@pytest.fixture
def manager():
    storage_proxy = MagicMock()
    post_manager = PostManager(storage_proxy)
    return post_manager
