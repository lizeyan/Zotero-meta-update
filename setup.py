from pathlib import Path

import pkg_resources
from setuptools import setup, find_packages


def parse_requirements(path):
    with (Path(__file__).parent / path).open() as requirements_txt:
        install_requires = [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_requires


def read_readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='Zotero-meta-update',
    version='0.1.1',
    description="",
    author='Zeyan Li',
    author_email='li_zeyan@icloud.com',
    url='https://github.com/lizeyan/Zotero-meta-update',
    packages=find_packages(),
    project_urls={
        "Bug Tracker": "https://github.com/lizeyan/Zotero-meta-update/issues",
        "Source Code": "https://github.com/lizeyan/Zotero-meta-update",
    },
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    python_requires='>=3.10',
    scripts=[
        'bin/update_zotero_meta'
    ]
)
