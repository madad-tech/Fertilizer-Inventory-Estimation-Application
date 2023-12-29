import numpy as np
import datetime

class FAF1_class:
    
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'Friction Angle 1-axis'} : {message}")
    
    def __init__(self, config):
        
        self.print_(f'Initiate the FAF1 filter')
        
        self.friction_angle = float(config['Models']['filter']['friction_angle'])
        self.step =  float(config['Data']['step'])

    def run(self, elevation_map_semi_predicted, elevation_map_predicted_old_):
        
        
        self.print_(f'Running the filter')
        (max_length_index,max_width_index) = elevation_map_predicted_old_.shape
        
        elevation_map_predicted_ = np.copy(elevation_map_predicted_old_)
        tan_28 = np.tan(self.friction_angle / 180 * np.pi) * self.step
        
        for ly in [elevation_map_semi_predicted[-1]]:
            y_index = ly[0] / self.step
            if y_index>=0 and y_index<max_length_index :
                for x_index, z_index in enumerate(ly[1]):
                    for y_surface, z_surface in enumerate(elevation_map_predicted_[:, x_index]):
                        if z_surface - z_index > tan_28 * abs(y_surface - y_index):
                            elevation_map_predicted_[y_surface][x_index] = tan_28 * abs(y_surface - y_index) + z_index
                        elif z_surface - z_index < -tan_28 * abs(y_surface - y_index):
                            elevation_map_predicted_[y_surface][x_index] = -tan_28 * abs(y_surface - y_index) + z_index
        return elevation_map_semi_predicted , elevation_map_predicted_
