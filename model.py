from utils.transversal_models.NNM import *
from utils.transversal_models.DMM import *
from utils.filters.NNF import *
from utils.filters.FAF1 import *
from utils.filters.FAF12 import *
from utils.filters.DFF import *
from utils.MassCalculator import *
import numpy as np
import datetime
import os
import csv
import plotly.io as pio
import plotly.graph_objs as go

mapper = dict(NNM = NNM_class,DMM = DMM_class,NNF = NNF_class,FAF1 = FAF1_class,FAF12 = FAF12_class,DFF = DFF_class)

class model_class:
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'Run model'} : {message}")
    
    def __init__(self, config):
        
        self.i=0
        self.print_('Initiate the model')
        
        self.buffer_size = config['Models']['buffer_size']
        
        self.elevation_map_predicted_path=config['Data']['elevation_map_predicted_path']
        self.elevation_map_semi_predicted_path=config['Data']['elevation_map_semi_predicted_path']
        self.volume_mass_path=config['MassCalculator']['volume_mass_path']
        
        self.step=config['Data']['step']
        
        self.config=config
        
        # Choose the model
        self.transversal_model=dict()
        for observation_name, details in config['Models']['transversal_models'].items() :
            self.transversal_model[observation_name] = mapper[details['type']](config,observation_name)
         
        # Choose the filter
        
        self.filter = mapper[config['Models']['filter']['type']](config)
        
        
        self.print_('Loading densities')
        
        with open(config['MassCalculator']['densities_path'], 'r') as file:
            csv_reader = csv.reader(file)
            densities = next(csv_reader)
            densities = np.array([float(d) for d in densities])
        
        
        # Mass calculator
        self.MassCalculator = MassCalculator(config,densities)
        
        self.print_('Loading MAPS')
        
        if os.path.exists(self.elevation_map_predicted_path):
            self.elevation_map_predicted = np.load(self.elevation_map_predicted_path, allow_pickle=True)
        else:
            self.print_(f'The file {self.elevation_map_predicted_path} doesnt exist, generating new map')
            base_line = np.load(config['MassCalculator']['base_line_path'])
            # Repeat the base_line array to create elevation_map_predicted
            self.elevation_map_predicted = np.tile(base_line, (int(config['Data']['length']/self.step), 1))
            np.save(self.elevation_map_predicted_path,  self.elevation_map_predicted)

        
        if os.path.exists(self.elevation_map_semi_predicted_path):
            self.elevation_map_semi_predicted = np.load(self.elevation_map_semi_predicted_path, allow_pickle=True)
        else:
            self.print_(f'The file {self.elevation_map_semi_predicted_path} doesnt exist')
            self.elevation_map_semi_predicted = None
            
        
 
    def compute(self, name, observation):
        
        
        self.print_(f'Compute the model for {name}')
        
        sensor_data_values=[]
        
        # ground level sensor values
        for sensor_name, sensor_details in observation.items():
            if sensor_name != 'encoder' :
                sensor_data_values.append(float(sensor_details['z_cord'])-float(sensor_details['value']))
         
        sensor_data = (float(observation['encoder']['value'])-float(observation['encoder']['y_cord_sensor']),sensor_data_values)

        
        # Run the transversal model
        if self.elevation_map_semi_predicted is None:
            self.elevation_map_semi_predicted = np.array([[sensor_data[0], self.transversal_model[name].run(sensor_data[1])]])
        else:
            self.elevation_map_semi_predicted = np.append(self.elevation_map_semi_predicted,
                                                          [[sensor_data[0], self.transversal_model[name].run(sensor_data[1])]], axis=0)
            
        self.print_('Buffering FIFO')
        # Buffering
        a=len(self.elevation_map_semi_predicted) 
        if len(self.elevation_map_semi_predicted) > self.buffer_size:
            self.elevation_map_semi_predicted = self.elevation_map_semi_predicted[a-self.buffer_size:]
        self.print_(f'Buffering to {a}')
        
        # Run the filter
        self.print_('Compute the filter')
        (self.elevation_map_semi_predicted , self.elevation_map_predicted) = self.filter.run(self.elevation_map_semi_predicted, self.elevation_map_predicted)
        
        
        #redefine ground
        base_line = np.load(self.config['MassCalculator']['base_line_path'])
        # Repeat the base_line array to create elevation_map_predicted
        self.elevation_map_predicted = np.maximum(np.tile(base_line, (int(self.config['Data']['length']/self.step), 1)), self.elevation_map_predicted)
        
        
        # Compute volumes
        self.print_('Compute volumes')
        volume_archs = self.MassCalculator.calculate_volume_arch(self.elevation_map_predicted)
        volume_archs = np.array(volume_archs)
        
        
        # Compute mass
        self.print_('Compute mass')
        mass=self.compute_mass(volume_archs)
        
        
        self.print_('Save MAPS')
        np.save(self.elevation_map_predicted_path,  self.elevation_map_predicted)
        np.save(self.elevation_map_semi_predicted_path,self.elevation_map_semi_predicted)
        
        #np.save(f'../real_test/DDF/all_maps/{self.i}.npy',  self.elevation_map_predicted)
        self.i+=1
        
    def update_history(self,volume):
        mass=self.MassCalculator.calculate_mass(volume)
        
        np.save(self.volume_mass_path,np.array([volume,mass]))
        
    def compute_mass(self,volume):
        mass=self.MassCalculator.calculate_mass(volume)
        
        np.save(self.volume_mass_path,np.array([volume,mass]))
        
    def set_densities(self,densities):
        self.MassCalculator.set_densities(densities)
        
        
        
        
        
        
        