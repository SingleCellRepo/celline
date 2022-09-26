import sys

from celline.ncbi.genome import Genome
from celline.utils.config import Config

Config.initialize(sys.argv[1], None)
Genome.add(
    species=sys.argv[2],
    path=sys.argv[3]
)
