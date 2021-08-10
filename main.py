#!/usr/bin/env python

import os.path
import numpy as np
from PIL import Image as Img

import gym, time

import tkinter as tk
from tkinter import *
import datetime

import threading

from data import Environment, Episode, Derived, Step, Meta, Config, Final_State, saveData

import LunarLander;

# ENV CONFIG
env = LunarLander.LunarLander()
print(type(env))
if not hasattr(env.action_space, 'n'):
    raise Exception('Keyboard agent only supports discrete action spaces')

# CONSTANTS
render_speed = 0.04
ACTIONS = env.action_space.n
                    
# USER CONFIGS
user_choice = "Other"
label_choice = "Regular"
episode_desc = ""

# ACTIONS
flags = [False, False, False, False]

human_agent_action = 0
human_wants_restart = True
human_sets_pause = False
human_wants_start = True
human_wants_stop = False
human_wants_exit = False
stop_threads = False
save_button_enabled = False

root = None

# THREAD FUNCTIONS
 
def click_start():
    global human_wants_start, human_wants_stop, save_button_enabled

    print("click start called")
    rollout(env, current_milli_time())
    human_wants_start = True
    human_wants_stop = False
    save_button_enabled = False
    
def click_stop():
    global human_wants_stop, human_wants_start, save_button_enabled, step_list

    print("click stop called")
    total_reward = 0
    for step in step_list:
        total_reward += step.environment.reward
    print("total reward:")
    print(total_reward)
    human_wants_stop = True
    human_wants_start = False
    save_button_enabled = True

# label
# expert name
# date and time
# delay
# step_count


def click_save():
    global step_list, label_choice, user_choice, episode_desc, human_wants_stop

    if (not human_wants_stop) or (not step_list):
        return
    
    #print("Inside Step List", step_list)
    
    step_count = len(step_list)
    date = datetime.datetime.now()
    
    meta = Meta(type_label=label_choice,
                    expert_name=user_choice,
                    date_time = date)
    
    total_reward = 0
    for step in step_list:
        total_reward += step.environment.reward

    state_tuple = step_list[-1].environment.state

    # TODO : Total fuel consumed logic
    total_fuel_consumed = 100

    final_state = Final_State(total_fuel_consumed=total_fuel_consumed,
                                state_tuple= state_tuple,
                                cummalative_reward=total_reward)
    
    config = Config(delay=render_speed, step_count=step_count)

    episode = Episode(version=0, meta=meta, final_state=final_state,
                         config=config, notes = episode_desc)

    # Calling Save Function
    saveData(episode, step_list)

    print("data saved")
    #print(episode)
    step_list.clear()

def click_exit():
    global human_wants_exit, human_wants_stop, stop_threads
    human_wants_stop = False
    root.destroy()
    human_wants_exit = True
    stop_threads = True

# TKINTER CODE
def display_loop():
    
    global root
    
    # main tkinter configs
    root = tk.Tk()
    root.geometry("500x500")
    root.title("something hete")
    root.protocol("WM_DELETE_WINDOW", root.quit)
    
    # User Choice
    USER_OPTIONS = ["Rushik", "Rahul", "Safeer", "Pranav", "Other"]
    user_choice_variable = StringVar(root)
    user_choice_variable.set(USER_OPTIONS[0])
    
    option_widget = OptionMenu(root, user_choice_variable, *USER_OPTIONS)
    option_widget.pack()
    
    def select_user():
        global user_choice    
        user_choice = user_choice_variable.get()
    
    user_choice_button = Button(root, text = "OK", command = select_user)
    user_choice_button.pack()
    
    # labels
    LABEL_OPTIONS = ["Regular", "Somersault"]
    label_choice_variable = StringVar(root)
    label_choice_variable.set(LABEL_OPTIONS[0])
    
    label_widget = OptionMenu(root, label_choice_variable, *LABEL_OPTIONS)
    label_widget.pack()
    
    def select_label():
        global label_choice
        label_choice = label_choice_variable.get()
        
    label_choice_button = Button(root, text = "OK", command = select_label)
    label_choice_button.pack()
        
    
    # Start/Stop Frame
    start_stop_frame = Frame(root)
    start_stop_frame.pack()

    startbutton = Button(start_stop_frame, text = 'Start', fg ='green', command = click_start)
    startbutton.pack(side = LEFT)
    
    stopbutton = Button(start_stop_frame, text = 'Stop', fg ='red', command = click_stop)
    stopbutton.pack(side = LEFT)

    # Save Buton
    savebutton = Button(root, text="Save", fg="blue", command=click_save)
    savebutton.pack()


    # Exit Button
    exitbutton = Button(root, text="Exit", fg="black", command=click_exit)
    exitbutton.pack()
    
    # Desc
    def set_desc():
        global episode_desc
        episode_desc = inputtxt.get(1.0, "end-1c")
    
    # TextBox Creation
    inputtxt = tk.Text(root, height = 5, width = 20)
    inputtxt.pack()
    
    printButton = tk.Button(root, text = "Save Episode Desc", command = set_desc)
    printButton.pack()
    
    root.mainloop()

