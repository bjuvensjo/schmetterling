import os

from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="schmetterling",
    version="1.0.0",
    description="Pipeline",
    license="MIT",
    keywords="pipeline continuous build delivery",
    url="https://github.com/bjuvensjo/schmetterling",
    package_dir={'': 'src'},
    packages=['schmetterling'],
    # find_packages(where='./src', include=('schmetterling')),
    long_description=read('README.md'),
    classifiers=[
        "License :: OSI Approved :: Apache2 License",
    ],
    install_requires=[]
)
