import numpy as np
import datetime

class MassCalculator:
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'MassCalculator'} : {message}")
        
    def __init__(self, config,densities):  
        self.base_line = np.load(config['MassCalculator']['base_line_path'])
        self.step = float(config['Data']['step'])
        self.length = float(config['Data']['length'])
        self.arch_length=int(self.length/self.step/10)
        self.densities = densities

    def set_densities(self,densities):
        self.densities = densities
    
    def calculate_volume(self, elevation_map_predicted):
        area=0
        for curve in elevation_map_predicted :
            # Calculate the area between the array and the x-axis 
            area += np.trapz(curve,dx=self.step)*self.step - np.trapz(self.base_line,dx=self.step)*self.step
            #dz shold be one but for the test it will be
            #area += (np.trapz(curve,dx=self.step)*self.step - np.trapz(self.base_line,dx=self.step)*self.step)/0.836*3.5**3
            
        return area
    
    def calculate_mass(self, volume):
        self.print_(f'Results are {volume*self.densities}')
        return volume*self.densities

    def calculate_volume_arch(self, elevation_map_predicted):
        arch_mass = []
        for i in range(10):
            arch_mass.append(self.calculate_volume(elevation_map_predicted[i*self.arch_length:(i+1)*self.arch_length]))
        self.print_(f'Results are {arch_mass}')
        return arch_mass
