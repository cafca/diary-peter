"""Script to install Diary Peter."""
try:
    from setuptools import setup
except ImportError:
    print("Not using setuptools")
    from distutils.core import setup

setup(
    name="Diary Peter",
    version="0.1.0",
    author="Vincent Ahrend",
    author_email="mail@vincentahrend.com",
    url="https://github.com/ciex/diary-peter/",
    scripts=["main.py", "create_database.py"],
    packages=["diary_peter"],
    license="All Rights Reserved",
    description="A Conversational Diary",
    long_description=open("README.md").read(),
    install_requires=open("requirements.txt").read()
)
