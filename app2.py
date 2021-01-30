from telegram import (KeyboardButton, KeyboardButtonPollType, ParseMode,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import os
import sys
from threading import Thread
from XYGameHandler import *
import msgs as respond

for f in os.listdir('./'):
	if f.endswith('.log'):
		os.remove(f)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                     filename=f'XY_logs.log', level=logging.INFO)

token = '<token here>' #Bot Token for Win As Much As You Can


def start(update, context):
	global admin
	if admin:
		context.bot.send_message(chat_id=update.effective_user.id, text=respond.start_admin(), parse_mode=ParseMode.HTML)
	else:
		context.bot.send_message(chat_id=update.effective_user.id, text=respond.start_noadmin(), parse_mode=ParseMode.HTML)
	return BEGIN


#Commands for Admin
#TODO: Remove oneself from admin command
def makeMeAdmin(update, context):
	global admin
	if not admin:
		admin = update.effective_user.id
		update.message.reply_text(respond.admin_success())
		logging.info(f'BEGIN: Admin is {update.effective_user.full_name}. Awaiting Confirmation')
		return ADMIN_STATE

	elif update.effective_user.id == admin:
		update.message.reply_text(respond.alr_admin())
		return ADMIN_STATE

	else:
		update.message.reply_text(respond.admin_taken())
		logging.info(f'BEGIN: User {update.effective_user.full_name} tried to make himself admin')


def admin_menu(update, context):
	context.bot.send_message(chat_id=admin, text=respond.admin_menu(), parse_mode=ParseMode.HTML)
	logging.info('ADMIN: Admin confirmed.')
	return ADMIN


def admin_new_game(update, context):
	logging.info(f'ADMIN: Trying to create new game with {context.args} players')
	try:
		if not context.args:
			update.message.reply_text(respond.newgame_0())

		elif int(context.args[0]) in range(1,13):
			logging.info(f'ADMIN: Number of players, {context.args[0]} players have been entered.')


			'''
			game.teams is a dictionary containing team objects. It first loads
			with a placeholder team number. It will be replaced with gameteams[user_id]
			pointing to the same object when the participant claims the team.
			Henceforth, team_no of this object will be referenced to as game.teams[user_id].team_no

			syntax for game methods:
			game.getcard(team[x])
			game.getscore(team[x])

			'''
			global game
			construct_new_game(context.args[0])


			update.message.reply_text(respond.newgame(game.no_teams))
			return GAME_OPEN_TO_JOIN

		else:
			update.message.reply_text("The number of teams are too big. This game only supports a max of 12 teams.")
			logging.info(f'ADMIN: Number of teams {context.args} out of range')

	except ValueError:
		update.message.reply_text("ADMIN: Invalid number of teams have been passed.")


#Creates a new game with the Google Sheets and creates dictionary mapping team to userid
def construct_new_game(teams):
	logging.info(f'ADMIN: Creating new game with {int(teams)} teams')
	round_no = 0
	global game
	game = Game(int(teams))


def admin_start_game(update, context):
	global game

	#check for vacant teams
	vteams = check_vacant_teams()

	if vteams:
		update.message.reply_text(f'Could not start game! \n\nThese teams have not joined: {vteams}')
		return

	for ID in game.teams.keys():
		game.teams_not_played.append(game.teams[ID].team_no)
	#start round 1
	game.round_no += 1
	game.teams_that_played = {'X': [], 'Y': []}
	#X and Y Buttons
	buttons = [[KeyboardButton('X'), KeyboardButton('Y')]]

	if game.round_no == 1:
		logging.info(f'GAME_OPEN_TO_JOIN: Game started by Admin')
		for ID in game.teams.keys():
			context.bot.send_message(chat_id=ID, reply_markup=ReplyKeyboardMarkup(buttons), text=f'Round {game.round_no}: <b>X</b> or <b>Y</b>?', parse_mode=ParseMode.HTML)
		context.bot.send_message(chat_id=admin, text=respond.startgame(), parse_mode=ParseMode.HTML)
		return PLAYERS_SUBMITTING


def check_vacant_teams():
	global game
	vacant_teams = []
	vteams = ''
	for t in game.teams.keys():
		if isinstance(t, str):
			vacant_teams.append(t)
	if vacant_teams:
		for t in sorted(vacant_teams):
			vteams += f'\nTeam {t}'
		return vteams

	else:
		return False


