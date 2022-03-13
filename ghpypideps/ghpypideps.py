import json
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

from source_finder import find_source_repo

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
                            self.req['tests_require'] = [elt.value for elt in key.value.elts]

                # TODO: use dict for kkeys?
                if key.arg == 'extras_require':
                    # python-cloud-core
                    if isinstance(key.value, ast.Name) and key.value.id in assigns_keys:
                        self.req['extras_require'] = self.assigns[key.value.id]

                    if isinstance(key.value, ast.Dict):
                        extras_require = []
                        for val in key.value.values:
                            # nacl
                            if isinstance(val, ast.Name):
                                extras_require.extend(self.assigns[val.id])
                            if isinstance(val, ast.List):
                                # Flask
                                extras_require.extend([elt.value for elt in val.elts])

                        self.req['extras_require'] = extras_require

    def flat(self):
        return [item for sublist in self.req.values() for item in sublist]


def handle_requirements(uritemplate, path):
    req = uritemplate.file_contents(path).decoded.decode('utf-8')

    new_lines = []
    for line in req.split('\n'):
        if '-r' not in line:
            new_lines.append(line)

    req_file_name = 'requirements.txt'
    with open(req_file_name, "w") as file1:
        file1.write("\n".join(new_lines))
    
    req = [r.requirement for r in parse_requirements(req_file_name, session=PipSession())]
    os.remove(req_file_name)
    return req


def search_requirements(uritemplate, owner, repository, req_files):
    url = f'https://api.github.com/search/code?q=repo:{owner}/{repository}+filename:requirements.txt'
    print(url)
    r = httpx.get(url)

    searched_req = {}
    for item in r.json()['items']:
        if item['name'] not in req_files and 'lock' not in item['name']:
            print(item['path'])
            req = handle_requirements(uritemplate, item['path'])
            searched_req[item['path']] = req
            print(req)
            print()
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
            setup_req.extend(config[OPTIONS_EXTRAS_REQUIRE][key].strip().split('\n'))

    # tqdm
    if 'options' in sections:
        for section in ['setup_requires', 'tests_require', 'install_requires']:
            requires = config['options'].get(section)
            if requires:
                setup_req.extend(requires.strip().split('\n'))

    os.remove(SETUP_CFG)
    return setup_req


def fetch_deps(package_name):
    req_files = []
    all_req = {}

    url = find_source_repo(package_name)
    if 'github' not in url:
        return

    if url[-1] == '/':
        url = url[:-1]
    
    owner, repository = url.replace('https://github.com/', '').replace('http://github.com/', '').split("/")
    uritemplate = github.repository(owner, repository)

    for content in uritemplate.directory_contents(''):
        content_obj = content[1]

        # click
        # TODO: walk through directory https://github.com/matplotlib/matplotlib/tree/main/requirements
        if content_obj.type == 'dir' and content_obj.name == 'requirements':
            for dir_content in uritemplate.directory_contents(content_obj.name):
                if '.txt' in dir_content[0] and 'lock' not in dir_content[0]:
                    req_files.append(content[0])
                    print(f'{content[1].path}/{dir_content[0]}')
                    full_path = f'{content_obj.path}/{dir_content[0]}'
                    req = handle_requirements(uritemplate, full_path)
                    print(req)
                    print()
                    all_req[full_path] = req

        if content_obj.type == 'file':
            if 'requirements' in content_obj.name and '.txt' in content_obj.name and 'lock' not in content_obj.name:
                print(content_obj.name)
                req_files.append(content_obj.name)
                req = handle_requirements(uritemplate, content_obj.name)
                all_req[content_obj.name] = req
                print(req)
                print()

            if content_obj.name == SETUP_CFG:
                print(content_obj.path)
                setup_cfg_req = handle_setup_cfg(uritemplate)
                print(setup_cfg_req)
                all_req[SETUP_CFG] = setup_cfg_req

            if content_obj.name == SETUP_PY:
                print(content_obj.path)
                req = uritemplate.file_contents(SETUP_PY).decoded.decode('utf-8')

                tree = ast.parse(req)
                analyzer = Analyzer()
                analyzer.visit(tree)
                setup_py_req = analyzer.flat()
                print(setup_py_req)
                print()
                all_req[SETUP_PY] = setup_py_req

    requires_dist = get_from_pypi(package_name)
    all_req['pypi'] = requires_dist
    print('pypi')
    print(requires_dist)
    print()
    
    req = search_requirements(uritemplate, owner, repository, req_files)
    all_req.update(req)
    print('searched')
    print(req)
    print()
    print('all')
    print(all_req)

    return all_req


if __name__ == "__main__":
    # package_name = 'python-dateutil'
    # package_name = 'six'
    # package_name = 'urllib3'
    # package_name = 'PyYAML'
    # package_name = 'numpy'
    package_name = 'click'
    # package_name = 'botocore'
    # package_name = 'matplotlib'
    # package_name = 'attrs'
    # package_name = 'pyrsistent'
    # package_name = 'jmespath'
    # package_name = 'Jinja2'
    # package_name = 'PyJWT'
    # package_name = 'oauthlib'
    # package_name = 'requests-oauthlib'
    # package_name = 'google-cloud-core'
    # package_name = 'Werkzeug'
    # package_name = 'Flask'
    # package_name = 'scipy'
    # package_name = 'Pillow'
    # package_name = 'pluggy'
    # package_name = 'tqdm'
    # package_name = 'GitPython'
    # package_name = 'gunicorn'
    # package_name = 'PyNaCl'
    # package_name = 'requests'

    deps = fetch_deps(package_name)
    with open(f'tests/results/{package_name}.json', 'w') as outfile:
        json.dump(deps, outfile, indent=2)


    # with open("examples/setup_mat.py", "r") as source:
    #     tree = ast.parse(source.read())
    #     print(ast.dump(tree, indent=4))

    # analyzer = Analyzer()
    # analyzer.visit(tree)
    # print(analyzer.assigns)
    # print(analyzer.req)
    # print(analyzer.flat())