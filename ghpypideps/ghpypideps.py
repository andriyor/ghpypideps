# TODO: fix import
# poetry run python ghpypideps/ghpypideps.py
# poetry run pytest --ignore=__pypackages__ -vv
# poetry run python example.py

from __future__ import absolute_import
try:
    from .source_finder import find_source_repo
except (ModuleNotFoundError, ImportError) as e:
    from source_finder import find_source_repo

import os
import ast
# [python - Proper way to parse requirements file after pip upgrade to pip 10.x.x? - Stack Overflow](https://stackoverflow.com/questions/49689880/proper-way-to-parse-requirements-file-after-pip-upgrade-to-pip-10-x-x)
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
import configparser

import github3
import httpx
from dotenv import load_dotenv

load_dotenv()

config = configparser.ConfigParser()
SETUP_CFG = 'setup.cfg'
SETUP_PY = 'setup.py'
OPTIONS_EXTRAS_REQUIRE = 'options.extras_require'

token = os.environ.get('GITHUB_TOKEN')
github = github3.login(token=token)


# PyNaCl
# Flask
class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.assigns = {}
        self.req = {}

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            if isinstance(node.value, ast.List):
                constants = []
                for elr in node.value.elts:
                    if isinstance(elr, ast.Constant):
                        constants.append(elr.value)
                self.assigns[node.targets[0].id] = constants

                # yarl
                if node.targets[0].id in ['setup_requires', 'tests_require', 'install_requires']:
                    self.req[node.targets[0].id] = constants

            if isinstance(node.value, ast.Dict):
                constants = []
                for val in node.value.values:
                    # python-cloud-core extras
                    if isinstance(val, ast.Constant):
                        constants.append(val.value)

                    # attrs
                    if isinstance(val, ast.List):
                        for elr in val.elts:
                            if isinstance(elr, ast.Constant):
                                constants.append(elr.value)
                self.assigns[node.targets[0].id] = constants

    def visit_Call(self, node):
        is_setuptools_setup = isinstance(node.func, ast.Attribute) and hasattr(node.func.value, 'id') and node.func.value.id == 'setuptools' and node.func.attr == 'setup'
        is_setup = isinstance(node.func, ast.Name) and (node.func.id == 'setup' or is_setuptools_setup)

        if is_setup or is_setuptools_setup:
            assigns_keys = self.assigns.keys()
            for key in node.keywords:
                # handle BinOp? https://github.com/matplotlib/matplotlib/blob/main/setup.py#L308
                for setup_arg in ['setup_requires', 'tests_require', 'install_requires']:
                    if key.arg == setup_arg:
                        if isinstance(key.value, ast.Name) and key.value.id in assigns_keys:
                            self.req[setup_arg] = self.assigns[key.value.id]

                        if isinstance(key.value, ast.List):
                            self.req[setup_arg] = [elt.value for elt in key.value.elts]

                        # wcwidth
                        if isinstance(key.value, ast.Constant):
                            self.req[setup_arg] = key.value.value.split(';')

                # TODO: use dict for keys?
                if key.arg == 'extras_require':
                    # python-cloud-core
                    if isinstance(key.value, ast.Name) and key.value.id in assigns_keys:
                        self.req['extras_require'] = self.assigns[key.value.id]

                    if isinstance(key.value, ast.Dict):
                        extras_require = []
                        for val in key.value.values:
                            # nacl
                            if isinstance(val, ast.Name):
                                deps = self.assigns.get(val.id)
                                # zope.interface
                                if deps:
                                    extras_require.extend(deps)

                            if isinstance(val, ast.List):
                                # Flask
                                extras_require.extend([elt.value for elt in val.elts])

                        self.req['extras_require'] = extras_require


def handle_requirements(uritemplate, path):
    req = uritemplate.file_contents(path).decoded.decode('utf-8')

    new_lines = []
    for line in req.split('\n'):
        if '-r' not in line:
            new_lines.append(line)

    req_file_name = 'requirements.txt'
    with open(req_file_name, "w") as file1:
        file1.write("\n".join(new_lines))

    req = []
    for r in parse_requirements(req_file_name, session=PipSession()):
        # ipython,google-auth
        if r.requirement != '.' and '.[' not in r.requirement and '..' not in r.requirement:
            req.append(r.requirement.strip())

    os.remove(req_file_name)
    return req


