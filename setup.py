"""Setup script for the python-act library module"""

from os import path

from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="provreq",
    version="0.1.5",
    author="mnemonic AS",
    zip_safe=True,
    author_email="opensource@mnemonic.no",
    description="Provreq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="provreq,attack,mnemonic",
    entry_points={
        "console_scripts": [
            "provreq-generate = provreq.tools.generate:main",
            "provreq-promise-usage = provreq.tools.promise_usage:main",
            "provreq-agent = provreq.tools.show_agent:main",
            "provreq-promise = provreq.tools.show_promise:main",
            "provreq-bundle = provreq.tools.show_bundle:main",
            "provreq-promise-search = provreq.tools.promise_search:main",
            "provreq-config = provreq.tools.config:main",
            "provreq-format-json = provreq.tools.format_json:main",
        ]
    },
    # Include ini-file(s) from act/workers/etc
    package_data={"provreq.tools": ["etc/*.ini"]},
    packages=["provreq.tools", "provreq.tools.libs"],
    # https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages
    # __init__.py under all packages under in the act namespace must contain exactly string:
    # __path__ = __import__('pkgutil').extend_path(__path__, __name__)
    namespace_packages=["provreq"],
    url="https://github.com/mnemonic-no/provreq",
    install_requires=["tabulate", "pytest", "pydantic", "pyattck", "caep"],
    python_requires=">=3.6, <4",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
)
