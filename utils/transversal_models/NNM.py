import torch
import numpy as np
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import datetime
import os


class RegressionModel(nn.Module):
    def __init__(self,num_inputs=2):
        super(RegressionModel, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(num_inputs, 64),
            nn.ReLU(),
            nn.Linear(64, 256),
            nn.ReLU(),
            nn.Linear(256, 86)
        )
    
    def forward(self, x):
        out = self.fc(x)
        return out


class NNM_class:
    
    def __init__(self, config, observation_name):
        self.print_(f'Initiate the NNM model for {observation_name}')
        num_inputs = len(config['watchdog']['observations'][observation_name].keys())-1
        
        self.observation_name=observation_name
        self.model = RegressionModel(num_inputs)
        
        if 'pretrained_path' in config['Models']['transversal_models'][observation_name].keys() :
            self.model_path = config['Models']['transversal_models'][observation_name]['pretrained_path']
            self.load_model()
        else :
            self.print_(f'err no pretrained_path found for NNM {observation_name}')
    
    def load_model(self):
        self.model.load_state_dict(torch.load(self.model_path))
    
    def run(self, inputs):
        self.print_(f'Predicting for {self.observation_name} from inputs {str(inputs)}')
        inputs = torch.tensor(inputs).float()
        outputs = self.model(inputs)
        return outputs.detach().numpy()
    
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'NNM'} : {message}")
        
    
   
