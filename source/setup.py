from setuptools import setup

setup(
    name='sparc_dash',
    version='0.1',
    py_modules=['sparc_dash_cli', 'sparc_dash'],
    install_requires=[
        'Click','Blackfynn'
    ],
    entry_points='''
        [console_scripts]
        sparc_dash=sparc_dash_cli:cli
    ''',
)