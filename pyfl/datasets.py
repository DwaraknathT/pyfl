from __future__ import print_function

from random import Random

import torch
import torch.distributed as dist
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

crop_size = {
  'mnist': 28,
  'cifar10': 32,
  'cifar100': 32,
  'imagenet': 64,
}


class Partition(object):

  def __init__(self, data, index):
    self.data = data
    self.index = index

  def __len__(self):
    return len(self.index)

  def __getitem__(self, index):
    data_idx = self.index[index]
    return self.data[data_idx]


class DataPartitioner(object):

  def __init__(self, data, sizes=[0.5, 0.5, 0.5], seed=1234):
    self.data = data
    self.partitions = []
    rng = Random()
    rng.seed(seed)
    data_len = len(data)
    indexes = [x for x in range(0, data_len)]
    rng.shuffle(indexes)

    for frac in sizes:
      part_len = int(frac * data_len)
      self.partitions.append(indexes[0:part_len])
      indexes = indexes[part_len:]

  def use(self, partition):
    return Partition(self.data, self.partitions[partition])


def get_data(args):
  """ Applies general preprocess transformations to Datasets
      ops -
      transforms.Normalize = Normalizes each channel of the image
      args - mean tensor, standard-deviation tensor
      transforms.RandomCrops - crops the image at random location
      transforms.HorizontalFlip - randomly flips the image
  """
  transform_train = transforms.Compose([
    transforms.RandomCrop(crop_size[args.dataset], padding=4),
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
    testset = torchvision.datasets.MNIST(
      root='./data', train=False, download=True, transform=transform_test)
    args.num_classes = 10

  if args.dataset == 'cifar10':
    trainset = torchvision.datasets.CIFAR10(
      root='./data', train=True, download=True, transform=transform_train)
    testset = torchvision.datasets.CIFAR10(
      root='./data', train=False, download=True, transform=transform_test)
    args.num_classes = 10

  elif args.dataset == 'cifar100':
    trainset = torchvision.datasets.CIFAR100(
      root='./data', train=True, download=True, transform=transform_train)
    testset = torchvision.datasets.CIFAR100(
      root='./data', train=False, download=True, transform=transform_test)
    args.num_classes = 100

  if args.dist:
    print('Sharding dataset')
    size = dist.get_world_size() - 1
    args.batch_size = int(args.batch_size / float(size))
    partition_sizes = [1.0 / size for _ in range(size)]
    partition = DataPartitioner(trainset, partition_sizes)
    partition = partition.use(dist.get_rank() - 1)
    trainloader = torch.utils.data.DataLoader(partition,
                                              batch_size=args.batch_size,
                                              shuffle=True)
  else:
    trainloader = torch.utils.data.DataLoader(
      trainset, batch_size=args.batch_size, shuffle=True, num_workers=4)

  testloader = torch.utils.data.DataLoader(
    testset, batch_size=args.batch_size, shuffle=False, num_workers=4)

  return trainloader, testloader


'''
def make_data_partition(args):
  """
  Make partitions of a given dataset based on
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
    if batch_idx % num_batches_per_device == 0 and batch_idx != 0:
      device_id += 1
    device_specific_dataset[device_id].append(data)

  device_specific_dataset = {key: iter(device_specific_dataset[key])
                             for key in device_specific_dataset.keys()}

  return device_specific_dataset
'''
