import os
import sys

rawbasedir = sys.argv[1]
print(",".join([f"{rawbasedir}/{path}" for path in os.listdir(rawbasedir)]))
