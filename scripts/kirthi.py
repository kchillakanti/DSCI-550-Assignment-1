# This is template. Feel free to modify it. 

from main import raw_data
import pandas as pd
#from ryan import output_for_chain
#import class_name from script_name_in_folder

"""
Class is a container which is good for put all the data and functions(methods) into one object 
and generate many diversified version, which is called 'instance'. 
If you do not need to create many instnaces, you can design your script without Class.
"""
class Myclass(): #If you have superclass to get inheritance, put the name in the paranthesis. 
    # this class attributes are shared across all the instances of Myclass type.
    class_attrribute_1 = 0 
    class_attribute_2 = ""
    
    def __init__(self): # initializer 
        instance_attribute_1 = 0 
        instance_attribute_2 = "" 
        print("Congrats! You've just generate an instance of Myclass") 
        pass


def custom_function(input):
    """function tooltip - this will pop up when you call your function"""
        
    'Write your function here'

    return 100 



output_for_chain = 'put your output here to convey to next person'