# MAIN THREAD
class App(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
    
    def callback(self):
        self.root.quit()
        
    def run(self):
        display_loop()
        global stop_threads
        if stop_threads:
            return

app = App()

# UTILITIES

def current_milli_time():
    return round(time.time() * 1000)


def mapWasd(key):
    #print(key)

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
    human_agent_action = a
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

import io

def numpy2pil(np_array: np.ndarray):
    """
    Convert an HxWx3 numpy array into an RGB Image
    """
    #print(np_array)
    assert_msg = 'Input shall be a HxWx3 ndarray'
    assert isinstance(np_array, np.ndarray), assert_msg
    assert len(np_array.shape) == 3, assert_msg
    assert np_array.shape[2] == 3, assert_msg

    img = Img.fromarray(np_array, 'RGB')
    #img.save("x.png")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")

    #f = open("myfile.png", "wb")
    #f.write(img_byte_arr.getvalue())
    #f.flush()
    #f.close()
    return img_byte_arr.getvalue()


# list to record Step Data-> Environment
step_list = []
import base64
import numpy as np
def rollout(env, startTime):
    
    global human_agent_action, human_wants_restart, human_sets_pause, human_wants_stop, human_wants_start, user_choice, label_choice, human_wants_exit, step_list, save_button_enabled
    
    human_wants_restart = False
    human_wants_start = False
    human_wants_stop = False
    human_wants_exit = False
    # save_button_enabled = False
    
    obser = env.reset()
    step_list = [] 
    # print("After reset")

    total_reward = 0
    total_timesteps = 0
    
    # to keep track of step
    sequence_number = 0

    while 1:
        
        #increment sequence number
        sequence_number+=1

        # print(user_choice, label_choice)

        a = human_agent_action
        total_timesteps += 1

        actionCount = 1
        noAction = True
        
        obser, r, done, info = env.step(a)
        print(r)

                #actionCount+=1
                #env.render()
                #env.render()


        environment = Environment (
                        state=obser.tolist(),
                        action = tuple(flags),
                        reward=r)

        #TODO: Fuel Consumed logic
        fuel_consumed = -1

        #capturing frame from render as an rgb_array
        nparray = np.array(env.render('rgb_array'))

        frame = numpy2pil(nparray)
        #print(frame)

        #x = Img.frombytes(frame)
        #x.save("123.png")

        step_list.append(
            Step(parent_episode_ref=0,
                capture_frame=frame,
                sequence_number=sequence_number,
                environment=environment,
                derived = Derived(fuel_consumed=fuel_consumed)))
                 
        total_reward += r
        # print(human_wants_start, human_wants_stop)
        #if window_still_open==False: return False
        #if done: break
        #if human_wants_restart: break
        
        if done:
            click_stop()

        if human_wants_start:
            # print("Pressed Restart")
            break
        
        # if human_wants_stop:
        #     save_button_enabled = True
        while human_wants_stop:
            env.render()
            time.sleep(0.01)
            
        # print(actionCount)

        if human_wants_exit:
            return False
        
        time.sleep(render_speed)# + render_speed*(actionCount-1)*2)
#     print("timesteps %i reward %0.2f" % (total_timesteps, total_reward))

# print("ACTIONS={}".format(ACTIONS))
# print("Press keys 1 2 3 ... to take actions 1 2 3 ...")
# print("No keys pressed is taking action 0")

while 1:
    window_still_open = rollout(env, current_milli_time())
    if window_still_open == False:
        # print("CLOSE ALL WINDWW")
        app.join()
        # print('thread killed')
        env.close()
        break

print("broken out of all loops")


