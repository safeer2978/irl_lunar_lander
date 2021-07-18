## What this file is supposed to do???

# To create Episode, step and version dictionaries.
# To save these dictionaries into mongo

## collect data using functions and structure them as 
# dictionaries so they could be saved into mongo.

## this file is only responible to write data into mongo.

### TODO: Change Database name according to the requirement.
### TODO: Insert Version and Deails into database.


# Constants
VERSION_NUMBER = 1
DB_NAME = "test"
DB_port = 27017
DB_HOST = 'localhost'

# Remains unchanged until schema is changed.
def createVersion():
    id=1
    version_number = VERSION_NUMBER
    date_of_creation = ""
    description = ""
    version = {id, version_number, date_of_creation, description}
    return version


def saveData(episode, step):
    return 1

#from _typeshed import StrPath
from dataclasses import dataclass, asdict
import dataclasses
from typing import List

#Episode

@dataclass
class Meta():
    type_label:str
    expert_name:str
    date_time:str
    
@dataclass
class Final_State():
    state_tuple:tuple
    cummalative_reward:int
    total_fuel_consumed:int
    
@dataclass
class Config():
    delay:int
    step_count:int
    

@dataclass
class Episode():
    #id: int
    version:int 
    meta: Meta
    final_state:Final_State
    config: Config
    

@dataclass
class Step():
    a:int

# print(asdict(Episode(id=5,
#                     version=54,
#                     meta = Meta("normal", "safeer", "monday"),
#                     final_state= Final_State((1,2,3),123,123),
#                     config=Config(12,13) )))


# Step

@dataclass
class Environment():
    state: tuple
    action: tuple
    reward: int

@dataclass
class Derived():
    fuel_consumed: int


@dataclass
class Step():
    parent_episode_ref: int # Check
    capture_frame: list
    sequence_number: int
    environment: Environment
    derived: Derived

# print(asdict(Step(parent_episode_ref=1,
#                 capture_frame=[6,7,8],
#                 sequence_number=45,
#                 environment=Environment((5,3,4,2),(2,5,6,4),645),
#                 derived=Derived(34))))



from pymongo import MongoClient

client = MongoClient(DB_HOST, DB_port)
db = client[DB_NAME]
episode_collection=db['episode']
step_collection=db['step']

## Data is saved at the end of an episode
## Data would include A single Episode Object and a List of Step Objects.
def saveData(episode: Episode, steps:list()):
    #Set schema version to episode
    episode.version = VERSION_NUMBER
    
    #write the episode into mongodb.
    
    episode_ = episode_collection.insert_one(asdict(episode))
    id = episode_.inserted_id #episode_.id # get this from mongo
    #handle the ID of the episode and map all steps with that.
    for step in steps:
        #map the id to each step
        step.parent_episode_ref = id
    
    step_dicts = []
    #convert list of dataclass to list of dict
    for step in steps:
        step_dicts.append(asdict(step))

    #save data to mongoDB
    step_collection.insert_many(step_dicts)

## Insert Test
# saveData(Episode(
#                      version=54,
#                      meta = Meta("normal", "safeer", "monday"),
#                      final_state= Final_State((1,2,3),123,123),
#                      config=Config(12,13) ),
# [Step(parent_episode_ref=1,
#                  capture_frame=[6,7,8],
#                  sequence_number=45,
#                  environment=Environment((5,3,4,2),(2,5,6,4),645),
#                  derived=Derived(34))])
    
