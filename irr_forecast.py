import math, csv, time, os
import numpy as np, scipy.stats as st, matplotlib.pyplot as plt
import requests, click
from ratelimit import limits

# free trial
api_key_free = 'g7AehjAxhZPilJdO3aEyVRDmTikQAhs4'

# premium
api_key_premium = 'HwqyKe0MKq9VruZ4uTDTiejp4CF7Qm4a'

call_count = 0

def distance(coord1, coord2):
    # calculates distance between two latitude-longitude coordinates using the Haversine formula

    # coordinates are strings of comma separated latitude and longitude 
    lat1, long1 = [float(i)*math.pi/180 for i in coord1.split(",")]
    lat2, long2 = [float(i)*math.pi/180 for i in coord2.split(",")]

    r = 6371
    a = (math.sin((lat2-lat1)/2))**2
    b = math.cos(lat1)*math.cos(lat2)*(math.sin((long2-long1)/2))**2
    return 2*r*math.asin((a+b)**0.5)

    # lat1, lon1 = [float(i) for i in coord1.split(",")]
    # lat2, lon2 = [float(i) for i in coord2.split(",")]

    # R = 6371e3;                 
    # phi_1 = lat1 * math.pi/180      
    # phi_2 = lat2 * math.pi/180
    # delPhi = (lat2-lat1) * math.pi/180
    # delLambda = (lon2-lon1) * math.pi/180
    # a =  ( math.sin(delPhi/2) * math.sin(delPhi/2) ) + ( math.cos(phi_1) * math.cos(phi_2) * math.sin(delLambda/2) * math.sin(delLambda/2) )
    # c = 2 * math.atan2((a**0.5), (1-a)**0.5)
    # return (R * c)/1000

