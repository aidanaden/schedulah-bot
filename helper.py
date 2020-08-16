import datetime

class schedulah_keyboard():


    def __init__(self, layout=[3, 4], defaults=['/start', '/back', '/done']):
        self.layout = layout
        self.defaults = defaults


    def create_days_keyboard(self):

        # create days array (value of the keyboard buttons)
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        # final array to return keyboard values with self.layout 
        days_keyboard = []

        # create starting index value
        start_idx = 0
        
        # itarate through layout array, get index and value of 
        # each row from self.layout
        for i,n in enumerate(self.layout):

            # create array to store values of each keyboard row
            keyboard_row = []

            # iterate through value array and add values according
            # to number of values in each row per self.layout

            # e.g with days keyboard we are following [3, 4] layout
            # which means the first row will contain 3 values (days)
            # while the second row will contain 4 values (days)

            # create final index (starting index + num of values in row)
            end_idx = start_idx + n

            for day in (days[start_idx:end_idx]):
                keyboard_row.append(day)
            
            days_keyboard.append(keyboard_row)
            start_idx = end_idx

        # add default commands to bottom of keyboard array    
        days_keyboard.append(self.defaults)

        return days_keyboard
        

    def create_keyboard(self, values):
        # final array to return keyboard values with self.layout 
        values_keyboard = []

        # create starting index value
        start_idx = 0
        
        # itarate through layout array, get index and value of 
        # each row from self.layout
        for i,n in enumerate(self.layout):

            # create array to store values of each keyboard row
            keyboard_row = []

            # iterate through value array and add values according
            # to number of values in each row per self.layout

            # e.g with days keyboard we are following [3, 4] layout
            # which means the first row will contain 3 values (days)
            # while the second row will contain 4 values (days)

            # create final index (starting index + num of values in row)
            end_idx = start_idx + n

            for value in (values[start_idx:end_idx]):
                keyboard_row.append(value)
            
            values_keyboard.append(keyboard_row)
            start_idx = end_idx

        # add default commands to bottom of keyboard array    
        values_keyboard.append(self.defaults)

        return values_keyboard




def converted_to_string(time_string):
    if isinstance(time_string, datetime.date):
        time_string = time_string.strftime('%H%M')
    return time_string