# from core.utils import get_data, make_data_partition
# from core.args import get_args
# import numpy as np

import os

import torch
import torch.distributed as dist
# args = get_args()
# device_datasets = make_data_partition(args)
import torch.multiprocessing as mp
from torch.multiprocessing import Process


class Server:

  def run(self):
    print("Server is runnning \n")
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

    coor_obj = Coordinator()
    coor_obj.run()


class Device:
  def run(self):
    print("Device is running \n")
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


class Coordinator:
  def run(self, i=1):
    print("Coordinator is runnning \n")
    dataset_size = 100
    print("The number of batches per device {}".format(dataset_size // i))


def spawn_server():
  serv = Server()
  serv.run()


def spawn_device():
  dev = Device()
  dev.run()


def run(rank, size):
  tensor = torch.zeros(1)
  if rank == 0:
    tensor += 1
    # Send the tensor to process 1
    req = dist.irecv(tensor=tensor, dst=1)
    print('Rank 0 started sending')
  else:
    # Receive tensor from process 0
    req = dist.irecv(tensor=tensor, src=0)
    print('Rank 1 started receiving')
  req.wait()
  print('Rank ', rank, ' has data ', tensor[0])


def init_process(rank, size, fn, backend='gloo'):
  """ Initialize the distributed environment. """
  os.environ['MASTER_ADDR'] = '127.0.0.1'
  os.environ['MASTER_PORT'] = '29500'
  dist.init_process_group(backend, rank=rank, world_size=size)
  fn()


if __name__ == "__main__":
  mp.set_start_method('spawn')
  # server_conn, dev_conn = Pipe()
  '''
  server_process = Process(target=spawn_server)
  dev_process = [Process(target=spawn_device) for _ in range(4)]
  server_process.start()
  for p in dev_process:
      p.start()
  for p in dev_process:
      p.join()
  server_process.join()
  '''
  processes = []
  for i in range(5):
    if i == 0:
      p = Process(target=init_process, args=(i, 5, spawn_server))
    else:
      p = Process(target=init_process, args=(i, 5, spawn_device))
    p.start()
    processes.append(p)
  for p in processes:
    p.join()
