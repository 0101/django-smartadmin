from setuptools import setup

import smartadmin


setup(
    name='django-smartadmin',
    version=smartadmin.__versionstr__,
    description='Django ModelAdmin for the lazy.',
    long_description=open('README.rst').read(),
    author='Petr Pokorny',
    author_email='petr@innit.cz',
    license='MIT',
    url='http://0101.github.com/django-smartadmin/',
    packages=['smartadmin'],
    include_package_data=True,
    install_requires=(
         'setuptools>=0.6b1',
         'pipetools>=0.1.7',
    ),
)
