# from core.utils import get_data, make_data_partition
# from core.args import get_args
# import numpy as np

import os
from mpi4py import MPI
import torch
import torch.distributed as dist
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.communication.message import Message
import torch.multiprocessing as mp
from torch.multiprocessing import Process, Pipe

device2server= DeviceServerMessage()
server2device =ServerDeviceMessage()
class Server:

  def run(self,comms):
    print("Server is runnning \n")
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    device_messages=[]
    for con in comms:
      dev_msg= con.recv()
      device_messages.append(dev_msg[0])
      print(dev_msg[0].sender_id)
    
    #coor_obj = Coordinator()
    #oor_obj.run()


class Device:
  def run(self,comms):
    my_msg= Message({'sender_id': os.getpid(), 
                      'receiver_id': 0,
                      'message_class': device2server.D2S_NOTIF_CLASS,
                      'message_type': device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
                      'message': None})

    print("Device is running \n")
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    comms.send([my_msg])
    

class Coordinator:
  def run(self, i=1):
    print("Coordinator is runnning \n")
    dataset_size = 100
    print("The number of batches per device {}".format(dataset_size // i))


def spawn_server(comms):
  serv = Server()
  serv.run(comms)


def spawn_device(comms):
  dev = Device()
  dev.run(comms)


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


def init_process(rank, size, fn, comms, backend='gloo'):
  """ Initialize the distributed environment. """
  os.environ['MASTER_ADDR'] = '127.0.0.1'
  os.environ['MASTER_PORT'] = '29500'
  dist.init_process_group(backend, rank=rank, world_size=size)
  fn(comms)


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
  server_comm=[]
  device_comm=[]
  for i in range(4):
    server_con,device_con=Pipe()
    server_comm.append(server_con)
    device_comm.append(device_con)
  for i in range(5):
    if i == 0:
      p = Process(target=init_process, args=(i, 5, spawn_server, server_comm))
    else:
      p = Process(target=init_process, args=(i, 5, spawn_device, device_comm[i-1]))
    p.start()
    processes.append(p)
  
  for p in processes:
    p.join()

