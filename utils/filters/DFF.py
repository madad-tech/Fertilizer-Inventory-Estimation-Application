import numpy as np
import datetime
import torch
import torchvision.transforms as T
import matplotlib.pyplot as plt
from PIL import Image

from  utils.filters.model_DFF.networks_tf import Generator
#from deepfillv2.model.networks import Generator


class DFF_class:
    
    def print_(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] {'Deep Fill Filter'} : {message}")
    
    def __init__(self, config):
        
        self.print_(f'Initiate the DFF filter')
        
        
        self.device = torch.device('cpu')

        #sd_path = 'deepfillv2/checkpoints/celebahq/model_exp0/states.pth'
        #sd_path = 'deepfillv2/pretrained/states_tf_places2.pth'
        #sd_path = 'deepfillv2/pretrained/normal_self_trained.pth'
        self.sd_path = 'deepfillv2/pretrained/pretrained_self_trained.pth'
        #sd_path = 'deepfillv2/pretrained/pretrained_bar-mask_self_trained.pth'

        self.step =  float(config['Data']['step'])
        self.sd_path = config['Models']['filter']['sd_path']
        self.step_DFF = 2
        self.generator = Generator(checkpoint=self.sd_path, return_flow=True).to(self.device)
    
        self.sc=1

        
    def run(self,elevation_map_semi_predicted_,elevation_map_predicted_old_):
        
        self.print_(f'Running the filter')
        
        (max_length_index,max_width_index) = elevation_map_predicted_old_.shape
        
        
        # pooling
        elevation_map_semi_predicted_chosen=[]
        full_positions=np.zeros(round(max_length_index*self.step/self.step_DFF)+1)
        for curve in elevation_map_semi_predicted_[::-1]:
            pos=curve[0]
            if not full_positions[round(pos/self.step_DFF)]:
                full_positions[round(pos/self.step_DFF)]=1
                elevation_map_semi_predicted_chosen.append(curve)
        elevation_map_semi_predicted_chosen=np.array(elevation_map_semi_predicted_chosen)
        
        
        mask_array_0 = np.zeros((max_length_index,max_width_index), dtype=np.uint8)
        for ly in elevation_map_semi_predicted_chosen:
            y_index=int(ly[0]/self.step)
            if y_index>=0 and y_index<max_length_index :
                mask_array_0[max(0,y_index-int(max_width_index/3)):min(y_index+int(max_width_index/3),max_length_index)]=1
                elevation_map_predicted_old_[y_index]=ly[1]

        mask_array=mask_array_0.copy()
        for ly in elevation_map_semi_predicted_chosen:  
            y_index=int(ly[0]/self.step)
            if y_index>=0 and y_index<max_length_index :
                mask_array[y_index]=0


        mask_array=mask_array*255

        min_value = -7
        max_value = 14
        normalized_transposed_array = (255*(elevation_map_predicted_old_ - min_value) / (max_value - min_value)).T

        # Create an empty 3-channel RGB array
        rgb_array = np.zeros((max_width_index,max_length_index, 3), dtype=np.uint8)

        # Copy the grayscale values to all three channels
        rgb_array[:, :, 0] = normalized_transposed_array
        rgb_array[:, :, 1] = normalized_transposed_array
        rgb_array[:, :, 2] = normalized_transposed_array

        image_pil=Image.fromarray(rgb_array)
        mask_pil=Image.fromarray(mask_array.T)

        image = T.ToTensor()(image_pil).to(self.device)
        mask = T.ToTensor()(mask_pil).to(self.device)
        
        output = self.generator.infer(image, mask, return_vals=['inpainted', 'stage1', 'stage2', 'flow'])[2]
        image = Image.fromarray(output)
        # Resizing the image
        resized_image = image.resize(elevation_map_predicted_old_.shape)

        image_compl = ((np.mean(resized_image,axis=2)/255)*(max_value - min_value)+min_value).T * mask_array_0 + elevation_map_predicted_old_ * (1.-mask_array_0)

        return elevation_map_semi_predicted_chosen,image_compl
        
