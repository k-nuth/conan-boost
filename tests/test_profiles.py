import ast
import pathlib
import unittest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RecipeCompatibility(unittest.TestCase):
    def test_recipe_api_is_preserved(self):
        def interface(path):
            tree = ast.parse(path.read_text())
            recipe = next(node for node in tree.body if isinstance(node, ast.ClassDef))
            return {target.id: ast.dump(node.value) for node in recipe.body
                    if isinstance(node, ast.Assign) for target in node.targets
                    if isinstance(target, ast.Name) and target.id in
                    {"name", "settings", "options", "default_options"}}
        self.assertEqual(interface(ROOT / 'upstream/boost/all/conanfile.py'),
                         interface(ROOT / 'recipes/boost/all/conanfile.py'))

    def test_thread_profile_tracks_dependency_closure(self):
        data = yaml.safe_load((ROOT / 'recipes/boost/all/dependencies/dependencies-1.92.0.yml').read_text())
        options = dict(line.split('=', 1) for line in (ROOT / 'profiles/native-minimal').read_text().splitlines()
                       if line.startswith('boost/*:without_'))
        closure = set()
        def visit(name):
            if name not in closure:
                closure.add(name)
                for dependency in data['dependencies'].get(name, []):
                    visit(dependency)
        visit('thread')
        self.assertEqual({k.removeprefix('boost/*:without_') for k, v in options.items() if v == 'False'}, closure)
        self.assertEqual(set(options), {'boost/*:without_' + name for name in data['configure_options']})

    def test_archive_is_pinned(self):
        data = yaml.safe_load((ROOT / 'recipes/boost/all/conandata.yml').read_text())
        self.assertEqual(data['sources']['1.92.0']['sha256'],
                         '5c1d40cb8e19adbf740a4ec2da35b3e58f3f5804b1dce44deb53df72193cbc6c')

    def test_only_latest_version_is_supported(self):
        config = yaml.safe_load((ROOT / 'recipes/boost/config.yml').read_text())
        source = yaml.safe_load((ROOT / 'recipes/boost/all/conandata.yml').read_text())
        self.assertEqual(set(config['versions']), {'1.92.0'})
        self.assertEqual(set(source['sources']), set(config['versions']))
        self.assertEqual({p.stem.removeprefix('dependencies-') for p in
                          (ROOT / 'recipes/boost/all/dependencies').glob('dependencies-*.yml')},
                         set(config['versions']))
