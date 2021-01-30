"""

This is where all the text responses come from, so as to not clutter the app.py workspace.


"""

import os
global info_path
current_path = os.path.dirname(__file__)
info_path = f'{current_path}\\info_text'

#start
def start_admin():
    with open(f'{info_path}\\startwadmin.txt') as f:
        msg = f.read()
    return msg

def start_noadmin():
    with open(f'{info_path}\\startnoadmin.txt') as f:
        msg = f.read()
    return msg


#ADMIN COMMANDS
#makemeadmin
def admin_success():
    return 'You have been given the role of admin. \n\nIt is HIGHLY RECOMMENDED that you use either Telegram Web or the Telegram app to facilitate the game. \n\nPress /confirm to confirm.'

def alr_admin():
    return 'You\'re already an admin.'

def admin_taken():
    return "There already is an admin this game."


#admin menu
def admin_menu():
    with open(f'{info_path}\\admin_menu.txt') as f:
        msg = f.read()
    return msg

def admin_help():
    with open(f'{info_path}\\admin_help.txt') as f:
        msg = f.read()
    return msg

#newgame
def newgame_0():
    return "Please include number of teams - eg '/newgame 12' starts a game with 12 teams"

def newgame(no_teams):
    with open(f'{info_path}\\newgame.txt') as f:
        msg = f.read()
    return f'New game with {no_teams} teams have been created! ' + msg

#startgame
def startgame():
    with open(f'{info_path}\\startgame.txt') as f:
        msg = f.read()
    return msg

#reveal
def ready_to_reveal():
    return 'All teams have submitted. Press /reveal to reveal results.'


def reveal(round_no, combi):
    #TODO <b>_a_X _b_Y<b>
    return f'Results of Round {round_no} revealed to participants (<b>{combi[0][0]}X  {combi[1][0]}Y</b>). The gSheet will show all scores. Press /nextround to progress to the next round.'

#round 7 to end game
def round7_over():
    return 'Round 7 over. Press /endgame to reveal all final scores'

#join acknowledge
def all_joined():
    return 'All team representatives have joined. Press /startgame to begin game from round 1.'

#card request - asking for the cards
def card_req(round_no):
    #bonus rounds
    bonus_rounds = {}
    mults = {3: 3, 5: 5, 7: 10}
    for i in mults.keys():
        bonus_rounds[i] = f'<u><b>BONUS ROUND!</b></u> Playing for {mults[i]} times the score! \n\n'

    ask_for_card = f'Round {round_no}: <b>X</b> or <b>Y</b>?'
    admin_round_text= f'Open for submission: Round {round_no} '

    #Bonus Round Notification
    if round_no in [3, 5, 7]:
        ask_for_card = bonus_rounds[round_no] + ask_for_card
        admin_round_text+= f'(x{mults[round_no]})'

    return ask_for_card, admin_round_text

#PARTICIPANT COMMANDS
def join_midgame(round_no):
    return f'Welcome to <i><b>Win as Much as You can!</b></i> You have taken over as representative of your team. The game is currently in Round {round_no}.'

#card_acknowledge
def alr_submitted(round_no, card):
    return f'You have already submitted for Round {round_no}: <b>{card}</b>'

#acknowledge to participant
def acknowledge_play_part(round_no, card):
    return f"Round {round_no}: You have played <b>{card}</b>. \n\nPlease wait while I collate scores from the rest of the teams."

def game_stopped():
    return 'Game has been stopped manually by admin. Please press /leavegame to leave this game.'

#quit game while still running
def in_game_quit():
    return 'You have left the game. You can join again by pressing /start, followed by /join'

#quit game after admin manually stops
def quit_manual_stop():
    return 'You have left the game. You can join again by pressing /join when the new game is set up.'
'''
TO TEST:
- Admin cannot reveal when not all teams have inputted their score. WORKS
- inputting out of range teams WORKS
- double writing for the same round - during the input phase and during the reveal phase WORKS
- quit/leave game +rejoin WORKS
- stopgame WORKS
- admin remove someone and another joins same team WORKS
- new admin info features WORKS
'''
