import argparse

parser = argparse.ArgumentParser(description='Ensemble Training')
# Base Parameters
parser.add_argument(
  '--model', default='lenet', type=str, help='Model to use')
parser.add_argument(
  '--dataset', default='mnist', type=str, help='Dataset to use')
parser.add_argument(
  '--num_classes', default=10, type=int, help='Number of classes')
parser.add_argument(
  '--batch_size', default=32, type=int, help='Batch size')

# FL Parameteres
parser.add_argument(
  '--iid_partion', default=False, type=bool, help='Do a non-iid partition of the dataset')
parser.add_argument(
  '--num_devices', default=5, type=int, help='Number of devices')


def get_args():
  args = parser.parse_args()

  return args
