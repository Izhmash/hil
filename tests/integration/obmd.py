"""Integration tests for interactions with obmd."""

import json
import requests
import pytest
from hil.test_common import config_testsuite, config_merge, \
    fresh_database, fail_on_log_warnings, server_init, with_request_context, \
    obmd_cfg

from hil import api, config, errors


@pytest.fixture()
def configure():
    """Set up the HIL configureation."""
    config_testsuite()
    config_merge({
        'extensions': {
            'hil.ext.obm.mock': '',
        },
        'devel': {
            'dry_run': None,
        },
    })
    config.load_extensions()


fresh_database = pytest.fixture(fresh_database)
fail_on_log_warnings = pytest.fixture(fail_on_log_warnings)
server_init = pytest.fixture(server_init)
with_request_context = pytest.yield_fixture(with_request_context)
obmd_cfg = pytest.fixture(obmd_cfg)


pytestmark = pytest.mark.usefixtures(
    'configure',
    'fresh_database',
    'fail_on_log_warnings',
    'server_init',
    'with_request_context',
)


@pytest.fixture
def mock_node(obmd_cfg):
    """Register a node wth obmd & hil. returns the node's label.

    The node will be attached to a project called 'anvil-nextgen'.
    """
    obmd_uri = 'http://localhost' + obmd_cfg['ListenAddr'] + '/node/node-99'

    # register a node with obmd:
    requests.put(
        obmd_uri,
        auth=('admin', obmd_cfg['AdminToken']),
        data=json.dumps({
            "type": "mock",
            "info": {
                "addr": "10.0.0.4",
                "NumWrites": 0,
            },
        }))

    # and then with hil:
    api.node_register(
        node='node-99',
        obm={
            "type": 'http://schema.massopencloud.org/haas/v0/obm/mock',
            "host": "ipmihost",
            "user": "root",
            "password": "tapeworm",
        },
        obmd={
            'uri': obmd_uri,
            'admin_token': obmd_cfg['AdminToken'],
        },
    )

    # Create a project, and attach the node.
    api.project_create('anvil-nextgen')
    api.project_connect_node('anvil-nextgen', 'node-99')

    return 'node-99'


def test_enable_disable_obm(mock_node):
    """Test enabling and disabling the obm of a node via the api."""

    # First, enable the obm
    api.node_enable_disable_obm(mock_node, enabled=True)

    # Obm is enabled; we shouldn't be able to detach the node:
    with pytest.raises(errors.BlockedError):
        api.project_detach_node('anvil-nextgen', mock_node)

    # ...so disable it first:
    api.node_enable_disable_obm(mock_node, enabled=False)

    # ...and then it should work:
    api.project_detach_node('anvil-nextgen', mock_node)


def _follow_redirect(method, resp, data=None, stream=False):
    assert resp.status_code == 307
    resp = requests.request(method, resp.location, data=data, stream=stream)
    assert resp.ok
    return resp


def test_power_operations(mock_node):
    """Test the power-related obm api calls.

    i.e. power_off, power_cycle, set_bootdev.
    """
    # Obm is disabled; these should all fail:
    with pytest.raises(errors.BlockedError):
        api.node_power_off(mock_node)
    with pytest.raises(errors.BlockedError):
        api.node_power_on(mock_node)
    with pytest.raises(errors.BlockedError):
        api.node_set_bootdev(mock_node, 'A')
    with pytest.raises(errors.BlockedError):
        api.node_power_cycle(mock_node, force=True)
    with pytest.raises(errors.BlockedError):
        api.node_power_cycle(mock_node, force=False)

    # Now let's enable it and try again.
    api.node_enable_disable_obm(mock_node, enabled=True)

    def _power_cycle(force):
        _follow_redirect(
            'POST',
            api.node_power_cycle(mock_node, force=force),
            data=json.dumps({
                'force': force,
            }))

    _follow_redirect('POST', api.node_power_off(mock_node))
    _follow_redirect('POST', api.node_power_on(mock_node))
    _follow_redirect(
        'PUT',
        api.node_set_bootdev(mock_node, 'A'),
        data=json.dumps({'bootdev': 'A'}),
    )
    _power_cycle(True)
    _power_cycle(False)
