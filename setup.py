# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages


def _get_version():
    v_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'rest_arch', '__init__.py')
    ver_info_str = re.compile(r".*version_info = \((.*?)\)", re.S). \
        match(open(v_file_path).read()).group(1)
    return re.sub(r'(\'|"|\s+)', '', ver_info_str).replace(',', '.')

entry_points = [
    # skt
    "skt = rest_arch.skt.cmds:skt"
]

data = [
    "static/*",
    "skt/static/*"
]

setup(
    name="rest_arch",
    version=_get_version(),
    description="A Restful Framework Based On Gunicorn",
    long_description=open("README.md").read(),
    author="kiven",
    author_email="kiven.mr@gmail.com",
    packages=find_packages(),
    package_data={"": ["LICENSE"], "skt": data},
    url="https://github.com/MrKiven/REST_ARCH/",
    tests_require=[
        'pytest==2.5.2',
        'pytest-cov==1.8.1',
        'pytest-xdist==1.13.1',
        'mock==1.0.1',
    ],
    entry_points={"console_scripts": entry_points},
    install_requires=[
        'PyMySQL==0.6.2',
        'redis==2.10.5',
        'requests==2.7.0',
        'SQLAlchemy==0.9.3',
        'PyYAML==3.11',
        'ipython==4.1.2',
        'gipc==0.5.0',
        'wheel==0.24.0',
        'click==5.1',
        'Fabric==1.10.2',
        'Jinja2==2.7.3',
    ],

)