def admin_increment_round(update, context):
	global game
	vteams = check_vacant_teams()
	if vteams:
		logging.info(f'ROUND {game.round_no}: Teams not joined - {vteams}')
		update.message.reply_text(f'Could not go to next round! \n\nThese teams have not joined: {vteams}')
		return

	game.round_no += 1
	game.teams_that_played = {'X': [], 'Y': []}
	for ID in game.teams.keys():
		game.teams_not_played.append(game.teams[ID].team_no)

	#X and Y Buttons
	buttons = [[KeyboardButton('X'), KeyboardButton('Y')]]

	#DONE: Notification of Score Multipliers to admin and teams.
	if game.round_no in range(2,8):
		logging.info(f'REVEALING: Progressing game to Round {game.round_no}')

		#PLACEHOLDER; WILL PUT THIS INTO THE TEXT FILES.
		global bonus_rounds

		ask_for_card, admin_round_text = respond.card_req(game.round_no)

		#starts to ask for answers for the current team.
		for ID in game.teams.keys():
			#DONE: make buttons and all that jazz
			context.bot.send_message(chat_id=ID, reply_markup=ReplyKeyboardMarkup(buttons), text=ask_for_card, parse_mode=ParseMode.HTML)
		update.message.reply_text(admin_round_text)
		return PLAYERS_SUBMITTING

	#end of game conditions
	elif game.round_no == 8:
		end_of_game(update, context)
		return ENDGAME
	# else:
	# 	return POLLING


def end_of_game(update, context):
	global game
	#Facilitates end of the game
	for ID in game.teams.keys():
		context.bot.send_message(chat_id=ID, text=f'<b>Game over!</b> Your team has scored a total of <b>{game.getscore(game.teams[ID])} points</b>.', reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)

	#TODO: for easier reference send the full_names of the team representatives
	update.message.reply_text('Game has ended. Full results are on the Google Spreadsheet.')
	game = None
	logging.info('ROUND 7 END: Game has completed.')

#TODO: Make it possible for the admin to bump the participant to respond.
#DONE: Stop admin from revealing if not all teams have played
def admin_reveal_round_result(update, context):
	#reveals round score to participants
	#DONE check if all teams have played
	#disallows revealing if not all teams have played.
	if game.teams_not_played:
		teams_not_played_str = ''
		for i in game.teams_not_played:
			teams_not_played_str += f'\nTeam '

		logging.info(f'ROUND {game.round_no}Tried to reveal while these teams have not played: {teams_not_played_str}')
		update.message.reply_text(f'Could not reveal round yet - These teams have not submitted: {teams_not_played_str}')
		return

	#TODO: Customise the message based on whether they win or lose points.
	combi = game.getcombi()			#['aX', 'bY']

	logging.info(f'PLAYERS_SUBMITTING: {combi} \nteams that played x gained {game.xScore}.\nteams that played y gained {game.yScore}')

	results_msg = f'Results for Round {game.round_no}: <b>{combi[0][0]}X  {combi[1][0]}Y</b>'
	wamayc = 'Remember the name of the game, <i><b>Win As Much As You Can!</b></i>'
	#sends results to teams that played X and Y respectively.
	msgx = f'{results_msg}\n\nYour score for Round {game.round_no}: <b>{game.xScore}</b>\n\n{wamayc}'
	msgy = f'{results_msg}\n\nYour score for Round {game.round_no}: <b>{game.yScore}</b>\n\n{wamayc}'
	for ID in game.teams_that_played['X']:
		context.bot.send_message(chat_id=ID, text=msgx, parse_mode=ParseMode.HTML)
	for ID in game.teams_that_played['Y']:
		context.bot.send_message(chat_id=ID, text=msgy, parse_mode=ParseMode.HTML)

	#DONE: Give a summary in the text of the rounds.
	context.bot.send_message(chat_id=update.effective_user.id, text=respond.reveal(game.round_no, combi), parse_mode=ParseMode.HTML)

	#end game condition
	if game.round_no == 7:
		update.message.reply_text(respond.round7_over())
		return GAME_ENDING
	else:
		return REVEALING


#DONE: write the beginning menu with the commands and all that here as well.
#DONE: send message to all current participants about game ending and rejoining new game instructions
#DONE: anything that the participant puts from here brings them back to the begin state
def admin_stop_game(update, context):
	global game
	for ID in game.teams.keys():
		if isinstance(ID, int): 		#verify it is a team in use
			context.bot.send_message(chat_id=ID, text=respond.game_stopped())
	update.message.reply_text("Game Stopped. You will be put back into the admin start page.")
	game = None
	logging.info('Game stopped by admin.')
	update.message.reply_text(respond.admin_menu())
	return ADMIN


