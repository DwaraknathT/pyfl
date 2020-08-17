from core.utils import get_data, make_data_partition
from core.args import get_args
import numpy as np

args = get_args()
device_datasets = make_data_partition(args)