import os
from model import CANNet2s
from utils import save_checkpoint

import torch
from torch import nn
from torch.autograd import Variable
from torchvision import datasets, transforms
import torch.nn.functional as F

import numpy as np
import argparse
import json
import cv2
import dataset
import time

parser = argparse.ArgumentParser(description='PyTorch CANNet2s')

parser.add_argument('train_json', metavar='TRAIN',
                    help='path to train json')
parser.add_argument('val_json', metavar='VAL',
                    help='path to val json')

def main():
    global args,best_prec1

    best_prec1 = 1e6

    args = parser.parse_args()
    args.lr = 1e-4
    args.batch_size    = 1 
    args.momentum      = 0.95
    args.decay         = 5*1e-4
    args.start_epoch   = 0
    args.epochs = 200
    args.workers = 4
    args.seed = int(time.time())
    args.print_freq = 10
    with open(args.train_json, 'r') as outfile:
        train_list = json.load(outfile)
    with open(args.val_json, 'r') as outfile:
        val_list = json.load(outfile)

    torch.cuda.manual_seed(args.seed)

    model = CANNet2s()
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Number of parameters: {total_params}")

    model = model.cuda()

    # saved_state = torch.load('model_best.pth.tar')
    # model.load_state_dict(saved_state['state_dict'],strict = False)


    criterion = nn.MSELoss(reduction='sum').cuda()

    optimizer = torch.optim.Adam(model.parameters(), args.lr,
                                weight_decay=args.decay)

    for epoch in range(args.start_epoch, args.epochs):

        train(train_list, model, criterion, optimizer, epoch)
        prec1 = validate(val_list, model, criterion)

        is_best = prec1 < best_prec1
        best_prec1 = min(prec1, best_prec1)
        print(' * best MAE {mae:.3f} '
              .format(mae=best_prec1))
        save_checkpoint({
            'state_dict': model.state_dict(),
        }, is_best)

def train(train_list, model, criterion, optimizer, epoch):
    torch.cuda.empty_cache()

    losses = AverageMeter()
    batch_time = AverageMeter()
    data_time = AverageMeter()

    train_loader = torch.utils.data.DataLoader(
        dataset.listDataset(train_list,
                       shuffle=True,
                       transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ]),
                       train=True,
                       batch_size=args.batch_size,
                       num_workers=args.workers),
        batch_size=args.batch_size)
    print('epoch %d, processed %d samples, lr %.10f' % (epoch, epoch * len(train_loader.dataset), args.lr))

    model.train()
    end = time.time()

    for i,( img, target ) in enumerate(train_loader):

        data_time.update(time.time() - end)

        img = img.cuda()
        img = Variable(img)

        img1 =  img[:,:,:(int(img.shape[2]/2)),:(int(img.shape[3]/2)) ]
        img2 = img[:,:,:(int(img.shape[2]/2)) :,(int(img.shape[3]/2)): ]
        img3 = img[:,:,(int(img.shape[2]/2)) :,:(int(img.shape[3]/2)) ]
        img4 = img[:,:,(int(img.shape[2]/2)):,(int(img.shape[3]/2)): ]


        predicted1 = model(img1)
        predicted2 = model(img2)
        predicted3 = model(img3)
        predicted4 = model(img4)
        predicted_temp_1 = torch.cat((predicted1,predicted2), dim =3)
        predicted_temp_2 = torch.cat((predicted3,predicted4), dim =3)

        predicted = torch.cat((predicted_temp_1, predicted_temp_2) , dim = 2)

        
        target = target.type(torch.FloatTensor)[0].cuda()
        target = Variable(target)

        # print(target.shape)
        # print(predicted.shape)
        loss = criterion(predicted[0,0,:,:], target)



        losses.update(loss.item(), img.size(0))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        batch_time.update(time.time() - end)
        end = time.time()

        if i % args.print_freq == 0:
            print('Epoch: [{0}][{1}/{2}]\t'
                  'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                  'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                  'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                  .format(
                   epoch, i, len(train_loader), batch_time=batch_time,
                   data_time=data_time, loss=losses))


def validate(val_list, model, criterion):
    print ('begin val')
    val_loader = torch.utils.data.DataLoader(
    dataset.listDataset(val_list,
                   shuffle=False,
                   transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ]),  train=False),
    batch_size=1)

    model.eval()

    mae = 0

    for i,(img, target) in enumerate(val_loader):
        # only use previous frame in inference time, as in real-time application scenario, future frame is not available


        img = img.cuda()
        img = Variable(img)
        
        img1 =  img[:,:,:(int(img.shape[2]/2)),:(int(img.shape[3]/2)) ]
        img2 = img[:,:,:(int(img.shape[2]/2)) :,(int(img.shape[3]/2)): ]
        img3 = img[:,:,(int(img.shape[2]/2)) :,:(int(img.shape[3]/2)) ]
        img4 = img[:,:,(int(img.shape[2]/2)):,(int(img.shape[3]/2)): ]


        predicted1 = model(img1)
        predicted2 = model(img2)
        predicted3 = model(img3)
        predicted4 = model(img4)
        predicted_temp_1 = torch.cat((predicted1,predicted2), dim =3)
        predicted_temp_2 = torch.cat((predicted3,predicted4), dim =3)

        predict = torch.cat((predicted_temp_1, predicted_temp_2) , dim = 2)
        # predict = model(img)

        target = target.type(torch.FloatTensor)[0].cuda()
        target = Variable(target)
        target = target.type(torch.FloatTensor)

        mae += abs(predict.data.sum()-target.sum())

    mae = mae/len(val_loader)
    print(' * MAE {mae:.3f} '
              .format(mae=mae))

    return mae

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

if __name__ == '__main__':
    main()
