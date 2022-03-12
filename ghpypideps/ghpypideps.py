import json
import os
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
OPTIONS_EXTRAS_REQUIRE = 'options.extras_require'

token = os.environ.get('GITHUB_TOKEN')
github = github3.login(token=token)

# TODO: walk through directory https://github.com/matplotlib/matplotlib/tree/main/requirements


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
                setup_req = handle_setup_cfg(uritemplate)
                print(setup_req)
                all_req[SETUP_CFG] = setup_req

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
    # package_name = 'click'
    # package_name = 'botocore'
    # package_name = 'matplotlib'
    # package_name = 'attrs'
    # package_name = 'pyrsistent'
    # package_name = 'jmespath'
    # package_name = 'Jinja2'
    package_name = 'PyJWT'
    deps = fetch_deps(package_name)

    with open(f'tests/results/{package_name}.json', 'w') as outfile:
        json.dump(deps, outfile, indent=4)
