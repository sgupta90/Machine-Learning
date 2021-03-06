import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt

transform = transforms.Compose([transforms.ToTensor()]) # converting image to tensor between [0,1]
trainset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
testset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

'''
Network for Denoising AutoEncoder
'''
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(1 * 28 * 28, 400)
        self.fc2 = nn.Linear(400, 20)
        self.fc3 = nn.Linear(20, 400)
        self.fc4 = nn.Linear(400, 1 * 28 * 28)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.sigmoid(self.fc4(x))
        return x

# instantiating the model
net = Net()
print(net)
batch = 64 #batch size
trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch, shuffle=True)
testloader = torch.utils.data.DataLoader(testset, batch_size=batch, shuffle=False)

criterion = nn.BCELoss() # setting the loss function
optimizer = optim.Adam(net.parameters(), lr=0.009)

'''
Function to get data with noise
'''
def get_noisy(x, mean, stddev):
    noise = torch.FloatTensor(x.data.new(x.size()).normal_(mean, stddev))
    inputs_noisy = torch.clamp(x + noise, 0, 1)
    return inputs_noisy

n = trainset.data.shape[0] #number of samples in test data
num_batch = trainset.data.shape[0]/batch
epochs = 10
train_loss_list = []

for epoch in range(epochs):
  training_loss = 0.0
  for i, data in enumerate(trainloader, 0):
      # get the inputs; data is a list of [inputs, labels]
      inputs, labels = data

      # zero the parameter gradients
      optimizer.zero_grad()

      #Noisy input 
      inputs_noisy = get_noisy(inputs, 0, 0.5) #get noisy data

      # forward + backward + optimize
      outputs = net(inputs_noisy)
      loss = criterion(outputs, inputs.view(-1, 28 * 28))
      loss.backward()
      optimizer.step()

      training_loss += loss.item() * inputs.shape[0]
      #training_loss += loss.item()

      #print(f'data = {len(data)}, average epoch loss = {loss.item()} inputs:{inputs.shape[0]}')

  train_avg_loss = training_loss/n
  #train_avg_loss = training_loss/num_batch
  print(f'epoch={epoch}, train_avg_loss= {train_avg_loss}')
  train_loss_list.append(train_avg_loss)

print('Finished Training')
PATH = './hw5_dAE.pth'
torch.save(net.state_dict(), PATH)

x = list(range(1, epochs+1))
plt.figure()
plt.ylabel('loss')
plt.xlabel('epoch')
plt.plot(x, train_loss_list, label='training loss')
plt.legend()

# Testing Accuracy
net1 = Net()
net1.load_state_dict(torch.load(PATH))
itr = iter(testloader)
inputs,_ = itr.next()
test_x = get_noisy(inputs,0,0.4)
outputs = net1(test_x)
output = outputs.view(64, 1, 28, 28)
output = output.detach().numpy()
fig, axes = plt.subplots(nrows=2, ncols=5, sharex=True, sharey=True, figsize=(25,5))

# input images on top row, reconstructions on bottom
for noisy_imgs, row in zip([test_x, output], axes):
    for img, ax in zip(noisy_imgs, row):
        ax.imshow(np.squeeze(img), cmap='gray')
