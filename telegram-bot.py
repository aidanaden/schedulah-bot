import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)
from credentials import *
from helper import *
from datetime import datetime




# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)




CREATE_EDIT, DAY, VIEW, EDIT, CONFIRM_EDIT, ACTIVITY, ADDED_ACTIVITY, COMPLETED = range(8)




# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    

    reply_values = ['/create', '/edit', '/view']
    start_keyboard = schedulah_keyboard(layout=[3]).create_keyboard(reply_values)


    welcome_msg = """Welcome! I'm the Schedulah Bot.
Create your weekly/daily schedule with us and we'll send reminders for your activities before they start! (just in case you forget) ;)


How to use me?


I've got 4 commands:

1. /create
2. /edit
3. /view
4. /done


/create - create a new schedule with me! 

/edit - edit your existing schedule with me! :)

/view - view your existing schedule with me! ;)

/done - exit from the bot at any time! :>    
    """
    
    update.message.reply_text(welcome_msg, 
    reply_markup=ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True, one_time_keyboard=False))


    return CREATE_EDIT




def create_new_calender(update, context):
    """Create new calender/timetable"""
    """Which day would you like to set up activities for? :)"""

    days_keyboard = schedulah_keyboard().create_days_keyboard()

    reply_msg = """Creating a new calender!
Which day would you like to 
set activites for?"""

    update.message.reply_text(reply_msg,
        reply_markup=ReplyKeyboardMarkup(days_keyboard, resize_keyboard=True, one_time_keyboard=False))
    
    
    return DAY




def edit_existing_calender(update, context):
    """Edit existing calender/timetable"""

    days_keyboard = schedulah_keyboard().create_days_keyboard()

    update.message.reply_text(
        'Editing your existing calender!'
        'Which day would you like to edit activites for?',
        reply_markup=ReplyKeyboardMarkup(days_keyboard, resize_keyboard=True, one_time_keyboard=False))


    return EDIT




def edit_day_activity(update, context):
    """User replies with day they want to edit. Ask user for name of activity they want to edit."""


    day = update.message.text
    day_activities = get_day_activities(day, context)


    reply_msg = f"""Activites for <b>{day.lower()}</b>\n\n{day_activities}\n\nWhich activity do you wanna edit? (pls enter name of activity tenks)"""


    update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)


    return CONFIRM_EDIT




def confirm_complete_edit(update, context):
    """User completed editing activities in a specific day they selected, 
    ask user if done or want to edit another day"""


    exit_values = ['Continue editing!', 'Change day!']
    exit_keyboard = schedulah_keyboard(layout=[2]).create_keyboard(exit_values)
    

    reply_msg = f"""Add more activities to your <b>{day.lower()}</b> schedule? or add activities to another day?"""


    update.message.reply_text(reply_msg, 
    reply_markup=ReplyKeyboardMarkup(exit_keyboard, resize_keyboard=True, one_time_keyboard=True), parse_mode=ParseMode.HTML)




def view_existing_calender(update, context):
    """View existing calender/timetable"""

    view_days_values = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday', 'View All Days']
    view_keyboard = schedulah_keyboard(layout=(3,4,1)).create_keyboard(view_days_values)

    update.message.reply_text(
        'Viewing your existing calender! Which day would you like to view activities for? :)',
        reply_markup=ReplyKeyboardMarkup(view_keyboard, resize_keyboard=True, one_time_keyboard=False))

    
    return VIEW




def get_day_activities(day, context):

    activities_msg = f"\n\n<b>{day.upper()}</b>\n\n"

    if day not in context.user_data or context.user_data[day] == "" or context.user_data[day] is None:

        activity_msg = "No activities created yet!\n\n"
        activities_msg += activity_msg

        return activities_msg

    else:

        activities = context.user_data[day]
        
        for activity in activities:
                
            time_start = converted_to_string(activity['time_start'])
            time_end = converted_to_string(activity['time_end'])
            name = activity['name']
            location = activity['location']
            details = activity['details']

            activity_msg = f"""NAME: {name}\nTIME: {time_start} - {time_end}\nLOCATION: {location}\nDETAILS: {details}\n\n"""
            activities_msg += activity_msg

        return activities_msg




def _view_all_calender_days(context, all_activities_msg="", days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']):

    for day in days:

        day_activities_msg = get_day_activities(day, context)
        all_activities_msg += day_activities_msg
    
    return all_activities_msg




def view_calender_day(update, context):
    """User enters day, output all activities added on day"""


    day = update.message.text

    
    if day not in context.user_data or context.user_data[day] is None:
        update.message.reply_text(f'Sorry! Looks like you haven\'t created any activities on <b>{day.lower()}</b> yet!', parse_mode=ParseMode.HTML)

    
    else:
    
        activities_msg = get_day_activities(day, context)
        update.message.reply_text(activities_msg, parse_mode=ParseMode.HTML)
    

    return VIEW




def view_all_calender_days(update, context):

    all_activities_msg = _view_all_calender_days(context=context)

    update.message.reply_text(all_activities_msg, parse_mode=ParseMode.HTML)

    return VIEW




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
    reply_msg = f"""Accessing your <b>{text.lower()}</b> schedule!
To add an activity to your schedule,
Enter the details of your activity in the format below.
        
<b>EXAMPLE</b>
TIME: 1200-1400
NAME: CS2030
LOCATION: HOME
DETAILS: ELEARNING until further notice"""


    update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)

    return ACTIVITY




