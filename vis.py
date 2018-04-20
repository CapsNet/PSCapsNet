import argparse

import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from capsule_layer.functional import flaser
from torch.autograd import Variable
from torchvision.utils import save_image

from utils import models, get_iterator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize SP Capsule Network')
    parser.add_argument('--data_type', default='CIFAR10', type=str,
                        choices=['MNIST', 'FashionMNIST', 'SVHN', 'CIFAR10', 'STL10'], help='dataset type')
    parser.add_argument('--model_name', default='CIFAR10_Capsule_95.pth', type=str, help='model epoch name')
    opt = parser.parse_args()

    DATA_TYPE = opt.data_type
    MODEL_NAME = opt.model_name
    model = models[DATA_TYPE]().eval()

    if torch.cuda.is_available():
        model.cuda()
        model.load_state_dict(torch.load('epochs/' + MODEL_NAME))
    else:
        model.load_state_dict(torch.load('epochs/' + MODEL_NAME, map_location='cpu'))

    images, labels = next(iter(get_iterator(DATA_TYPE, 'test_multi', 16, True)))
    save_image(images, filename='vis_%s_original.png' % DATA_TYPE, nrow=4, normalize=True)
    if torch.cuda.is_available():
        images = images.cuda()
    images = Variable(images)
    image_size = (images.size(-1), images.size(-2))

    features = None
    for name, module in model.named_children():
        if name == 'conv1':
            out = module(images)
            save_image(out.mean(dim=1, keepdim=True).data, filename='vis_%s_conv1.png' % DATA_TYPE, nrow=4,
                       normalize=True)
        elif name == 'features':
            out = module(out)
            features = out
        elif name == 'classifier':
            out = out.permute(0, 2, 3, 1)
            out = out.contiguous().view(out.size(0), -1, module.weight.size(-1))
            priors = (module.weight[None, :, None, :, :] @ out[:, None, :, :, None]).squeeze(dim=-1)
            output = priors.sum(dim=-2, keepdim=True) / priors.size(1)
            for r in range(3):
                logits = (priors * F.normalize(output, p=2, dim=-1)).sum(dim=-1, keepdim=True)
                probs = F.softmax(logits, dim=1)
                output = (probs * priors).sum(dim=-2, keepdim=True)
            classes = flaser(output).squeeze(dim=-2).norm(dim=-1)
            prob = (probs.expand(*probs.size()[:-1], module.weight.size(-1)) * classes.unsqueeze(dim=-1).unsqueeze(
                dim=-1)).mean(dim=1)
            prob = prob.contiguous().view(prob.size(0), *features.size()[-2:], -1)
            prob = prob.permute(0, 3, 1, 2)

            heat_maps = []
            for i in range(prob.size(0)):
                img = images[i].data.cpu().numpy()
                img = img - np.min(img)
                if np.max(img) != 0:
                    img = img / np.max(img)
                mask = prob[i].mean(dim=0)
                mask = cv2.resize(mask.data.cpu().numpy(), image_size)
                mask = mask - np.min(mask)
                if np.max(mask) != 0:
                    mask = mask / np.max(mask)
                heat_map = np.float32(cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET))
                cam = heat_map + np.float32((np.uint8(img.transpose((1, 2, 0)) * 255)))
                cam = cam - np.min(cam)
                if np.max(cam) != 0:
                    cam = cam / np.max(cam)
                heat_maps.append(transforms.ToTensor()(cv2.cvtColor(np.uint8(255 * cam), cv2.COLOR_BGR2RGB)))
            heat_maps = torch.stack(heat_maps)
            save_image(heat_maps, filename='vis_%s_features.png' % DATA_TYPE, nrow=4, normalize=True)
