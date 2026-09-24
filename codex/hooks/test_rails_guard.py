import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HOOK = Path(__file__).with_name("rails_guard.py")


class GuardJourneys(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.create_repo("project", "main")

    def create_repo(self, name, branch):
        path = self.root / name
        path.mkdir()
        self.git(path, "init", "-b", branch)
        return path

    def git(self, path, *args):
        return subprocess.run(["git", "-C", str(path), *args], capture_output=True,
                              text=True, check=True).stdout

    def hook(self, payload, event="PreToolUse"):
        result = subprocess.run([sys.executable, str(HOOK), event],
                                input=json.dumps(payload), capture_output=True,
                                text=True, check=True, cwd=self.repo)
        return json.loads(result.stdout)

    def edit(self, path="new/deep/file.rb", **extra):
        return self.hook({"cwd": str(self.repo), "tool_name": "apply_patch",
                          "tool_input": {"command": f"*** Begin Patch\n*** Add File: {path}\n+hello\n*** End Patch"}, **extra})

    def denied(self, result):
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def feature(self):
        self.git(self.repo, "switch", "-c", "feature/test")

    def test_operator_cannot_edit_main_even_in_fresh_nested_directory(self):
        self.denied(self.edit())

    def test_operator_can_edit_feature_branch(self):
        self.feature()
        self.assertEqual(self.edit(), {})

    def test_move_into_other_default_branch_is_denied(self):
        self.feature()
        other = self.create_repo("other", "master")
        command = f"*** Begin Patch\n*** Update File: before.rb\n*** Move to: {other}/new/file.rb\n@@\n-a\n+b\n*** End Patch"
        self.denied(self.hook({"tool_input": {"command": command}}))

    def test_symlink_into_default_branch_is_denied(self):
        self.feature()
        other = self.create_repo("other", "main")
        (self.repo / "linked").symlink_to(other, target_is_directory=True)
        self.denied(self.edit("linked/deep/file.rb"))

    def test_every_file_in_a_native_patch_is_checked(self):
        self.feature()
        other = self.create_repo("other", "main")
        command = f"*** Begin Patch\n*** Add File: first.rb\n+one\n*** Add File: {other}/second.rb\n+two\n*** End Patch"
        self.denied(self.hook({"tool_input": {"command": command}}))

    def test_local_origin_default_branch_is_protected(self):
        self.git(self.repo, "symbolic-ref", "HEAD", "refs/heads/trunk")
        self.git(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        self.denied(self.edit())

    def test_legacy_file_payload_uses_payload_cwd(self):
        self.denied(self.hook({"cwd": str(self.repo), "tool_input": {"file_path": "nested/a.rb"}}))

    def test_malformed_payload_is_denied(self):
        for value in [{}, {"tool_input": {"command": "garbage"}}, {"tool_input": {"command": 2}}, {"tool_input": {"file_path": ""}}]:
            with self.subTest(value=value):
                self.denied(self.hook(value))
        result = subprocess.run([sys.executable, str(HOOK), "PreToolUse"], input="{",
                                capture_output=True, text=True, check=True)
        self.denied(json.loads(result.stdout))

    def test_pipeline_warns_then_blocks_and_explicit_small_fix_allows(self):
        self.feature()
        (self.repo / "Gemfile").touch()
        markers = self.repo / ".codex"
        markers.mkdir()
        self.assertIn("PIPELINE WARN", self.edit("app/models/item.rb")["hookSpecificOutput"]["additionalContext"])
        (markers / ".pipeline-block").touch()
        self.denied(self.edit("app/models/item.rb"))
        (markers / ".small-fix").write_text("Independent correction")
        self.assertIn("SMALL-FIX", self.edit("app/models/item.rb")["hookSpecificOutput"]["additionalContext"])
        (markers / ".small-fix").unlink()
        (markers / ".current-story").write_text("DoR: PASSED\n")
        self.assertEqual(self.edit("app/models/item.rb"), {})
        self.assertEqual(self.edit("test/models/item_test.rb"), {})

    def test_stop_reports_real_rspec_journey_changes_without_claiming_review(self):
        self.feature()
        for name in ["app/controllers/items_controller.rb", "spec/system/items_spec.rb"]:
            file = self.repo / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch()
        message = self.hook({}, "Stop")["systemMessage"]
        self.assertIn("cannot attest", message)
        self.assertNotIn("No changed operator", message)
        self.assertEqual(self.hook({"stop_hook_active": True}, "Stop"), {})

    def test_stop_returns_valid_empty_json_without_changes(self):
        self.assertEqual(self.hook({}, "Stop"), {})

    def test_stop_recognizes_tracked_ruby_modification_and_rejects_head_receipt(self):
        file = self.repo / "worker.rb"
        file.write_text("before\n")
        self.git(self.repo, "add", "worker.rb")
        self.git(self.repo, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "Initial")
        file.write_text("after\n")
        (self.repo / ".codex").mkdir()
        (self.repo / ".codex/.last-review").write_text(self.git(self.repo, "rev-parse", "HEAD"))
        self.assertIn("not accepted", self.hook({}, "Stop")["systemMessage"])

    def test_session_reports_disk_roster_as_unverified_callable_roles(self):
        message = self.hook({}, "SessionStart")["hookSpecificOutput"]["additionalContext"]
        self.assertIn("not proof", message)

    def test_nonrepo_and_detached_head_are_allowed(self):
        self.assertEqual(self.edit(str(self.root / "outside.rb")), {})
        (self.repo / "README").touch()
        self.git(self.repo, "add", "README")
        self.git(self.repo, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "Initial")
        self.git(self.repo, "checkout", "--detach")
        self.assertEqual(self.edit(), {})


if __name__ == "__main__":
    unittest.main()
