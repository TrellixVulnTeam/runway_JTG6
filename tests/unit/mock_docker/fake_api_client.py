"""Fake Docker API client."""
# pylint: disable=attribute-defined-outside-init,protected-access
import copy
from typing import Any, Dict, Optional

import docker
import mock
from docker.constants import DEFAULT_DOCKER_API_VERSION

from . import fake_api


class CopyReturnMagicMock(mock.MagicMock):
    """A MagicMock which deep copies every return value."""

    def _mock_call(  # pylint: disable=arguments-differ
        self, *args: Any, **kwargs: Any
    ) -> Any:
        ret = super()._mock_call(*args, **kwargs)  # type: ignore
        if isinstance(ret, (dict, list)):
            ret = copy.deepcopy(ret)  # type: ignore
        return ret  # type: ignore


def make_fake_api_client(
    overrides: Optional[Dict[str, Any]] = None
) -> CopyReturnMagicMock:
    """Return non-complete fake APIClient.

    This returns most of the default cases correctly, but most arguments that
    change behavior will not work.

    """
    if overrides is None:
        overrides = {}
    api_client = docker.APIClient(version=DEFAULT_DOCKER_API_VERSION)
    mock_attrs = {  # type: ignore
        "build.return_value": fake_api.FAKE_IMAGE_ID,
        "commit.return_value": fake_api.post_fake_commit()[1],
        "containers.return_value": fake_api.get_fake_containers()[1],
        "create_container.return_value": fake_api.post_fake_create_container()[1],
        "create_host_config.side_effect": api_client.create_host_config,
        "create_network.return_value": fake_api.post_fake_network()[1],
        "exec_create.return_value": fake_api.post_fake_exec_create()[1],
        "exec_start.return_value": fake_api.post_fake_exec_start()[1],
        "images.return_value": fake_api.get_fake_images()[1],
        "inspect_container.return_value": fake_api.get_fake_inspect_container()[1],
        "inspect_image.return_value": fake_api.get_fake_inspect_image()[1],
        "inspect_network.return_value": fake_api.get_fake_network()[1],
        "logs.return_value": [b"hello world\n"],
        "networks.return_value": fake_api.get_fake_network_list()[1],
        "start.return_value": None,
        "wait.return_value": {"StatusCode": 0},
        "version.return_value": fake_api.get_fake_version(),
    }
    mock_attrs.update(overrides)
    mock_client = CopyReturnMagicMock(**mock_attrs)

    mock_client._version = DEFAULT_DOCKER_API_VERSION
    return mock_client


def make_fake_client(overrides: Optional[Dict[str, Any]] = None) -> docker.DockerClient:
    """Return a Client with a fake APIClient."""
    client = docker.DockerClient(version=DEFAULT_DOCKER_API_VERSION)
    client.api = make_fake_api_client(overrides)
    return client
