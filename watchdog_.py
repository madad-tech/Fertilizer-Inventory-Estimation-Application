import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv
import yaml
from model import model_class
import datetime
import numpy as np
import schedule
import os
import pandas as pd

# Specify the path to your YAML file
yaml_file_path = 'config.yaml'

# Open the YAML file and load its contents
with open(yaml_file_path, 'r') as file:
    yaml_content = yaml.safe_load(file)

yaml_watchdog = yaml_content['watchdog']

# Initiate the sensors
observations = yaml_watchdog['observations']

model=model_class(yaml_content)





def print_(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {'watchdog'} : {message}")


def save_history() :
    print_('Save history')
    volume_mass = np.load(yaml_content['MassCalculator']['volume_mass_path'])

    historical_data_path = yaml_watchdog['historical_data_path']
    if os.path.exists(historical_data_path):
        historical_data = np.load(historical_data_path, allow_pickle=True)
    else:
        historical_data = np.array([])  # Initialize empty array if file doesn't exist

    # Append current timestamp and volume_mass to historical_data
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    historical_data = np.append(historical_data, {'timestamp': timestamp, 'volume_mass': volume_mass})

    # Save the updated historical_data
    np.save(historical_data_path, historical_data, allow_pickle=True)
    
def update_densities() :
    
    with open(yaml_content['MassCalculator']['densities_path'], 'r') as file:
        csv_reader = csv.reader(file)
        try:
            densities = next(csv_reader)
            # Process the densities data
            densities = np.array([float(d) for d in densities])
            print_(f'Update mass from densities {densities}')

            volume_mass = np.load(yaml_content['MassCalculator']['volume_mass_path'])[0]

            model.set_densities(densities)

            model.compute_mass(volume_mass)
        except StopIteration:
            # Handle the end of iteration
            print("No more data to read.")
        
    
    
def update() :

    observations_flags=[]
    with open(yaml_watchdog['sensors_file_path'], 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            #check which key is row[0] in order to add it to observation
            for name,sensors in observations.items() :
                for sensor_name,value in sensors.items() :
                    if value['key'] == row[0] and value['value'] != row[1] :
                        observations_flags.append(name)
                        print_(name +'/'+sensor_name+' has been changed from '+str(value['value'])+' to '+str(row[1]))
                        observations[name][sensor_name]['value']=row[1]
    
    # Write the updated observations back to the YAML file
    with open(yaml_file_path, 'w') as file:
        yaml.dump(yaml_content, file)
    
    # check if there is changes and run the model
    for name in set(observations_flags) : 
        print_('Run the model for '+ name)
        model.compute(name, observations[name])
        

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super(FileChangeHandler, self).__init__()
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory :
            self.callback(event.src_path)

            


# Define the callback function to be executed on file change
def on_file_change(k):
    
      
    print_(f"File {k} change event occurred.")
    if k == yaml_watchdog['sensors_file_path'] :
        update()
    elif k == yaml_content['MassCalculator']['densities_path']:
        update_densities()

# Create an event handler and pass the callback function
event_handler = FileChangeHandler(callback=on_file_change)

# Create an observer and set the event handler
observer = Observer()
observer.schedule(event_handler, path=yaml_watchdog['sensors_file_folder'], recursive=False)

# Start the observer
observer.start()

schedule.every(yaml_watchdog['time_interval_history']).seconds.do(save_history)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()


    
