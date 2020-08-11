import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)
from credentials import *




# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)




CREATE_EDIT, DAY, ACTIVITY, ADDED_ACTIVITY, VIEW_ALL, COMPLETED = range(6)

DAYS_REPLY_KEYBOARD = [['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']]




# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    

    reply_keyboard = [['Create', 'Edit', 'View']]


    welcome_msg = """Welcome! I'm the Schedulah Bot. Create your weekly/daily 
    schedule with us and we'll send reminders for your activities before they 
    start! (just in case you forget) ;)
    
    How to use me?

    I've got 3 commands
    1. Create
    2. Edit
    3. View

    Create - create a new schedule with me! 

    Edit - edit your existing schedule with me! :)

    View - view your existing schedule with me! ;)
    
    """
    
    update.message.reply_text(welcome_msg, 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


    return CREATE_EDIT




def create_new_calender(update, context):
    """Create new calender/timetable"""
    """Which day would you like to set up activities for? :)"""


    update.message.reply_text(
        'Creating a new calender!'
        'Which day would you like to set activites for?',
        reply_markup=ReplyKeyboardMarkup(DAYS_REPLY_KEYBOARD, one_time_keyboard=True))
    
    
    return DAY




def edit_existing_calender(update, context):
    """Edit existing calender/timetable"""


    update.message.reply_text(
        'Editing your existing calender!'
        'Which day would you like to edit activites for?',
        reply_markup=ReplyKeyboardMarkup(DAYS_REPLY_KEYBOARD, one_time_keyboard=True))


    return None




def view_existing_calender(update, context):
    """View existing calender/timetable"""


    update.message.reply_text(
        'Viewing your existing calender!'
        'Which day would you like to view activities for? :)',
        reply_markup=ReplyKeyboardMarkup(DAYS_REPLY_KEYBOARD, one_time_keyboard=True))




def enter_calender_day(update, context):
    """User enters day, guide user to enter details of activity"""
    
    
    # remove previous 'day' value so 
    # that we can insert current 'day' value
    if 'day' in context.user_data:
        del context.user_data['day']


    # set new 'day' value
    text = update.message.text
    context.user_data['day'] = text  


    # request user to add activity in 
    # ACTIVITY FORMAT
    update.message.reply_text(
        f'Accessing your {text} schedule!'
        'To add an activity to your schedule,'
        'Enter the details of your activity in the format below.\n\n'
        '<EXAMPLE>\n'
        'TIME: 1200-1400'
        'NAME: CS2030'
        'LOCATION: HOME'
        'DETAILS: ELEARNING until further notice'
    )

    return ACTIVITY




def get_activity_time_start_end(activity_time):
    """
    Receive activity time string in format XXXX-XXXX
    EXAMPLE:
    
    1200-1400
    """


    activity_time_start = activity_time.split('-')[0]
    activity_time_end = activity_time.split('-')[1]

    
    return activity_time_start, activity_time_end




def add_activity_calender_day(update, context):
    """User enters activity, add activity to the schedule of the selected day"""


    # get day of activity 
    day = context.user_data['day']


    activity_text = update.message.text 


    [activity_time, activity_name, activity_loc, activity_details] = [x.split(':')[1] for x in activity_text.splitlines()]


    activity_time_start, activity_time_end = get_activity_time_start_end(activity_time)


    activity = {
        'time_start': activity_time_start,
        'time_end': activity_time_end,
        'name': activity_name,
        'location': activity_loc,
        'details': activity_details
        }
    

    if context.user_data[day] is None:
        context.user_data[day] = [activity]
    else:
        update.message.reply_text(f"""Looks like you\'ve already got some activities set for your {day} schedule!
        \nAdding your newly created activity: \"{activity_name}\" to your schedule!""")

        # TODO: CHECK IF NEW ACTIVITY ADDED COINCIDES WITH ANY EXISTING ACTIVITIES
        
        context.user_data[day].append(activity)


    exit_options = [['Add more!', 'Change day!', 'I\'m done!']]
    exit_keyboard = ReplyKeyboardMarkup(exit_options, one_time_keyboard=True)


    update.message.reply_text(f"""Would you like to add more activities 
                                to your {day} schedule or would you like 
                                to add activities to another day?""", reply_markup=exit_keyboard)

    


    return ADDED_ACTIVITY




def add_more_activities_calender_day(update, context):
    """User enters day, guide user to enter details of activity"""
    

    day = context.user_data['day']   


    update.message.reply_text(
        f'Adding to your {day} schedule!'
        'To add an activity to your schedule,'
        'Enter the details of your activity in the format below.\n\n'
        '<EXAMPLE>\n'
        'TIME: 1200-1400'
        'NAME: CS2030'
        'LOCATION: HOME'
        'DETAILS: ELEARNING until further notice'
    )

    return ACTIVITY




def change_calender_day(update, context):
    """Which day would you like to set up activities for?"""


    update.message.reply_text(
        'Which day would you like to set activites for? :)',
        reply_markup=ReplyKeyboardMarkup(DAYS_REPLY_KEYBOARD, one_time_keyboard=True))
    
    
    return DAY




def confirm_complete(update, context):
    """
    User enters im done after adding activity to day schedule.
    Ask for final confirmation (if user would like to view existing 
    calender or simply exit from bot)
    """


    exit_options = [['Confirm exit!','View schedule and tHEN exit!']]
    exit_keyboard = ReplyKeyboardMarkup(exit_options,one_time_keyboard=True)

    update.message.reply_text(f"""Are you sure you\'re done with your calender? 
    You may also proceed to view your existing calender before exiting the bot!""", reply_markup=exit_keyboard)


    return COMPLETED






def completed_and_exit(update, context):
    """
    User confirms exit, end conversation and quit from schedulah-bot
    """


    update.message.reply_text('Bye bYE!!')


    return ConversationHandler.END





def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    pp = PicklePersistence(filename='schedulah-bot')
    updater = Updater(TOKEN, persistence=pp, use_context=True)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # on different commands - answer in Telegram
    schedulah_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CREATE_EDIT: [
                MessageHandler(Filters.regex('^(Create)$'), create_new_calender), 
                MessageHandler(Filters.regex('^(Edit)$'), edit_existing_calender),
                MessageHandler(Filters.regex('^(View)$'), view_existing_calender)
                ],

            DAY: [
                MessageHandler(Filters.regex('^(Monday)$'), enter_calender_day), 
                MessageHandler(Filters.regex('^(Tuesday)$'), enter_calender_day),
                MessageHandler(Filters.regex('^(Wednesday)$'), enter_calender_day),
                MessageHandler(Filters.regex('^(Thursday)$'), enter_calender_day), 
                MessageHandler(Filters.regex('^(Friday)$'), enter_calender_day),
                MessageHandler(Filters.regex('^(Saturday)$'), enter_calender_day),
                MessageHandler(Filters.regex('^(Sunday)$'), enter_calender_day)
            ],

            ACTIVITY: [
                MessageHandler(Filters.regex('^(TIME:)( )?[0-2][0-9][0-5][0-9]( )?[-]( )?[0-2][0-9][0-5][0-9](\nNAME:)( )?(.+)(\nLOCATION:)( )?(.+)(\nDETAILS:)( )?(.*)'), add_activity_calender_day)
            ],

            ADDED_ACTIVITY: [
                MessageHandler(Filters.regex('^(Add more)$'), add_more_activities_calender_day),
                MessageHandler(Filters.regex('^(Change day!)$'), change_calender_day),
                MessageHandler(Filters.regex('^(I\'m done!)$'), confirm_complete)
            ],

            COMPLETED: [
                MessageHandler(Filters.regex('^(Confirm exit!)$'), completed_and_exit),
                MessageHandler(Filters.regex('^(View schedule and tHEN exit!)$'), completed_and_exit)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^(I\'m done!|done!)$'), confirm_complete)],
        name='my_schedulah',
        persistent=True
    )


    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(schedulah_handler)


    # Start the Bot
    updater.start_polling()


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()




if __name__ == '__main__':
    main()