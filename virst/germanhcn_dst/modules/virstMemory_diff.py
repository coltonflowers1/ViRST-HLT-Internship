#######################
#Author: Colton Flowers
#Implements a different version of virstMemory.py similar to a counter
########################



class Memory():
        
        def __init__(self):
                self.exercise = ""
                self.action_memory = 0
                self.max = 0
                return 
        
        
        def set_exercise(self, exercise):
                
                self.exercise = exercise
                return 

        def update(self):
                """
                Increments action_memory by 1. 

                Parameters
                ----------
                N/A

                Returns
                -------
                Null
                """

                self.action_memory += 1
                
                return 

        def get_last_action(self):

                return self.action_memory
        
        def get_second_to_last(self):
                """
                Resets action_memory to the second to last number

                Parameters
                ----------
                N/A

                Returns
                -------
                Null
                """
                self.action_memory = self.max - 1
                
        def set_memory(self, number):
                """
                Resets action_memory to the given number. 

                Parameters
                ----------
                number : int

                Returns
                -------
                Null
                """
                self.action_memory = number
                
        def reset_memory(self, exercise):
                """
                Resets action_memory to 1. 
                Sets exercise to the given exercise.

                Parameters
                ----------
                exercise : str

                Returns
                -------
                Null
                """
                self.action_memory = 1
                self.exercise = exercise
                return 
        def is_at_end(self):
                return self.max == self.action_memory
                
