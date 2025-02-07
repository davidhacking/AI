docker run -it --gpus all --shm-size 8G -v `pwd`:/workspace/alpha_zero -p 8888:8888 -p 8097:8097 --name pytorch_notebook pytorch:0.4.1-py3-gpu /bin/bash
