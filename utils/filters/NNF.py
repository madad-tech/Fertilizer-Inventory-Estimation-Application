import numpy as np
import datetime

class NNF_class:
    
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'Nearest Neighbor Filter'} : {message}")
    
    def __init__(self, config):
        
        self.print_(f'Initiate the Nearest Neighbor Filter')
        self.step_NNF = float(config['Models']['filter']['step_NNF'])
        self.step =  float(config['Data']['step'])
        self.max_length_index =  int(float(config['Data']['length'])/self.step)

    def run(self, elevation_map_semi_predicted, elevation_map_predicted_old_):
        
        
        self.print_(f'Running the filter')
        (max_length_index,max_width_index) = elevation_map_predicted_old_.shape
        
        
        elevation_map_predicted=[]
        elevation_map_semi_predicted_chosen=[]

        # dicretization
        full_positions=np.zeros(round(self.max_length_index*self.step/self.step_NNF)+1)
        for curve in elevation_map_semi_predicted[::-1]:
            pos=curve[0]
            y_index=pos/self.step
            if y_index>=0 and y_index<max_length_index :
                if not full_positions[round(pos/self.step_NNF)]:
                    full_positions[round(pos/self.step_NNF)]=1
                    elevation_map_semi_predicted_chosen.append(curve)
        elevation_map_semi_predicted_chosen=np.array(elevation_map_semi_predicted_chosen)

        # nearest neighbor
        for i in range(self.max_length_index):
            elevation_map_predicted.append(elevation_map_semi_predicted_chosen
                                            [np.argmin(np.abs(elevation_map_semi_predicted_chosen[:,0]-i*self.step))]
                                            [1])
        return elevation_map_semi_predicted_chosen , np.array(elevation_map_predicted)
