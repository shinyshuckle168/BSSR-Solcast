from setuptools import setup

setup(
    name='irr_forecast',
    version='0.1',
    py_modules=['irr_forecast'],
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',

        'requests',
        'ratelimit',
        'click',
    ],
    entry_points='''
        [console_scripts]
        call_from_matlab = irr_forecast:call_from_matlab
        schedule = irr_forecast:schedule
    ''',
)   
