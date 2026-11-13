import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('regenerate', ROOT / 'scripts/rebuild-dependencies.py')
regen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regen)


class RegenerationTests(unittest.TestCase):
    def test_compiled_backends_export_dump_dependency(self):
        data = yaml.safe_load((ROOT / 'recipes/boost/all/dependencies/dependencies-1.92.0.yml').read_text())
        for backend in regen.STACKTRACE_DUMP_USERS:
            self.assertIn('stacktrace_dump', data['dependencies'][backend])
            self.assertIn('stacktrace', data['dependencies'][backend])
        self.assertNotIn('stacktrace_dump', data['dependencies']['stacktrace_noop'])
        self.assertNotIn('stacktrace_dump', data['dependencies']['stacktrace_dump'])
        self.assertIn('iconv', data['requirements']['locale'])
        self.assertIn('icu', data['requirements']['locale'])

    def test_pinned_head_does_not_allow_dirty_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', '-c', 'user.name=Test', '-c',
                    'user.email=test@example.invalid', *args], cwd=path, stderr=subprocess.DEVNULL)
            git('init')
            jam = path / 'Jamfile'
            jam.write_text('lib original ;\n')
            git('add', 'Jamfile')
            git('commit', '-m', 'initial')
            original = git('rev-parse', 'HEAD')
            regen.require_clean(path)
            jam.write_text('lib modified ;\n')
            with self.assertRaisesRegex(ValueError, 'Modified source'):
                regen.require_clean(path)
            git('add', 'Jamfile')
            with self.assertRaisesRegex(ValueError, 'Modified source'):
                regen.require_clean(path)
            git('reset', '--hard', 'HEAD')
            (path / 'untracked.jam').write_text('lib injected ;\n')
            with self.assertRaisesRegex(ValueError, 'Modified source'):
                regen.require_clean(path)
            self.assertEqual(git('rev-parse', 'HEAD'), original)

    def test_dirty_pinned_submodule_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            child = parent / 'libs/module'
            child.mkdir(parents=True)
            def git(directory, *args):
                return subprocess.check_output(['git', '-c', 'user.name=Test', '-c',
                    'user.email=test@example.invalid', *args], cwd=directory, stderr=subprocess.DEVNULL)
            git(parent, 'init')
            git(child, 'init')
            jam = child / 'Jamfile'
            jam.write_text('lib original ;\n')
            git(child, 'add', 'Jamfile')
            git(child, 'commit', '-m', 'module')
            commit = git(child, 'rev-parse', 'HEAD').decode().strip()
            git(parent, 'update-index', '--add', '--cacheinfo', f'160000,{commit},libs/module')
            git(parent, 'commit', '-m', 'pinned module')
            regen.validate_checkout(parent)
            jam.write_text('lib modified ;\n')
            with self.assertRaisesRegex(ValueError, 'Modified source checkout'):
                regen.validate_checkout(parent)
