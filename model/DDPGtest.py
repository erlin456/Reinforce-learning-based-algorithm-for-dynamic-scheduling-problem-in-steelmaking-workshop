#-*- coding:utf-8 -*-

"""
deep deterministic policy gradient test
"""

import os
import gym

from DDPG import *

env_name = 'Pendulum-v0' # 游戏名
env = gym.make(env_name).unwrapped # 创建gym游戏

# use the cuda or not
device = 'cuda' if torch.cuda.is_available() else 'cpu'
if device == 'cuda':
    print('using the GPU...')
else:
    print('using the CPU...')

# 强化学习参数
state_dim = env.observation_space.shape[0] # 状态个数
action_dim = env.action_space.shape[0] # 动作个数
max_action = float(env.action_space.high[0]) # 动作最大值

# 其它参数
num_episodes = 1     # 训练时走几次
num_steps = 2     # 训练时一次走几步
test_iteration = 10     # 测试时走几次
num_test_steps = 200    # 测试时一次走几步
mode = 'train'      # train or test

retrain = True        # 是否重头训练
weight_num = 900        # 载入权重的代数,用于中途继续训练和test情况
log_interval = 100       # 每隔log_interval保存一次参数
print_log = 5       # 每走print_log次输出一次
exploration_noise = 0.1 # 加入随机量
capacity = 5000 # 储存量


# create the directory to save the weight and the result
directory = './exp_ddpg_' + env_name +'./'
if not os.path.exists(directory):    
    os.mkdir(directory)

# 创建agent
agent = DDPG(state_dim, action_dim, max_action,capacity,device)

# train
if mode == 'train':
    # 是否中途开始训练
    if retrain == False:
        agent.load(directory, weight_num)
        
    for i_episode in range(num_episodes):
        # 环境回归原位
        state = env.reset()
        rewards = []
        
        # 每次走num_steps步
        for t in range(num_steps):
            # 选action
            action = agent.select_action(state)
            
            # add noise to action
            action = (action + np.random.normal(0, exploration_noise, size=env.action_space.shape[0])).clip(
                env.action_space.low, env.action_space.high)
            
            # 环境反馈
            next_state, reward, done, info = env.step(action)
            rewards.append(reward)
            agent.replay_buffer.push((state, next_state, action, reward, np.float(done)))
            '''
            for each in agent.replay_buffer.storage:
                print(each)
            '''
            # 更新state
            state = next_state
            if done:
                break
                
        # 参数更新是运行完一次更新一次, 不是每走一步更新一次
        if len(agent.replay_buffer.storage) >= capacity-1:
            agent.update()
            
        # 保存权重并输出
        if i_episode % log_interval == 0 and i_episode != 0:
            agent.save(directory, i_episode)
            
        # 每隔几次输出一次信息
        if i_episode % print_log == 0 and i_episode != 0:
            # 输出回报
            print("Episode: {}, reward: {}".format(i_episode, np.sum(rewards)))
    env.close()
# test
elif mode == 'test':
    agent.load(directory, weight_num)
    print("load weight...")
    
    for i_episode in range(test_iteration):
        state = env.reset()
        for t in range(num_test_steps):
            action = agent.select_action(state)
            
            next_state, reward, done, _ = env.step(np.float32(action))
            env.render()
            state = next_state
            if done:
                break
    env.close()
else:
    raise NameError("mode wrong!!!")

