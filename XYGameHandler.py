import sheets as sh

class Game():
	def __init__(self, no_teams, round_no=0):
		self.no_teams = no_teams
		self.round_no = round_no
		self.teams, self.op, self.scoring_matrix, self.sheetid = self.initialise
		self.x = 0
		self.y = 0
		self.xScore = 0
		self.yScore = 0
		self.teams_that_played = {'X': [], 'Y': []}
		self.teams_not_played = [] 			#use teamno instead of playerid for easier drop in/out implementation

	#Initialises the game, creates new sheet on GSheets and populates team object dict
	@property
	def initialise(self):
		op, scoring_matrix_set, sheetid = sh.initialise_sheet(self.no_teams)

		#scoring_matrix_set is dict in form 'Y': [[0], [-50], [-40]...]
		#hence we need to make into actual list.
		#and the X matrix is reversed due to needing to write to excel.
		scoring_matrix_set['X'].reverse()
		scoring_matrix = {'X': [], 'Y': []}
		for i in range(self.no_teams+1):
			for k in scoring_matrix_set.keys():
				scoring_matrix[k].append(scoring_matrix_set[k][i][0])

		team_dict = {}
		for n in range(1, self.no_teams+1):
			team_dict[str(n)] = sh.team(n)

		return team_dict, op, scoring_matrix, sheetid


	#For some reason, when using team's method, self argument is required.
	#(team)
	def getcard(self, t):
		return t.readcard(self.round_no)


	def getscore(self, t):
		return t.readscore(self.round_no)


	def submitcard(self, t, card):
		t.writecard(card, self.round_no)


	def getcombi(self):
		combi = self.op.readcombi(self.round_no)
		combi_split = combi.split()

		mult = [0, 1, 1, 3, 1, 5, 1, 10]

		#combi_split is ['aX', 'bY']
		self.x = int(combi_split[0][0])
		self.y = int(combi_split[1][0])
		self.xScore = self.scoring_matrix['X'][self.x]*mult[self.round_no]
		self.yScore = self.scoring_matrix['Y'][self.y]*mult[self.round_no]
		return combi_split

