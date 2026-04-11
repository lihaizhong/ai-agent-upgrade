from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import importlib.util


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "__main__.py"

spec = importlib.util.spec_from_file_location(
    "prompt_learning_workspace",
    REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "workspace.py",
)
if spec is None or spec.loader is None:
    raise ImportError("Cannot load prompt-learning workspace module")
workspace_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = workspace_module
spec.loader.exec_module(workspace_module)


class TestWorkspaceFallback(unittest.TestCase):
    def test_normalize_workspace_username_returns_defaults_when_empty(self) -> None:
        result = workspace_module.normalize_workspace_username(None)
        self.assertEqual(result, "defaults")

    def test_normalize_workspace_username_returns_defaults_for_empty_string(
        self,
    ) -> None:
        result = workspace_module.normalize_workspace_username("")
        self.assertEqual(result, "defaults")

    def test_normalize_workspace_username_preserves_valid_username(self) -> None:
        result = workspace_module.normalize_workspace_username("test-user")
        self.assertEqual(result, "test-user")

    def test_normalize_workspace_username_replaces_spaces(self) -> None:
        result = workspace_module.normalize_workspace_username("Test User")
        self.assertEqual(result, "Test-User")

    @mock.patch("subprocess.run")
    def test_resolve_workspace_identity_uses_fallback_when_no_git_username(
        self, mock_run
    ) -> None:
        mock_run.side_effect = OSError("git not found")
        test_root = Path(tempfile.mkdtemp(prefix="test-ws-"))
        self.addCleanup(lambda: shutil.rmtree(test_root, ignore_errors=True))
        with mock.patch.dict(
            os.environ, {"PROMPT_LEARNING_WORKSPACE_ROOT": str(test_root)}
        ):
            identity = workspace_module.resolve_workspace_identity()
        self.assertEqual(identity["workspace_user"], "defaults")
        self.assertTrue(identity.get("using_fallback"))

    @mock.patch("subprocess.run")
    def test_fallback_workspace_created(self, mock_run) -> None:
        mock_run.side_effect = OSError("git not found")
        test_root = Path(tempfile.mkdtemp(prefix="test-ws-"))
        self.addCleanup(lambda: shutil.rmtree(test_root, ignore_errors=True))
        with mock.patch.dict(
            os.environ, {"PROMPT_LEARNING_WORKSPACE_ROOT": str(test_root)}
        ):
            workspace_module.ensure_workspace(
                REPO_ROOT / "agent-skills" / "prompt-learning"
            )
        defaults_workspace = test_root / "defaults"
        self.assertTrue(defaults_workspace.exists())
        self.assertTrue((defaults_workspace / "profile" / "learner.json").exists())


if __name__ == "__main__":
    import shutil

    unittest.main()
