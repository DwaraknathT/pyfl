from __future__ import print_function

from collections import defaultdict

import torch
import torchvision
import torchvision.transforms as transforms

mean = {
  'mnist': (0.1307,),
  'cifar10': (0.4914, 0.4822, 0.4465),
  'cifar100': (0.5071, 0.4867, 0.4408),
  'imagenet': (0.485, 0.456, 0.406),
}
std = {
  'mnist': (0.3081,),
  'cifar10': (0.2023, 0.1994, 0.2010),
  'cifar100': (0.2675, 0.2565, 0.2761),
  'imagenet': (0.229, 0.224, 0.225),
}


def get_data(args):
  """ Applies general preprocess transformations to Datasets
      ops -
      transforms.Normalize = Normalizes each channel of the image
      args - mean tensor, standard-deviation tensor
      transforms.RandomCrops - crops the image at random location
      transforms.HorizontalFlip - randomly flips the image
  """
  transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean[args.dataset], std[args.dataset]),
  ])

  transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean[args.dataset], std[args.dataset])
  ])
  if args.dataset == 'mnist':
    trainset = torchvision.datasets.MNIST(
      root='./data', train=True, download=True, transform=transform_train)
    trainloader = torch.utils.data.DataLoader(
      trainset, batch_size=args.batch_size, shuffle=True, num_workers=2)
    testset = torchvision.datasets.MNIST(
      root='./data', train=False, download=True, transform=transform_test)
    testloader = torch.utils.data.DataLoader(
      testset, batch_size=args.batch_size, shuffle=False, num_workers=2)

  if args.dataset == 'cifar10':
    trainset = torchvision.datasets.CIFAR10(
      root='./data', train=True, download=True, transform=transform_train)
    trainloader = torch.utils.data.DataLoader(
      trainset, batch_size=args.batch_size, shuffle=True, num_workers=4)

    testset = torchvision.datasets.CIFAR10(
      root='./data', train=False, download=True, transform=transform_test)
    testloader = torch.utils.data.DataLoader(
      testset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    args.num_classes = 10

  elif args.dataset == 'cifar100':
    trainset = torchvision.datasets.CIFAR100(
      root='./data', train=True, download=True, transform=transform_train)
    trainloader = torch.utils.data.DataLoader(
      trainset, batch_size=args.batch_size, shuffle=True, num_workers=4)

    testset = torchvision.datasets.CIFAR100(
      root='./data', train=False, download=True, transform=transform_test)
    testloader = torch.utils.data.DataLoader(
      testset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    args.num_classes = 100

  return trainloader, testloader


def make_data_partition(args):
  """
  Make non-iid, iid partition of a given dataset based on
  number of workers
  :param args: Argument object
  :return: Dictionary with dataset partitions for each worker
  """
  trainloader, testloader = get_data(args)
  device_specific_dataset = defaultdict(list)
  num_batches = len(trainloader)
  num_batches_per_device = num_batches // args.num_devices
  device_id = 0
  for batch_idx, (data, target) in enumerate(trainloader):
    if batch_idx % num_batches_per_device == 0:
      device_id += 1
    device_specific_dataset[device_id].append(data)

  device_specific_dataset = {key: iter(device_specific_dataset[key])
                             for key in device_specific_dataset.keys()}

  return device_specific_dataset
