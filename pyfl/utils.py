import errno
import inspect
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import torch

from pyfl.models.lenet import LeNet, SimpleConvNet
from pyfl.models.resnet import resnet20
from pyfl.models.vgg import vgg11, vgg11_bn

from pyfl.communication.message_definitions import ServerDeviceMessage, DeviceServerMessage

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s",
                              datefmt='%m/%d/%Y %I:%M:%S %p')


def get_console_handler():
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(FORMATTER)
  return console_handler


def get_file_handler(logfile_name):
  try:
    file_handler = RotatingFileHandler('logs/{}.log'.format(logfile_name, mode='w'))
  except:
    raise OSError('Logs directory not created')
  file_handler.setFormatter(FORMATTER)
  return file_handler


def get_logger(logger_name):
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
  logger.addHandler(get_console_handler())
  # TODO: Remove this commented part
  # logger.addHandler(get_file_handler(logger_name))
  # with this pattern, it's rarely necessary to propagate the error up to parent
  logger.propagate = False
  return logger


def setup_dirs():
  try:
    os.makedirs('logs')
    os.makedirs('runs')
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise


def get_model(task_config):
  if task_config['model'] == 'simplenet':
    model = SimpleConvNet()
  elif task_config['model'] == 'lenet':
    model = LeNet()
  elif task_config['model'] == 'vgg11':
    model = vgg11()
  elif task_config['model'] == 'vgg11_bn':
    model = vgg11_bn()
  elif task_config['model'] == 'resnet20':
    model = resnet20(task_config['num_clases'])
  else:
    raise NotImplementedError("Model not supported")

  if task_config['optimizer'] == 'sgd':
    optim = torch.optim.sgd()
  elif task_config['optimizer'] == 'adam':
    optim = torch.optim.adam()
  else:
    raise NotImplementedError("Optimizer not implemented")

  return model, optim


# Excludes 'internal' names (start with '__').
def Public(name):
  return not name.startswith('__')


def Attributes(ob):
  # Exclude methods.
  attributes = inspect.getmembers(ob, lambda member: not inspect.ismethod(member))
  # Exclude 'internal' names.
  publicAttributes = filter(lambda desc: Public(desc[0]), attributes)
  attribute_list = [type(x[1]) for x in publicAttributes]
  return tuple(attribute_list)

def message_class_type(message_object, message_class):
  return_var = False
  if message_class == 'server':
    if isinstance(message_object.message_class,Attributes(ServerDeviceMessage)):
      return_var = True
  if message_class == 'device':
    if isinstance(message_object.message_class, Attributes(DeviceServerMessage)):
      return_var = True
  return return_var

