#!/usr/bin/env python
import sys, gym, time
import time
from queue import Queue
def current_milli_time():
    return round(time.time() * 1000)

# Parameters
render_speed = 0.009 #delay in seconds. lower will make game faster. mostly prefer 0.008 to be playable

q = Queue(maxsize = 3)

env = gym.make('LunarLander-v2')

flags= [False, False, False, False]

if not hasattr(env.action_space, 'n'):
    raise Exception('Keyboard agent only supports discrete action spaces')
ACTIONS = env.action_space.n
SKIP_CONTROL = 0    # Use previous control decision SKIP_CONTROL times, that's how you
                    # can test what skip is still usable.

human_agent_action = 0
human_wants_restart = True
human_sets_pause = False

def mapWasd(key):
    print(key)

    ## w->71 d->52 a->49
    ## center engine->2 left engine->1, right engine->3

    if(key == 71):
        return 2
    if(key == 52):
        return 3
    if(key==49):
        return 1
    return 0


def key_press(key, mod):
    global human_agent_action, human_wants_restart, human_sets_pause
    if key==0xff0d: human_wants_restart = True
    if key==32: human_sets_pause = not human_sets_pause
    a = mapWasd(int( key - ord('0') ))
    if a <= 0 or a >= ACTIONS: return
    if(q.full()):
        #key_release(key, mod)
        q.get()
    q.put(a)
    human_agent_action = q.get()
    flags[a]=True

def key_release(key, mod):
    global human_agent_action
    a = mapWasd(int( key - ord('0') ))
    if a <= 0 or a >= ACTIONS: return
    if human_agent_action == a:
        human_agent_action = 0
    flags[a]=False

env.render()
env.unwrapped.viewer.window.on_key_press = key_press
env.unwrapped.viewer.window.on_key_release = key_release

def rollout(env, startTime):
    global human_agent_action, human_wants_restart, human_sets_pause
    human_wants_restart = False
    obser = env.reset()
    skip = 0
    total_reward = 0
    total_timesteps = 0
    while 1:
        if not skip:
            print("taking action {}".format(human_agent_action))
            a = human_agent_action
            total_timesteps += 1
            skip = SKIP_CONTROL
        else:
            skip -= 1

        actionCount = 1
        noAction = True
        for i in range(4):
            if(flags[i]):
                noAction = False
                obser, r, done, info = env.step(i)
                actionCount+=1
                env.render()
                #env.render()

        if(noAction):
            obser, r, done, info = env.step(0)
            env.render()

        if r != 0:
            print("reward %0.3f" % r)
        total_reward += r

    
        
        #if window_still_open==False: return False
        #if done: break
        if human_wants_restart: break
        while human_sets_pause:
            env.render()
            time.sleep(0.01)
        print(actionCount)
        
        time.sleep(render_speed)# + render_speed*(actionCount-1)*2)
    print("timesteps %i reward %0.2f" % (total_timesteps, total_reward))

print("ACTIONS={}".format(ACTIONS))
print("Press keys 1 2 3 ... to take actions 1 2 3 ...")
print("No keys pressed is taking action 0")

while 1:
    window_still_open = rollout(env, current_milli_time())
    if window_still_open==False: break

{"mode":"full","isActive":false}