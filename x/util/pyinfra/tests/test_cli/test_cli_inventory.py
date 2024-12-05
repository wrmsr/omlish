from os import path

from pyinfra import inventory
from pyinfra.context import ctx_inventory, ctx_state

from ..paramiko_util import PatchSSHTestCase
from .util import run_cli


class TestCliInventory(PatchSSHTestCase):
    def test_load_deploy_group_data(self):
        ctx_state.reset()
        ctx_inventory.reset()

        hosts = ["somehost", "anotherhost", "someotherhost"]
        result = run_cli(
            "-y",
            ",".join(hosts),
            path.join("tests", "test_cli", "deploy", "deploy.py"),
            f'--chdir={path.join("tests", "test_cli", "deploy")}',
        )
        assert result.exit_code == 0, result.stdout

        assert inventory.data.get("hello") == "world"
        assert "leftover_data" in inventory.group_data
        assert inventory.group_data["leftover_data"].get("still_parsed") == "never_used"
        assert inventory.group_data["leftover_data"].get("_global_arg") == "gets_parsed"

    def test_load_group_data(self):
        ctx_state.reset()
        ctx_inventory.reset()

        hosts = ["somehost", "anotherhost", "someotherhost"]
        result = run_cli(
            "-y",
            ",".join(hosts),
            f'--group-data={path.join("tests", "test_cli", "deploy", "group_data")}',
            "exec",
            "uptime",
        )
        assert result.exit_code == 0, result.stdout

        assert inventory.data.get("hello") == "world"
        assert "leftover_data" in inventory.group_data
        assert inventory.group_data["leftover_data"].get("still_parsed") == "never_used"
        assert inventory.group_data["leftover_data"].get("_global_arg") == "gets_parsed"

    def test_load_group_data_file(self):
        ctx_state.reset()
        ctx_inventory.reset()

        hosts = ["somehost", "anotherhost", "someotherhost"]
        filename = path.join("tests", "test_cli", "deploy", "group_data", "leftover_data.py")
        result = run_cli(
            "-y",
            ",".join(hosts),
            f"--group-data={filename}",
            "exec",
            "uptime",
        )
        assert result.exit_code == 0, result.stdout

        assert "hello" not in inventory.data
        assert "leftover_data" in inventory.group_data
        assert inventory.group_data["leftover_data"].get("still_parsed") == "never_used"
        assert inventory.group_data["leftover_data"].get("_global_arg") == "gets_parsed"
