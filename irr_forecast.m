venv = 'solcast_env\Scripts\activate.bat &';
status = system(join([venv, 'schedule ASC_Route 5 1 starting_index forecasts 0 -i dhi -i dni']));