#DONE also try and do an admin_kick function if admin needs to remove representatives/ to swop etc. syntax: /remove <team no>
def admin_kick(update, context):
	#get the team number of removed team
	#return object
	#the rest is same as leavegame
	if not context.args:
		update.message.reply_text('Please specify the team to remove.')
		return

	try:
		#replies more than one word or team out of range
		if len(context.args) > 1 or int(context.args[0]) not in range(1, game.no_teams+1):
			update.message.reply_text('Team not found')
			return
		#if some random stuff is input
	except ValueError:
		update.message.reply_text('Team not found')
		return

	rep_id = find_team(int(context.args[0]))

	button = [[KeyboardButton('/quit')]]
	context.bot.send_message(chat_id=rep_id, text='You have been removed from the game. Press /quit to quit.')

	logging.info(f'Removed Team {context.args[0]} representative.')
	update.message.reply_text(f'Removed representative of Team {context.args[0]}')

	game.teams[context.args[0]] = game.teams[rep_id]
	del game.teams[rep_id]


def find_team(t):
	global game
	team_rep_id = 0
	for ID in game.teams.keys():
		if game.teams[ID].team_no == t:
			team_rep_id = ID
			logging.info(f'Player ID to remove: {team_rep_id}')
			break
	return team_rep_id


def admin_commands(update, context):
	logging.info('ADMIN: Showing Admin Commands')
	update.message.reply_text(respond.admin_menu())


def admin_help(update,context):
	global admin
	context.bot.send_message(chat_id=admin, text=respond.admin_help(), parse_mode=ParseMode.HTML)


#Commands for PARTICIPANT
def participant_query_team(update, context):
	#TODO: make keyboard buttons
	userid = update.effective_user.id
	logging.info(f'BEGIN: New participant id: {userid}')

	global game
	if game:
		kb = vacant_teams_kb()
		if kb[0]:
			context.bot.send_message(chat_id=update.effective_user.id, text='Which team are you representing?', reply_markup=ReplyKeyboardMarkup(kb))
			return PART_STATE

		else:
			update.message.reply_text('Unable to join the game because the game is full. You may /join again when there is a vacant team.')

	else:
		update.message.reply_text('There is no game running')