def search_requirements(uritemplate, owner, repository, req_files):
    url = f'https://api.github.com/search/code?q=repo:{owner}/{repository}+filename:requirements.txt'
    print('url')
    print(url)
    r = httpx.get(url)

    searched_req = {}

    items = r.json().get('items')
    if items:
        for item in items:
            if item['name'] not in req_files and 'lock' not in item['name']:
                req = handle_requirements(uritemplate, item['path'])
                searched_req[item['path']] = req

    return searched_req


def get_from_pypi(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    r = httpx.get(url)
    requires_dist = r.json()['info']['requires_dist']
    if not requires_dist:
        return []
    return requires_dist


# Jinja2
def handle_setup_cfg(uritemplate):
    setup_req = []
    req = uritemplate.file_contents(SETUP_CFG).decoded.decode('utf-8')

    with open(SETUP_CFG, "w") as file1:
        file1.write(req)

    config.read(SETUP_CFG)
    sections = config.sections()

    if OPTIONS_EXTRAS_REQUIRE in sections:
        for key in config[OPTIONS_EXTRAS_REQUIRE]:
            deps = config[OPTIONS_EXTRAS_REQUIRE][key].strip().split('\n')
            deps_without_empty = [dep for dep in deps if dep]
            setup_req.append({key: deps_without_empty})

    # boto3
    if 'metadata' in sections:
        for section in ['requires_dist']:
            requires = config['metadata'].get(section)
            if requires:
                deps = requires.strip().split('\n')
                setup_req.append({section: deps})

    # tqdm
    if 'options' in sections:
        for section in ['setup_requires', 'tests_require', 'install_requires']:
            requires = config['options'].get(section)
            if requires:
                deps = requires.strip().split('\n')
                setup_req.append({section: deps})

    os.remove(SETUP_CFG)
    return setup_req


def fetch_deps(package_name):
    req_files = []
    all_req = {
        'requirements.txt': {}
    }

    url = find_source_repo(package_name)
    print(url)
    if url is None or 'github' not in url:
        return

    if url[-1] == '/':
        url = url[:-1]

    owner, repository = url.replace('https://github.com/', '').replace('http://github.com/', '').split("/")
    uritemplate = github.repository(owner, repository)

    for content in uritemplate.directory_contents(''):
        content_obj = content[1]

        if content_obj.type == 'dir' and content_obj.name == 'requirements':
            for dir_content in uritemplate.directory_contents(content_obj.name):
                # click
                if dir_content[1].type == 'file':
                    if '.txt' in dir_content[0] and 'lock' not in dir_content[0]:
                        req_files.append(content[0])
                        req = handle_requirements(uritemplate, dir_content[1].path)
                        all_req['requirements.txt'][dir_content[1].path] = req

                # matplotlib
                if dir_content[1].type == 'dir':
                    for nested_dir_content in uritemplate.directory_contents(dir_content[1].path):
                        if '.txt' in nested_dir_content[0] and 'lock' not in nested_dir_content[0]:
                            req_files.append(nested_dir_content[0])
                            req = handle_requirements(uritemplate, nested_dir_content[1].path)
                            all_req['requirements.txt'][nested_dir_content[1].path] = req

        if content_obj.type == 'file':
            if 'requirements' in content_obj.name and '.txt' in content_obj.name and 'lock' not in content_obj.name:
                req_files.append(content_obj.name)
                req = handle_requirements(uritemplate, content_obj.name)
                all_req['requirements.txt'][content_obj.name] = req

            if content_obj.name == SETUP_CFG:
                setup_cfg_req = handle_setup_cfg(uritemplate)
                all_req[SETUP_CFG] = setup_cfg_req

            if content_obj.name == SETUP_PY:
                req = uritemplate.file_contents(SETUP_PY).decoded.decode('utf-8')

                try:
                    tree = ast.parse(req)
                    analyzer = Analyzer()
                    analyzer.visit(tree)
                    setup_py_req = analyzer.req
                    all_req[SETUP_PY] = setup_py_req
                except SyntaxError as e:
                    # msrest, azure-common
                    print(e)

    requires_dist = get_from_pypi(package_name)
    all_req['pypi'] = requires_dist

    req = search_requirements(uritemplate, owner, repository, req_files)
    all_req['requirements.txt'].update(req)
    return all_req
