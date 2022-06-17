venv = 'solcast_env\Scripts\activate.bat &';

% starting index can't be negative
starting_index = "1051";
ending_index = "2589";
route_folder = 'ASC_route_refined';

status = system(join([venv, 'call_from_matlab ', route_folder, starting_index, ending_index, ' forecasts 0 -i dhi -i dni -p 1']));
