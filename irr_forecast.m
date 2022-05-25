venv = 'solcast_env\Scripts\activate.bat &';

% starting index can't be negative
starting_index = "2500"
route_folder = 'ASC_route'

status = system(join([venv, 'call_from_matlab ', route_folder, ' 5 1 ', starting_index, ' forecasts 0 -i dhi -i dni']));
