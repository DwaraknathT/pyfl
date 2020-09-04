import errno
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import torch

from core.models.lenet import LeNet, SimpleConvNet
from core.models.resnet import resnet20
from core.models.vgg import vgg11, vgg11_bn

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
  #TODO: Remove this commented part
  #logger.addHandler(get_file_handler(logger_name))
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

  if task_config['optim'] == 'sgd':
    optim = torch.optim.sgd()
  elif task_config['optim'] == 'adam':
    optim = torch.optim.adam()
  else:
    raise NotImplementedError("Optimizer not implemented")

  return model, optim
