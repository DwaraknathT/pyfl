import errno
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

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
  logger.addHandler(get_file_handler(logger_name))
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