def add_activity_calender_day(update, context):
    """User enters activity, add activity to the schedule of the selected day"""


    # get day of activity 
    day = context.user_data['day']


    activity_text = update.message.text 


    [activity_time, activity_name, activity_loc, activity_details] = [x.split(':')[1] for x in activity_text.splitlines()]


    activity_time_start, activity_time_end = get_activity_time_start_end_to_datetime(activity_time)


    activity = {
        'time_start': activity_time_start,
        'time_end': activity_time_end,
        'name': activity_name,
        'location': activity_loc,
        'details': activity_details
        }
    

    if day not in context.user_data:
        context.user_data[day] = [activity]

    elif context.user_data[day] is None:
        context.user_data[day] = [activity]

    else:
        update.message.reply_text(f"""Looks like you\'ve already got some activities set for your <b>{day.lower()}</b> schedule!
        \nAdding your newly created activity: \"{activity_name}\" to your <b>{day.lower()}</b> schedule!""", parse_mode=ParseMode.HTML)

        # TODO: CHECK IF NEW ACTIVITY ADDED COINCIDES WITH ANY EXISTING ACTIVITIES
        
        context.user_data[day].append(activity)


    exit_values = ['Add more!', 'Change day!']
    exit_keyboard = schedulah_keyboard(layout=[2]).create_keyboard(exit_values)
    

    reply_msg = f"""Add more activities to your <b>{day.lower()}</b> schedule? or add activities to another day?"""


    update.message.reply_text(reply_msg, 
    reply_markup=ReplyKeyboardMarkup(exit_keyboard, resize_keyboard=True, one_time_keyboard=True), parse_mode=ParseMode.HTML)

    
    return ADDED_ACTIVITY




def add_more_activities_calender_day(update, context):
    """User enters day, guide user to enter details of activity"""
    

    day = context.user_data['day']   


    reply_msg = f"""Adding to your <b>{day.lower()}</b> schedule!
To add an activity to your schedule,
Enter the details of your activity in the format below.
        
<b>EXAMPLE</b>
TIME: 1200-1400
NAME: CS2030
LOCATION: HOME
DETAILS: ELEARNING until further notice"""


    update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)


    return ACTIVITY




def change_calender_day(update, context):
    """Which day would you like to set up activities for?"""


    day_keyboard = schedulah_keyboard().create_days_keyboard()

    update.message.reply_text(
        'Which day would you like to set activites for? :)',
        reply_markup=ReplyKeyboardMarkup(day_keyboard, resize_keyboard=True, one_time_keyboard=False))
    
    
    return DAY




def confirm_complete(update, context):
    """
    User enters im done after adding activity to day schedule.
    Ask for final confirmation (if user would like to view existing 
    calender or simply exit from bot)
    """

    exit_msg = f"""Are you sure you\'re done with your calender?\n 
You may also proceed to view your existing calender before exiting the bot!"""


    exit_options = [['Confirm exit!','View schedule and tHEN exit!']]
    exit_keyboard = schedulah_keyboard(layout=[2]).create_keyboard(exit_options)


    update.message.reply_text(exit_msg, 
    reply_markup=ReplyKeyboardMarkup(exit_options, resize_keyboard=True, one_time_keyboard=True))


    return COMPLETED




def completed_and_exit(update, context):
    """
    User confirms exit, end conversation and quit from schedulah-bot
    """


    update.message.reply_text('Bye bYE!!')


    return ConversationHandler.END




def view_and_exit(update, context):
    """
    User requests to view schedule, then exit
    """

    all_activities_msg = _view_all_calender_days(context=context)

    update.message.reply_text(all_activities_msg, parse_mode=ParseMode.HTML)
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
                MessageHandler(Filters.regex('^(/create)$'), create_new_calender), 
                MessageHandler(Filters.regex('^(/edit)$'), edit_existing_calender),
                MessageHandler(Filters.regex('^(/view)$'), view_existing_calender)
                ],

            DAY: [
                MessageHandler(Filters.regex('^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$'), enter_calender_day)
            ],

            VIEW: [
                MessageHandler(Filters.regex('^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$'), view_calender_day), 
                MessageHandler(Filters.regex('^(View All Days)$'), view_all_calender_days)
            ],

            EDIT: [
                MessageHandler(Filters.regex('^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$'), edit_calender_day)
            ],

            ACTIVITY: [
                MessageHandler(Filters.regex('^(TIME:)( )?[0-2][0-9][0-5][0-9]( )?[-]( )?[0-2][0-9][0-5][0-9](\nNAME:)( )?(.+)(\nLOCATION:)( )?(.+)(\nDETAILS:)( )?(.*)'), add_activity_calender_day)
            ],

            ADDED_ACTIVITY: [
                MessageHandler(Filters.regex('^(Add more!)$'), add_more_activities_calender_day),
                MessageHandler(Filters.regex('^(Change day!)$'), change_calender_day),
                MessageHandler(Filters.regex('^(I\'m done!)$'), confirm_complete)
            ],

            COMPLETED: [
                MessageHandler(Filters.regex('^(Confirm exit!)$'), completed_and_exit),
                MessageHandler(Filters.regex('^(View schedule and tHEN exit!)$'), view_and_exit)
            ]
        },
        fallbacks=[CommandHandler('done', confirm_complete), CommandHandler('start', start)],
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