def get_coords(folder, d):
    '''
    Constructs a list of latitudes and longitudes from sorted csv files. Coordinates are discarded if they are less than 'd' kilometers apart from their predecessor.

    Parameters
    ----------
    folder (string): Name of folder containing csvs whose first and second columns are longitudes and latitudes respectively. The csv files must be sorted alphanumerically. 

    Returns
    ------- 
    coords (list): List of comma separated latitudes and longitudes.
    d (int): Consecutive coordinates must be greater than or equal to d kilometers apart

    Notes

    -----
    Although the order of the coordinates in the provided csv files is longitude, latitude, the 'coords' list is ordered latitude, longitude in accordance with EPSG:4326. 
    ''' 

    path = os.getcwd()
    fnames = os.listdir(path + "\\" + folder)
    fnames.sort()

    coords = []
    for fname in fnames:
        with open(path + "\\" + folder + "\\" + fname, "r", encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for r in reader:
                new_coord = "{},{}".format(r[1], r[0])
                if coords != []:
                    # skips row if coordinates are less than a kilometer apart
                    if distance(coords[-1], new_coord) < d:
                        continue
                coords.append(new_coord)

    return coords

@limits(calls = 5000, period = 1200)
#5000/20min
def call_by_site(lat, long, call_type, paid = 0, hours = 168):
    '''
    Makes an API call for a given site.
    
    Please check Solcast documentation for more details. 
    
    Parameters
    ----------
    lat (float): Latitude of site.
    long (float): Longitude of site.
    call_type (string): Forecast ('forecasts') or estimated actuals ('estimated_actuals').
    paid (bool): If 0, the free trial Solcast account is used. If 1, the premium Solcast account is used. Default is 0.
    hours (int): How many hours into the future/past to make call for (NOTE: Max is 168). Default is 168.
    
    Returns
    -------
    call (response object): Forecast or actuals response in JSON format. a
    '''

    if paid == 0:
        api_key = 'g7AehjAxhZPilJdO3aEyVRDmTikQAhs4'
    elif paid == 1:
        api_key = 'HwqyKe0MKq9VruZ4uTDTiejp4CF7Qm4a'

    payload = {
        'api_key': api_key,
        'latitude': lat, 
        'longitude':long,
        'hours': hours
    }
    
    headers = {
      'Content-Type': 'application/json'
    }
    
    url = 'https://api.solcast.com.au/world_radiation/{}'.format(call_type)
    call = requests.get(url, params=payload, headers=headers)
    breakpoint()

    return call

def call_to_end(coords, index, irr_types, call_type, call_count, paid = 0, hours = 168):
    '''
    Finds irradiance values for sites in a list starting from some index and writes these values to csv files in the 'calls' folder. 

    Parameters
    ----------
    coords (list): List of comma separated latitudes and longitudes.
    index (int): The index of the first site in coords to make forecasts for.
    irr_types (list): List of desired data from call, e.g. GHI ('ghi'), DHI ('dhi'), or DNI ('dni'). 
    call_type (string): Forecast ('forecasts') or estimated actuals ('estimated_actuals').
    call_count (int): The number of API calls made since running the script.
    paid (bool): If 0, the free trial Solcast account is used. If 1, the premium Solcast account is used. Default is 0.
    hours (int): How many hours into the future to make forecasts for (NOTE: Max is 168). Default is 168.
    
    Returns
    -------
    call_count (int): The number of API calls made since running the script.
    '''        
    
    # list of coords to end of race
    coords_new = coords[index:]
        
    call_count_new = check_call_count(len(coords_new), call_count)

    # makes calls for each site in new coords list and appends them to a list
    calls = []
    for i in range(len(coords_new)):
        calls.append(call_by_site(coords_new[i].split(",")[0], coords_new[i].split(",")[1], call_type, paid, hours).json()[call_type])
    
    # list of times the forecast is made for
    time_ls = []
    for i in range(len(calls[0])):
        time_ls.append(calls[0][i]['period_end'])   
    
    # current time for naming csvs
    timestr = time.strftime("%Y%m%d-%H%M%S")  
    # creates csvs for each irr type
    for irr_type in irr_types:
        irr_string = "calls/{}_{}_{}.csv".format(timestr, irr_type, call_type)
        with open(irr_string, "a", newline = '') as irr_csv:
            irr_csvWriter = csv.writer(irr_csv, delimiter = ',')
            # first row
            irr_csvWriter.writerow(['latitude', 'longitude'] + time_ls) 

    for i in range(len(coords_new)):    
        # makes call for each site   
        call = call_by_site(coords_new[i].split(",")[0], coords_new[i].split(",")[1], call_type, hours).json()[call_type] 
        # writes call data to a different csv for each irr type
        for irr_type in irr_types:
            # file name         
            irr_string = "calls/{}_{}_{}.csv".format(timestr, irr_type, call_type)

            with open(irr_string, "a", newline = '') as irr_csv:
                irr_csvWriter = csv.writer(irr_csv, delimiter = ',')
                
                # writes site forecast to csv     
                irr_ls = []    
                for j in range(len(call)):   
                    irr_ls.append(call[j][irr_type])    
                irr_csvWriter.writerow([coords_new[i].split(",")[0], coords_new[i].split(",")[1]] + irr_ls) 
                
    return call_count_new

def check_call_count(n, call_count):
    '''
    Checks if making n API calls will put the total number of calls since running the script over 1000. If it does, displays a warning and prompts the user to continue or exit the script. If the script is not exited, returns the total number of calls if the n calls are made.
    
    Parameters
    ----------
    n (int): Number of calls to be made.
    call_count (int): The number of API calls made since running the script.
    
    Returns
    -------
    call_count (int): The number of API calls made since running the script plus n calls to be made.
    '''   
    
    if call_count + n > 1000:
        while True:
            prompt = "You will be making {} API calls. Since running this script you have already made {} calls, so you will make a total of {} calls. Are you sure you want to continue?".format(n, call_count, call_count + n)
            if click.confirm(prompt, abort=True):
                call_count += n
                return call_count

    else:
        call_count += n
        return call_count

@click.command()
@click.argument('folder')
@click.argument('period', type=click.INT)
@click.argument('max_rep', type=click.INT)
@click.argument('index', type=click.INT)
@click.argument('call_type')
@click.argument('call_count', type=click.INT)
@click.option('--irr_types', '-i', multiple=True, help="Desired data from call, e.g. GHI ('ghi'), DHI ('dhi'), or DNI ('dni').")
@click.option('-p', '--paid', type=click.INT, default=0, show_default=True, help='If 0, the free trial Solcast account is used. If 1, the premium Solcast account is used.')
@click.option('-h', '--hours', type=click.INT, default=168, show_default=True, help='How many hours into the future to make forecasts for (NOTE: Max is 168).')
def call_from_matlab(folder, index, irr_types, call_type, call_count, paid=0, hours=168):
    '''
    Creates a list of coordinates from a folder of csv files and then finds irradiance values for these coordinates from some starting index.

    \b
    Parameters
    ----------
    folder (string): Name of folder containing csvs whose first and second columns are longitudes and latitudes respectively. The csv files must be sorted alphanumerically. 
    period (int): Period in seconds.
    max_rep (int): Maximum number of function calls.
    index (int): The index of the first site in the list of coordinates to make forecasts for.
    call_type (string): Forecast ('forecasts') or estimated actuals ('estimated_actuals').
    call_count (int): The number of API calls made since running the script.

    \b
    Returns
    -------
    None
    '''

    coords = get_coords(folder, 0)
    call_count = call_to_end(coords, index, irr_types, call_type, call_count, paid = 0, hours = 168)

    click.echo('Done!')

@click.command()
@click.argument('folder')
@click.argument('period', type=click.INT)
@click.argument('max_rep', type=click.INT)
@click.argument('index_fname')
@click.argument('call_type')
@click.argument('call_count', type=click.INT)
@click.option('--irr_types', '-i', multiple=True, help="Desired data from call, e.g. GHI ('ghi'), DHI ('dhi'), or DNI ('dni').")
@click.option('-p', '--paid', type=click.INT, default=0, show_default=True, help='If 0, the free trial Solcast account is used. If 1, the premium Solcast account is used.')
@click.option('-h', '--hours', type=click.INT, default=168, show_default=True, help='How many hours into the future to make forecasts for (NOTE: Max is 168).')
def schedule(folder, period, max_rep, index_fname, irr_types, call_type, call_count, paid=0, hours=168):
    '''
    Creates a list of coordinates from a folder of csv files. Next, irradiance values for these coordinates are periodically found. Irradiance values are found from some starting index to the end of the list, and this starting index is obtained from a specified text file.
    
    \b
    Parameters
    ----------
    folder (string): Name of folder containing csvs whose first and second columns are longitudes and latitudes respectively. The csv files must be sorted alphanumerically. 
    period (int): Period in seconds.
    max_rep (int): Maximum number of function calls.
    index_fname (string): The name of the text file containing the index of the first site in the list of coordinates to make forecasts for. Should be continuously updated in StratApp.
    call_type (string): Forecast ('forecasts') or estimated actuals ('estimated_actuals').
    call_count (int): The number of API calls made since running the script.

    \b
    Returns
    -------
    None
    '''

    coords = get_coords(folder, 1)

    starttime = time.time()
    while max_rep > 0:
        with open(index_fname, 'r') as index_file:
            index =  int(index_file.readline())

        call_count = call_to_end(coords, index, irr_types, call_type, call_count, paid = 0, hours = 168)

        time.sleep(period - ((time.time() - starttime) % period))
        max_rep -= 1

    click.echo('Done!')