def vacant_teams_kb():
	vteams = []

	for t in game.teams.keys():
		if isinstance(t, str):
			vteams.append(f'Team {t}')

	logging.info(f'Vacant teams for kb: {vteams}')
	if len(vteams) < 4:
		vtButtons = []
		for i in range(len(vteams)):
			vtButtons.append(KeyboardButton(vteams[i]))
		return [vtButtons]

	#2 rows of buttons for number of vacant teams between 4 and 8
	elif len(vteams) > 3 and len(vteams) < 9:
		vtButtons1 = []
		vtButtons2 = []
		for i in range(len(vteams)//2):
			vtButtons1.append(KeyboardButton(vteams[i]))
		for i in range(len(vteams)//2, len(vteams)):
			vtButtons2.append(KeyboardButton(vteams[i]))
		return [vtButtons1, vtButtons2]

	#3 rows of buttons for number of vacant teams more than 8
	elif len(vteams) > 8:
		vtButtons1 = []
		vtButtons2 = []
		vtButtons3 = []
		for i in range(len(vteams)//3):
			vtButtons1.append(KeyboardButton(vteams[i]))
		for i in range(len(vteams)//3, 2*len(vteams)//3):
			vtButtons2.append(KeyboardButton(vteams[i]))
		for i in range(2*len(vteams)//3, len(vteams)):
			vtButtons3.append(KeyboardButton(vteams[i]))
		return [vtButtons1, vtButtons2, vtButtons3]



def participant_join_acknowledge(update, context):
	#TODO: make the query team buttons appear here again.
	global game
	global admin

	#if game cancelled:
	if not game:
		context.bot.send_message(chat_id=update.effective_user.id, text='Game was cancelled by admin. Please wait until a new one is set up, and rejoin with /join.', reply_markup=ReplyKeyboardRemove())
		return BEGIN

	part_id = update.effective_user.id
	part_team = update.message.text[-1]

	#DONE: if rep enters number out of range or some other random crap enter the different scenarios.
	#replaces the placeholder name for the team with userid
	try:
		game.teams[part_id] = game.teams[str(part_team)]
		del game.teams[str(part_team)]

	except KeyError:
		logging.info(f'PARTICIPANT_JOINING: {update.effective_user.full_name} entered invalid team no, {part_team}.')

		vteamsButtons = vacant_teams_kb()

		#Case where the team is alr taken
		if int(part_team) in range(1, game.no_teams+1):
			msg = f'<b>Team {part_team}</b> is already taken! Please choose a team from the options below.'

		#Case where team number entered is out of range
		else:
			msg = f'Team number is out of range. Please choose a team from the options below.'

		context.bot.send_message(chat_id=update.effective_user.id, text=msg, reply_markup=ReplyKeyboardMarkup(vacant_teams_kb()), parse_mode=ParseMode.HTML)

		return

	notify_team_joined = f'{update.effective_user.full_name} has joined {game.teams[part_id]}'
	context.bot.send_message(chat_id=update.effective_user.id, text=f'Acknowledged. You are in <b>{game.teams[part_id]}</b>.', reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
	logging.info(f'PARTICIPANT JOINING:{notify_team_joined}')

	#notifies admin of team representatives joining the game
	context.bot.send_message(chat_id=admin, text=notify_team_joined)

	#notifies admin when all team representatives have joined.
	if game.round_no == 0:
		if all(isinstance(i, int) for i in game.teams.keys()):
			context.bot.send_message(chat_id=admin, text=respond.all_joined())
			logging.info('FOR ADMIN: All teams have joined game')

	#Handling mid-game joins as replacement
	else:
		context.bot.send_message(chat_id=update.effective_user.id, text=respond.join_midgame(game.round_no), parse_mode=ParseMode.HTML)
		logging.info(f'PARTICIPANT JOINING: {update.effective_user.full_name} joined Team {game.teams[part_id]} at Round {game.round_no} ')

	if game.round_no > 0 and game.teams[update.effective_user.id].team_no in game.teams_not_played:
		#send the new player current game instructions if he has joined mid-game and previous person has not played x or y
		#X and Y Buttons
		buttons = [[KeyboardButton('X'), KeyboardButton('Y')]]
		ask_for_card = respond.card_req(game.round_no)[0]
		context.bot.send_message(chat_id=update.effective_user.id, reply_markup=ReplyKeyboardMarkup(buttons), text=ask_for_card, parse_mode=ParseMode.HTML)
		logging.info(f'BOT: Asking {update.effective_user.full_name} for X or Y')
	return POLLING


#DONE Make sure that the participant cannot send in repeat answers.
def participant_card_acknowledge(update, context):
	#Don't have to think about what happens if the participants input other things as only X or Y will trigger this function
	global game
	#if game has ended or admin stopped game do nothing
	if not game:
		context.bot.send_message(chat_id=update.effective_user.id, text='There is no game running', reply_markup=ReplyKeyboardRemove())
		return

	logging.info(f'PARTICIPANT CARD: {update.effective_user.full_name}, {game.teams[update.effective_user.id].team_no} played {update.message.text}')

	current_card = game.getcard(game.teams[update.effective_user.id])
	if game.round_no == 0:
		return

	elif game.teams[update.effective_user.id].team_no not in game.teams_not_played:
		context.bot.send_message(chat_id=update.effective_user.id, text=respond.alr_submitted(game.round_no, current_card), parse_mode=ParseMode.HTML)
		return

	#submit to gsheets
	team = game.teams[update.effective_user.id]
	card = update.message.text
	game.submitcard(team, card)
	logging.info('SUBMITTING CARD: Success')

	#appends to teams that play x or y so we know who plays what - for reveal.
	if update.message.text == "X":
		game.teams_that_played['X'].append(update.effective_user.id)
	elif update.message.text == 'Y':
		game.teams_that_played['Y'].append(update.effective_user.id)

	#removes team from not played list
	game.teams_not_played.remove(game.teams[update.effective_user.id].team_no)

	#send acknowledgements
	context.bot.send_message(chat_id=update.effective_user.id, text= respond.acknowledge_play_part(game.round_no, update.message.text), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=admin, text=f'{game.teams[update.effective_user.id]} played {update.message.text}')

	#checks if all teams have played. If so, notify admin
	current_submissions = []
	for team in game.teams.keys():
		current_submissions.append(game.getcard(game.teams[team]))
	if all(current_submissions):
		context.bot.send_message(chat_id=admin, text=respond.ready_to_reveal())

	if game.round_no == 7:
		context.bot.send_message(chat_id=update.effective_user.id, text='You have played your final round. Bot will not be responsive to subsequent inputs.', reply_markup=ReplyKeyboardRemove())

		return STOPPING


def participant_leave_game(update, context):
	global game
	global admin
	if game:
		#DONE send admin text
		#participant leaves the game halfway:
		#Switch the team object reference back to string representation of team number
		#delete reference of game.teams.[userid]
		logging.info(f'LEAVING GAME: {update.effective_user.id}, Team {game.teams[update.effective_user.id].team_no} left game')
		context.bot.send_message(chat_id=admin, text=f'{update.effective_user.full_name}, Team {game.teams[update.effective_user.id].team_no} left game')

		teamNo = str(game.teams[update.effective_user.id].team_no)
		game.teams[teamNo] = game.teams[update.effective_user.id]
		del game.teams[update.effective_user.id]

		context.bot.send_message(chat_id=update.effective_user.id, text=respond.in_game_quit(), reply_markup=ReplyKeyboardRemove())

		return STOPPING

	else:
		#admin cancels game
		#simply leave game back to BEGIN
		context.bot.send_message(chat_id=update.effective_user.id, text=respond.quit_manual_stop(), reply_markup=ReplyKeyboardRemove())
		return BACK


def participant_quit(update, context):
	context.bot.send_message(chat_id=update.effective_user.id, text='Bot will not respond to future inputs until you press /start again.', reply_markup=ReplyKeyboardRemove())
	return STOPPING

#Fallback to notify the person that the command is not recognised
def not_recognised(update, context):
	global admin
	#TODO pls make this more presentable for the user
	update.message.reply_text(f"{update.message.text} - Response not recognised")
	logging.warning(f'BOT: {update.effective_user.full_name} sent \"{update.message.text}\" which the bot does not recognise. There might be an error. Please check log history for this user.')


#To allow the bot to be restarted from within TG - ONLY AVAILABLE TO CALEB YOONG
def stop_and_restart():
    """Gracefully stop the Updater and replace the current process with a new one"""
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)
    logging.warning(f'BOT: Caleb Yoong has restarted the bot.')


def restart(update, context):
    update.message.reply_text('BOT: Bot is restarting...')
    Thread(target=stop_and_restart).start()


def stop(update,context):
	logging.info('BOT: Bot is stopping')
	updater.stop()
	return ConversationHandler.END

def start_bot():
	updater.start_polling()
	logging.info('BOT: Bot started')



def stop_bot():
	logging.info('BOT: Bot is stopping')
	updater.stop()
	logging.info('BOT: Bot has stopped')



updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


dispatcher.add_handler(CommandHandler('r', restart, filters=Filters.user(user_id=218844774)))
dispatcher.add_handler(CommandHandler('ctc', stop, filters=Filters.user(user_id=218844774)))

#Identity of the Admin of current game
admin = None

#game object - none if there is no game running
game = None


BEGIN, ADMIN_STATE, PART_STATE, JOINING, POLLING, BACK, STOPPING, ADMIN, GAME_OPEN_TO_JOIN, PLAYERS_SUBMITTING, REVEALING, GAME_ENDING, ENDGAME = range(13)

#Handles states for Admin
admin_handler = ConversationHandler(
		entry_points=[CommandHandler('confirm', admin_menu)],


		states = {
			ADMIN: [CommandHandler('newgame', admin_new_game)],

            GAME_OPEN_TO_JOIN: [CommandHandler('startgame', admin_start_game)],

			PLAYERS_SUBMITTING: [CommandHandler('reveal', admin_reveal_round_result)],

			REVEALING: [CommandHandler('nextround', admin_increment_round)],

			GAME_ENDING: [CommandHandler('endgame', admin_increment_round)]
		},

		fallbacks = [CommandHandler('stopgame', admin_stop_game), CommandHandler('remove', admin_kick), CommandHandler('help', admin_help), CommandHandler('commands', admin_menu)],

		map_to_parent = {ENDGAME: BEGIN}

)

#Handles states for participant
part_handler = ConversationHandler(
		entry_points = [MessageHandler(Filters.regex('^(Team [1-9]|Team [1][0-2])$'), participant_join_acknowledge)],

		states = {

			POLLING: [MessageHandler(Filters.regex('^(X|Y)$'), participant_card_acknowledge)],

		},
		fallbacks = [CommandHandler('leavegame', participant_leave_game), CommandHandler('quit', participant_quit)],

		map_to_parent = {STOPPING: ConversationHandler.END,
						BACK: BEGIN}
)


#Top level conv handler
conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],


		#states - CURRENT STATE: [MessageHandler(what will trigger the next command), command]
		states = {

			BEGIN: [CommandHandler('makemeadmin', makeMeAdmin),
				CommandHandler('join', participant_query_team)
				],

			ADMIN_STATE:[admin_handler],

			PART_STATE:[part_handler]

		},
		fallbacks = [MessageHandler(Filters.text & (~Filters.command), not_recognised)]
)

dispatcher.add_handler(conv_handler)
dispatcher.add_handler(part_handler)
dispatcher.add_handler(admin_handler)

