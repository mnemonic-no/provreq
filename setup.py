"""Setup script for the python-act library module"""

from os import path

from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), "rb") as f:
    long_description = f.read().decode('utf-8')

setup(
    name="aep",
    version="0.1.4",
    author="mnemonic AS",
    zip_safe=True,
    author_email="opensource@mnemonic.no",
    description="Adversary Emulation Planner (AEP)..",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
    keywords="aep,attack,mnemonic",
    entry_points={
        'console_scripts': [
            'aep-generate = aep.tools.generate:main',
            'aep-promise-usage = aep.tools.promise_usage:main',
            'aep-technique = aep.tools.show_technique:main',
            'aep-promise = aep.tools.show_promise:main',
            'aep-bundle = aep.tools.show_bundle:main',
            'aep-promise-search = aep.tools.promise_search:main',
            'aep-config = aep.tools.config:main',
            'aep-format-json = aep.tools.format_json:main',
        ]
    },

    # Include ini-file(s) from act/workers/etc
    package_data={'aep.tools': ['etc/*.ini']},
    packages=["aep.tools", "aep.tools.libs"],

    # https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages
    # __init__.py under all packages under in the act namespace must contain exactly string:
    # __path__ = __import__('pkgutil').extend_path(__path__, __name__)
    namespace_packages=['aep'],
    url="https://github.com/mnemonic-no/aep",
    install_requires=['tabulate', 'pytest', 'pydantic', 'pyattck', 'caep'],

    python_requires='>=3.6, <4',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
)
