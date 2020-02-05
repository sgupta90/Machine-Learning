# -*- coding: utf-8 -*-
"""hw5_adv_examples.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10NqmpFVJB8EjoyDy4HtTQuTz4Ca0ZuD6
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torchvision.models import resnet50
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json
from torch.autograd import Variable

#Remove this mount if not running in colab
from google.colab import drive
drive.mount('/content/drive')

#Change this path to run in local
classfile = '/content/drive/My Drive/imagenet_class_index.json'
#Load the image
my_img = Image.open("/content/drive/My Drive/Elephant2.jpg")

'''
Function to get the name of the class using index
'''
def getname(filename, index):
  with open(filename) as json_file:
    data = json.load(json_file)
    name = data[str(index)][1]
  return name

model = resnet50(pretrained=True) #Loading the model
transform = transforms.Compose([transforms.Resize(224), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

print(f'my_img:{type(my_img)}')
mytensor = transform(my_img).unsqueeze(0) #Creating the tensor from the image 

#Running in eval mode
model.eval()
predvector = model(mytensor) #Getting prediction
class_id = predvector.argmax(1).item() #Getting prediction class index

print(f'mytensor:{mytensor.shape} class_id:{class_id} predvector:{predvector.shape} max:{torch.max(mytensor)} min:{torch.min(mytensor)}')

# Function to rescale the image back to 0-1
def get_image(input_tensor):
  #print(f'Input max:{torch.max(mytensor)} min:{torch.min(mytensor)}')
  np_arr = input_tensor.clone().squeeze().detach().numpy()
  np_arr[0] = np_arr[0] * 0.229  + np.array([0.485])
  np_arr[1] = np_arr[1] * 0.224  + np.array([0.456])
  np_arr[2] = np_arr[2] * 0.225  + np.array([0.406])

  tensor_arr = torch.from_numpy(np_arr)
  #print(f'max:{torch.max(tensor_arr)} min:{torch.min(tensor_arr)}')
  clamped_tensor = torch.clamp(tensor_arr, 0, 1)
  image = clamped_tensor.clone().cpu()
  image = image.view(clamped_tensor.size())
  image = transforms.ToPILImage()(image)
  plt.imshow(image)
  return image

image = get_image(mytensor)
print(type(image))

class_name = getname(classfile, class_id)
print(f'class_name:{class_name} class_id:{class_id}')

############## PART A #################
epsilon = 0.01
test_input = mytensor.clone()

#setting target 101
target = torch.tensor([class_id], dtype= torch.long)

# Loss function
criterion = nn.CrossEntropyLoss()
print(f'Before test_input:{test_input.shape} max:{torch.max(test_input)} min:{torch.min(test_input)}')
for i in range(10):
  test_input.requires_grad = True
  # Forward pass the data through the model
  output = model(test_input)
  init_pred = output.argmax(1).item()

  # Calculate the loss
  loss = criterion(output, target)

  # Zero all existing gradients
  model.zero_grad()

  #print(hasattr(test_input.grad, "data"))
  # Calculate gradients of model in backward pass
  loss.backward()

  #print(hasattr(test_input.grad, "data"))
  
  # Collect datagrad
  data_grad = test_input.grad.data

  test_input.requires_grad = False
  test_input += epsilon*data_grad.sign() #Adding noise to perturb the image based on the loss

  # Re-classify the perturbed image
  new_output = model(test_input)
  new_pred = new_output.argmax(1).item()
  
  print(f'After new_pred:{new_pred} test_input:{test_input.shape} max:{torch.max(test_input)} min:{torch.min(test_input)}')
  if ( new_pred != 101 ):
    break

image = get_image(test_input)
print(f'######## New Class: {getname(classfile, new_pred)} ##############')

############## PART B #################
epsilon = 0.01
test_input = mytensor.clone()

#setting target 101
bullet_train_id = 466
target = torch.tensor([class_id], dtype= torch.long)
target2 = torch.tensor([bullet_train_id], dtype= torch.long) #target for bullet train

# Loss function
criterion = nn.CrossEntropyLoss()
print(f'Before test_input:{test_input.shape} max:{torch.max(test_input)} min:{torch.min(test_input)}')
for i in range(20):
  test_input.requires_grad = True
  # Forward pass the data through the model
  output = model(test_input)
  init_pred = output.argmax(1).item()

  # Calculate the loss
  loss = criterion(output, target) - criterion(output, target2)

  # Zero all existing gradients
  model.zero_grad()

  #print(hasattr(test_input.grad, "data"))
  # Calculate gradients of model in backward pass
  loss.backward()

  #print(hasattr(test_input.grad, "data"))
  
  # Collect datagrad
  data_grad = test_input.grad.data

  test_input.requires_grad = False
  test_input += epsilon*data_grad.sign()

  # Re-classify the perturbed image
  new_output = model(test_input)
  new_pred = new_output.argmax(1).item()
  
  print(f'After new_pred:{new_pred} test_input:{test_input.shape} max:{torch.max(test_input)} min:{torch.min(test_input)}')
  if ( new_pred == bullet_train_id ):
    break

image = get_image(test_input)
print(f'######## New Class: {getname(classfile, new_pred)} ##############')