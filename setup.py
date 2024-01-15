from setuptools import setup, find_packages

setup(
    name='xsnotif',
    version='0.0.2',
    description='XS Overlay notifications API',
    long_description=open('README.md').read(),
    author='Isaac Torbett',
    author_email='izacht13@email.com',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
