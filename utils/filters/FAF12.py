import numpy as np
import datetime

class FAF12_class:
    
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'Friction Angle 1-axis 2 lines'} : {message}")
    
    def __init__(self, config):
        
        self.print_(f'Initiate the FAF12 filter')
        
        self.friction_angle = float(config['Models']['filter']['friction_angle'])
        self.lines_angle = config['Models']['filter']['lines_angle']
        
        self.step =  float(config['Data']['step'])

    def run(self, elevation_map_semi_predicted_, elevation_map_predicted_old_):
        
        
        self.print_(f'Running the filter')
        (max_length_index,max_width_index) = elevation_map_predicted_old_.shape
        
        elevation_map_predicted_=np.copy(elevation_map_predicted_old_)
        tan_28=np.tan(self.friction_angle/180*np.pi)*self.step
        for ly in [elevation_map_semi_predicted_[-1]]:
            
            y_index=ly[0]/self.step
            if y_index>=0 and y_index<max_length_index :

                for x_index,z_index in enumerate(ly[1]) :
                    for line_angle in self.lines_angle :

                        for y_surface in range(len(elevation_map_predicted_old_)):
                            x_surface = round( np.tan(line_angle*180/np.pi) * (y_surface-y_index) + x_index )
                            if  x_surface >= elevation_map_predicted_.shape[1] or x_surface <0  :
                                continue

                            z_surface = elevation_map_predicted_[y_surface][x_surface]
                            if  z_surface-z_index>tan_28*np.sqrt((y_surface-y_index)**2+(x_surface-x_index)**2) :
                                elevation_map_predicted_[y_surface][x_surface]=tan_28*np.sqrt((y_surface-y_index)**2+(x_surface-x_index)**2)+z_index
                            elif  z_surface-z_index<-tan_28*np.sqrt((y_surface-y_index)**2+(x_surface-x_index)**2) :
                                elevation_map_predicted_[y_surface][x_surface]=-tan_28*np.sqrt((y_surface-y_index)**2+(x_surface-x_index)**2)+z_index

        return elevation_map_semi_predicted_,elevation_map_predicted_