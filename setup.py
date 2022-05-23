from setuptools import setup

setup(
    name='irr_forecast',
    version='0.1',
    py_modules=['irr_forecast'],
    install_requires=[
        'requests',
        'scipy',
        'ratelimit',
        'click',
        'pandas',
        'numpy'
    ],
    entry_points='''
        [console_scripts]
        call-to-end = irr_forecast:call_to_end
        get-coords = irr_forecast:get_coords
        call-count = irr_forecast:check_call_count
        schedule = irr_forecast:schedule
    ''',
)   
