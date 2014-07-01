import praw
import time
import datetime
import re
import ConfigParser
import os

#Load the options from the config file
config = ConfigParser.ConfigParser()
config.read('reddit.ini')
username = config.get('Bot Details', 'username')
password = config.get('Bot Details', 'password')
subreddit = config.get('Reddit Details', 'subreddit')
bot_user = config.get('Reddit Details', 'bot user')
modlog = config.get('Reddit Details', 'modlog')
ignore_mod_actions = config.get('Reddit Details', 'ignore mod actions')
loop = config.get('Reddit Details', 'loop')

#Connect to Reddit
r = praw.Reddit("Public ModLog bot for /r/"+subreddit+" by /u/edfaz. I'm run by /u/"+bot_user+".")
r.login(username, password)

#Initialise some variables required for the script
already_done_action = []
already_done_log = []

#This var controls the constant running of the bot. True will stop the bot.
stop = False

#Convert Unix timestamp to Y-M-D H-M-S format.
def timestamp_convert(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

#Remove Reddit's comment ID prefix via a regex match
def remove_t3(string):
    if string is None:
        return "None"
    else:
        return re.sub('t[0-9]_', '', string)


#Start the bot loop
while stop is False:
    try:
        #Open the output file
        text_file = open("output.txt", "w")

        #Title for the Wiki page
        mod_log_formatted = "#Mod Log for "+subreddit+" \n\n \n\n \n\n"
        mod_log_formatted += "This page shows the last 50 moderator actions\n\n"
        #Columns for the table. Don't change these unless you are going to change the 'for action in mod_log' loop
        table_r1 = "|  Time  |  Mod  |  Target  |  Action  |  Details  | \n"
        #Table formatting. Set to centre-align.
        table_r2 = "|:------------:|:------------:|:------------:|:------------:|:------------:| \n"
        mod_log_formatted += table_r1
        mod_log_formatted += table_r2
        #Initialise some vars
        mod_log_formatted_buffer = ""
        mod_log = []

        #Request the Mod log and format it for the next loop.
        for mod_action in r.get_subreddit(subreddit).get_mod_log(limit=50):
            if timestamp_convert(mod_action.created_utc) not in already_done_action and mod_action.action not in ignore_mod_actions:
                mod_log.append([timestamp_convert(mod_action.created_utc), mod_action.mod, remove_t3(mod_action.target_fullname), mod_action.action, mod_action.details])
                already_done_action.append(timestamp_convert(mod_action.created_utc))

        #Process each line of the mod log
        for action in mod_log:
            mod_log_temp_buffer = ""
            #If the moderator action for this line of the log is not on the ignore list and hasn't been processed already, format it.
            #Follows Reddit's formatting syntax. Check output.txt for the final product.
            if action[0] not in already_done_log and action[3] not in ignore_mod_actions:
                already_done_log.append(action[0])
                mod_log_temp_buffer += "| "
                mod_log_temp_buffer += action[0]
                mod_log_temp_buffer += " | "
                mod_log_temp_buffer += action[1]
                mod_log_temp_buffer += " | "
                #If the action taken has no comment ID, don't try to process it. Else generate a url to the comments
                if action[2] is "None":
                    mod_log_temp_buffer += " "
                else:
                    mod_log_temp_buffer += "http://www.reddit.com/r/"+subreddit+"/comments/"+action[2]
                mod_log_temp_buffer += " | "
                mod_log_temp_buffer += action[3]
                mod_log_temp_buffer += " | "
                mod_log_temp_buffer += action[4]
                mod_log_temp_buffer += " |"
                mod_log_temp_buffer += " \n"
                print mod_log_temp_buffer
                mod_log_formatted_buffer += mod_log_temp_buffer



        #Add the processed log to the title and table formatting done at the start. Then add the footer.
        mod_log_formatted += mod_log_formatted_buffer
        mod_log_formatted += "\n\n *** \n\n This page was generated by a bot. Please contact /u/"+bot_user+" if there's a problem. My source code is at [GitHub](https://github.com/fazzertron/reddit-modlogbot)"

        #Some basic diagnostic stuff. Comment out the r.edit_wiki_page line to just test the output (will be in output.txt).
        print "Writing the wiki page..."
        r.edit_wiki_page(subreddit, modlog, mod_log_formatted, "Updated Mod Log")
        print "Page written!"

        #Write to output.txt
        print "Writing output file..."
        text_file.write(mod_log_formatted)
        text_file.close()
        print "File written!"

        if loop == "yes":
            #Sleep to avoid spamming Reddit
            print "Now sleeping..."
            #time.sleep(3600)
            print "Sleep over, resuming..."
        else:
            print "Done! Now stopping."
            print "If you didn't want this to happen, set loop to yes in the config."
            stop = True

    #Some errors to catch
    except KeyboardInterrupt:
        print "[ERROR]: User closed program."
        stop = True
    except praw.errors.APIException, e:
        print "[ERROR]:", e
        print "sleeping 30 sec"
        sleep(30)
    except Exception, e:
        print "[ERROR]:", e
        print "blindly handling error"
        stop = True





