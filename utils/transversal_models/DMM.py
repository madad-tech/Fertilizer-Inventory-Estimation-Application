import numpy as np
import datetime

class DMM_class:
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'Data Matching Model'} : {message}")
    
    
    def __init__(self, config, observation_name):
        self.print_(f'Initiate the DMM model for {observation_name}')
        
        self.step=config['Data']['step']
        
        self.sensor_pos_index=[]
        for key,value in config['watchdog']['observations'][observation_name].items() :
            if key != 'encoder' :
                self.sensor_pos_index.append(int(value['x_cord']/self.step))
                
        self.matching_interval = config['Models']['transversal_models'][observation_name]['matching_interval']
        self.observation_name=observation_name
        
        if 'history_map_path' in config['Models']['transversal_models'][observation_name].keys() :
            history_map_path = config['Models']['transversal_models'][observation_name]['history_map_path']
            self.history_map = np.load(history_map_path)
        else :
            self.print_(f'err no history_map_path found for DMM {observation_name}')
        
    
    def run(self, inputs):
        self.print_(f'Predicting for {self.observation_name} from inputs {str(inputs)}')
        assert len(inputs) == len(self.sensor_pos_index)
    
        matching_interval_var=self.matching_interval
        
        while True :
            filtered_curves=self.history_map
            for index in range(len(self.sensor_pos_index)):
                filtered_curves = filtered_curves[
                    (filtered_curves[:, self.sensor_pos_index[index]] >= inputs[index] - matching_interval_var) &
                    (filtered_curves[:, self.sensor_pos_index[index]] <= inputs[index] + matching_interval_var)
                ]

            if len(filtered_curves)==0 :
                matching_interval_var+=0.1
            else :
                break

        estimated_curve=np.mean(filtered_curves,axis=0)
        
        return estimated_curve
    
    