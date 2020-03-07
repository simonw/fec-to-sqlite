from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="fec-to-sqlite",
    description="Save FEC campaign finance data to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/dogsheep/fec-to-sqlite",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["fec_to_sqlite"],
    entry_points="""
        [console_scripts]
        fec-to-sqlite=fec_to_sqlite.cli:cli
    """,
    install_requires=["sqlite-utils", "click", "requests", "fecfile", "tqdm"],
    extras_require={"test": ["pytest"]},
    tests_require=["fec-to-sqlite[test]"],
)
