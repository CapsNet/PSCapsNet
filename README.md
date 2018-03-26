# CapsuleTL
Capsule Transfer Learning

## Requirements
* [Anaconda(Python 3.6 version)](https://www.anaconda.com/download/)
* PyTorch(version >= 0.3.1) 
```
conda install pytorch torchvision -c pytorch
```
* PyTorchNet(version >= 0.0.1)
```
pip install git+https://github.com/pytorch/tnt.git@master
```
* capsule-layer(version >= 0.0.4)
```
pip install git+https://github.com/leftthomas/CapsuleLayer.git@master
```
* tqdm(version >= 4.19.5)
```
conda install tqdm
```

## Usage
```
python -m visdom.server -logging_level WARNING & python main.py --data_type FashionMNIST --num_epochs 300
optional arguments:
--data_type                   dataset type [default value is 'MNIST'](choices:['MNIST', 'FashionMNIST', 'SVHN', 'CIFAR10', 'CIFAR100', 'STL10'])
--net_mode                    network mode [default value is 'Capsule'](choices:['Capsule', 'CNN'])
--num_iterations              routing iterations number [default value is 3](it not work for sum routing)
--batch_size                  train batch size [default value is 100]
--num_epochs                  train epochs number [default value is 100]
```
Visdom now can be accessed by going to `127.0.0.1:8097/env/$data_type` in your browser, 
`$data_type` means the dataset type which you are training.

## Results
The train loss、accuracy, test loss、accuracy, and confusion matrix are showed with visdom,
the best test accuracy is ~ 95.72%.
![result](results/result.png)
