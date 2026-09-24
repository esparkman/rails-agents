import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest


SCRIPT = Path(__file__).with_name("sync_agents.py")
ROOT = SCRIPT.parent.parent


class ConversionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "output"

    def source(self, name="rails-example", body="Keep domain guidance.\n", extra=""):
        path = self.root / f"{name}.md"
        path.write_text(f"---\nname: {name}\ndescription: Example expert\nmodel: sonnet\ntools: Read,Write\n{extra}---\n\n{body}")
        return path

    def run_sync(self, *args, success=True, root=None, output=None):
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", str(root or self.root),
                                 "--output", str(output or self.output), *args],
                                capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_operator_regenerates_same_files_without_modifying_them(self):
        source = self.source(body='Ruby: "quotes", \\A, literal \\n, Unicode → and triple """.\n')
        self.run_sync()
        path = self.output / "rails-example.toml"
        before = path.read_bytes(), path.stat().st_mtime_ns
        self.run_sync()
        self.run_sync("--check")
        self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns))
        parsed = tomllib.loads(path.read_text())
        self.assertEqual(set(parsed), {"name", "description", "developer_instructions"})
        self.assertIn('Ruby: "quotes", \\A, literal \\n, Unicode → and triple """.', parsed["developer_instructions"])
        self.assertIn(hashlib.sha256(source.read_bytes()).hexdigest(), path.read_text())

    def test_operator_sees_stale_source_then_regenerates_it(self):
        path = self.source()
        self.run_sync()
        path.write_text(path.read_text() + "A new domain rule.\n")
        self.run_sync("--check", success=False)
        self.run_sync()
        self.assertIn("A new domain rule.", (self.output / "rails-example.toml").read_text())

    def test_operator_hand_edits_are_not_overwritten_even_when_other_files_need_updates(self):
        self.source()
        self.run_sync()
        path = self.output / "rails-example.toml"
        path.write_text(path.read_text() + "# my customization\n")
        self.source("rails-another")
        result = self.run_sync(success=False)
        self.assertIn("modified", result.stderr)
        self.assertTrue(path.read_text().endswith("# my customization\n"))
        self.assertFalse((self.output / "rails-another.toml").exists())

    def test_operator_receives_malformed_source_error_before_any_output(self):
        for malformed in ["no frontmatter", "---\nname: rails-example\n---\nbody",
                          "---\nname: rails-example\nname: twice\n---\nbody"]:
            with self.subTest(malformed=malformed):
                (self.root / "rails-example.md").write_text(malformed)
                self.run_sync(success=False)
                self.assertFalse(self.output.exists())

    def test_unknown_metadata_is_not_silently_discarded(self):
        self.source(extra="permissionMode: bypassPermissions\n")
        self.assertIn("unsupported", self.run_sync(success=False).stderr)

    def test_output_collision_and_stale_files_are_reported_without_deletion(self):
        self.source()
        self.output.mkdir()
        collision = self.output / "rails-example.toml"
        collision.write_text("name = 'personal-agent'\n")
        self.run_sync(success=False)
        self.assertEqual(collision.read_text(), "name = 'personal-agent'\n")
        collision.unlink()
        stale = self.output / "old-agent.toml"
        stale.write_text("name = 'old-agent'\n")
        self.assertIn("unexpected", self.run_sync(success=False).stderr)
        self.assertTrue(stale.exists())

    def test_name_mismatch_or_duplicate_cannot_write_outside_output(self):
        path = self.source()
        for name in ["../escape", "rails-another", "", "Rails-example"]:
            with self.subTest(name=name):
                path.write_text(f"---\nname: {name}\ndescription: Example\n---\nbody\n")
                self.run_sync(success=False)
                self.assertFalse(self.output.exists())

    def test_symlink_destination_is_not_followed(self):
        self.source()
        self.output.mkdir()
        personal = self.root / "personal.toml"
        personal.write_text("private")
        (self.output / "rails-example.toml").symlink_to(personal)
        self.run_sync(success=False)
        self.assertEqual(personal.read_text(), "private")

    def test_symlink_output_directory_is_not_followed(self):
        self.source()
        personal = self.root / "personal-agents"
        personal.mkdir()
        self.output.symlink_to(personal, target_is_directory=True)
        self.run_sync(success=False)
        self.assertEqual(list(personal.iterdir()), [])

    def test_check_does_not_create_missing_output(self):
        self.source()
        result = self.run_sync("--check", success=False)
        self.assertIn("stale/missing", result.stderr)
        self.assertFalse(self.output.exists())

    def test_new_tool_restriction_requires_explicit_adaptation(self):
        self.source(extra="disallowedTools: Write\n")
        self.assertIn("unsupported tool denylist", self.run_sync(success=False).stderr)

    def test_full_roster_preserves_guidance_and_adapts_runtime_contracts(self):
        self.run_sync(root=ROOT)
        sources = sorted([*ROOT.glob("rails-*.md"), *(ROOT / f"{name}.md" for name in
                          ("dhh-code-reviewer", "product-manager", "story-writer"))])
        self.assertEqual(len(sources), 23)
        self.assertEqual({p.stem for p in sources}, {p.stem for p in self.output.glob("*.toml")})
        for source in sources:
            with self.subTest(agent=source.stem):
                text = (self.output / f"{source.stem}.toml").read_text()
                instructions = tomllib.loads(text)["developer_instructions"]
                self.assertIn("expert Ruby on Rails engineer", instructions)
                self.assertNotIn("orchestrating Claude Code", instructions)
                self.assertNotIn(".claude/.current-story", instructions)
                self.assertNotIn("mcp__claude-in-chrome", instructions)
                self.assertNotIn("AskUserQuestion", instructions)
                self.assertNotIn("pilot supplies only", instructions)
                self.assertIn(hashlib.sha256(source.read_bytes()).hexdigest(), text)
                for heading in source.read_text().splitlines():
                    if heading.startswith("#"):
                        self.assertIn(heading, instructions)
                for example in re.findall(r"^```[^\n]*\n.*?^```", source.read_text(), re.MULTILINE | re.DOTALL):
                    self.assertIn(example, instructions, f"{source.name}: domain example was altered or dropped")
        qa = tomllib.loads((self.output / "rails-qa.toml").read_text())["developer_instructions"]
        self.assertIn("actual exposed schema", qa)
        story = tomllib.loads((self.output / "story-writer.toml").read_text())["developer_instructions"]
        self.assertIn("harness_engineering/Reference/books/agile-web-development", story)
        product = tomllib.loads((self.output / "product-manager.toml").read_text())["developer_instructions"]
        self.assertIn("Do not delete Fizzy boards, cards, or columns", product)


if __name__ == "__main__":
    unittest.main()
