# Alpha Zero General (any game, any framework!)
A simplified, highly flexible, commented and (hopefully) easy to understand implementation of self-play based reinforcement learning based on the AlphaGo Zero paper (Silver et al). It is designed to be easy to adopt for any two-player turn-based adversarial game and any deep learning framework of your choice. A sample implementation has been provided for the game of Othello in PyTorch and Keras. An accompanying tutorial can be found [here](https://suragnair.github.io/posts/alphazero.html). We also have implementations for many other games like GoBang and TicTacToe.

To use a game of your choice, subclass the classes in ```Game.py``` and ```NeuralNet.py``` and implement their functions. Example implementations for Othello can be found in ```othello/OthelloGame.py``` and ```othello/{pytorch,keras}/NNet.py```. 

```Coach.py``` contains the core training loop and ```MCTS.py``` performs the Monte Carlo Tree Search. The parameters for the self-play can be specified in ```main.py```. Additional neural network parameters are in ```othello/{pytorch,keras}/NNet.py``` (cuda flag, batch size, epochs, learning rate etc.). 

To start training a model for Othello:
```bash
python main.py
```
Choose your framework and game in ```main.py```.

### Docker Installation
For easy environment setup, we can use [nvidia-docker](https://github.com/NVIDIA/nvidia-docker). Once you have nvidia-docker set up, we can then simply run:
```
./setup_env.sh
```
to set up a (default: pyTorch) Jupyter docker container. We can now open a new terminal and enter:
```
docker exec -ti pytorch_notebook python main.py
```

### Experiments
We trained a PyTorch model for 6x6 Othello (~80 iterations, 100 episodes per iteration and 25 MCTS simulations per turn). This took about 3 days on an NVIDIA Tesla K80. The pretrained model (PyTorch) can be found in ```pretrained_models/othello/pytorch/```. You can play a game against it using ```pit.py```. Below is the performance of the model against a random and a greedy baseline with the number of iterations.
![alt tag](https://github.com/suragnair/alpha-zero-general/raw/master/pretrained_models/6x6.png)

A concise description of our algorithm can be found [here](https://github.com/suragnair/alpha-zero-general/raw/master/pretrained_models/writeup.pdf).

### Citation

If you found this work useful, feel free to cite it as

```
@misc{thakoor2016learning,
  title={Learning to play othello without human knowledge},
  author={Thakoor, Shantanu and Nair, Surag and Jhunjhunwala, Megha},
  year={2016},
  publisher={Stanford University, Final Project Report}
}
```

### Contributing
While the current code is fairly functional, we could benefit from the following contributions:
* Game logic files for more games that follow the specifications in ```Game.py```, along with their neural networks
* Neural networks in other frameworks
* Pre-trained models for different game configurations
* An asynchronous version of the code- parallel processes for self-play, neural net training and model comparison. 
* Asynchronous MCTS as described in the paper

Some extensions have been implented [here](https://github.com/kevaday/alphazero-general).

### Contributors and Credits
* [Shantanu Thakoor](https://github.com/ShantanuThakoor) and [Megha Jhunjhunwala](https://github.com/jjw-megha) helped with core design and implementation.
* [Shantanu Kumar](https://github.com/SourKream) contributed TensorFlow and Keras models for Othello.
* [Evgeny Tyurin](https://github.com/evg-tyurin) contributed rules and a trained model for TicTacToe.
* [MBoss](https://github.com/1424667164) contributed rules and a model for GoBang.
* [Jernej Habjan](https://github.com/JernejHabjan) contributed RTS game.
* [Adam Lawson](https://github.com/goshawk22) contributed rules and a trained model for 3D TicTacToe.
* [Carlos Aguayo](https://github.com/carlos-aguayo) contributed rules and a trained model for Dots and Boxes along with a [JavaScript implementation](https://github.com/carlos-aguayo/carlos-aguayo.github.io/tree/master/alphazero).
* [Robert Ronan](https://github.com/rlronan) contributed rules for Santorini.
* [Plamen Totev](https://github.com/plamentotev) contributed Go Text Protocol player for Othello.

Note: Chainer and TensorFlow v1 versions have been removed but can be found prior to commit [2ad461c](https://github.com/suragnair/alpha-zero-general/tree/2ad461c393ecf446e76f6694b613e394b8eb652f).

### 学习随笔
[tutorial](https://suragnair.github.io/posts/alphazero.html)
- 神经网络与损失函数设计
神经网络被训练以最小化以下损失函数
$$
l = \sum_{t} (v_{\theta}(s_t) - z_t)^2 - \vec{\pi}_t \cdot \log(\vec{p}_{\theta}(s_t))
$$
$v_{\theta}$ 和 $\vec{p}_{\theta}$ 都是关于$\theta$的神经网络

- 探索与利用（exploration and exploitation）
$$
U(s,a)=Q(s,a)+c_{puct}\cdot P(s,a)\cdot\frac{\sqrt{\sum_{b}N(s,b)}}{1 + N(s,a)}
$$
  - Q[s][a]（s状态下采取a行动的Q值） 是通过 Q[s][a] = (N[s][a]*Q[s][a] + v)/(N[s][a]+1) 每次更新得到
  - P[s][a] 通过模型预测得到 P[s], v = nnet.predict(s)
  - N[s][a] 则是统计值
  - $\sum_{b}N(s,b)$ = sum(N[s])
- 开发环境
  - 基础镜像：pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime
  - pip install coloredlogs==15.0.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
- 通过getSymmetries函数得到更多的训练数据
- 模型训练的输入是什么
  ```python
  boards = torch.FloatTensor(np.array(boards).astype(np.float64))
  ```

## TODO
- 棋盘board加入当前行动玩家 当前进行轮次数 上一次吃子轮次数
- action应该改成 x1 y1 x2 y2，这样不论是board还是canonicalBoard，同一个action的意义是一样的



