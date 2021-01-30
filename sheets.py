import gspread
import time

gc = gspread.service_account(filename='creds.json')
sheetKey = "<insert shet key here>"
wb = gc.open_by_key(sheetKey)

localtime = time.asctime()

newSheetName = f'XY on {localtime}'
worksheet = wb.sheet1
scoreSheet = worksheet.duplicate(insert_sheet_index=1, new_sheet_name=newSheetName)
#make sure you share the spreadsheet with admin first


#Using template, define the cells for each round and team. Returns dictionary w ?x?y as well
def init_scoreboard(no_teams):
	if no_teams < 12:
		scoreSheet.delete_columns(start_index=no_teams+2, end_index=13)

# Reference to where the cells are eg round 1 team 1 card cell

class operator_cells():
	def __init__(self, no_teams):
		self.no_teams = no_teams


	def readcombi(self, round_no):
		coord = self.aXbY_cell(round_no)
		return scoreSheet.cell(coord['r'], coord['c']).value

	def aXbY_cell(self, round_no):
		col = self.no_teams + 2
		row = round_no*2 + 2
		return {'r': row, 'c':col}


	def create_scoring_matrix(self):
		colOffset = 17


		'''
		Updating multiple cells at once requires new list for a new col - gspread interprets
		it as list[r][c]=rowcol.value

		Example:
		We want to update A1:A10
		sheets.update('A1:A10', [[a1val], [a2val], [a3val]...])

		'''
		xMatrix = [[0]]
		for gain in range(1, self.no_teams):
			no_y = self.no_teams - gain
			xMatrix.append([no_y*10])

		xMatrix.append([-10])

		yMatrix = []
		for gain in range(len(xMatrix)):
			yMatrix.append([xMatrix[gain][0]*-1])

		print(yMatrix)
		print(xMatrix)

		x_col = self.no_teams + 6
		y_col = self.no_teams + 7

		xMatrix.reverse()

		xRange = scoring_matrix_range(x_col, xMatrix)
		yRange = scoring_matrix_range(y_col, yMatrix)

		scoreSheet.update(f'{xRange}', xMatrix)
		scoreSheet.update(f'{yRange}', yMatrix)

		aXbY_col = self.no_teams + 5
		aXbY = aXbY_list(self.no_teams)
		aXbYRange = scoring_matrix_range(aXbY_col, aXbY)

		scoreSheet.update(f'{aXbYRange}', aXbY)

		return {'X': xMatrix, 'Y': yMatrix}

"""
Object called team; syntax team(<team_no>(int))

team's cells: team1.<cellType>(<roundno>(int))

"""
class team():
	def __init__(self, team_no):
		self.team_no = team_no

	def __repr__(self):
		return f'Team {self.team_no}'

	def writecard(self, card, round_no):
		cell = self.card_cell(round_no)
		scoreSheet.update_cell(cell['r'], cell['c'], card)


	def readcard(self, round_no):
		cell = self.card_cell(round_no)
		return scoreSheet.cell(cell['r'], cell['c']).value


	def readscore(self, round_no):
		cell = self.score_cell(round_no)
		return scoreSheet.cell(cell['r'], cell['c']).value

	def card_cell(self, round_no):
		rowOffset = 2
		row = round_no*2 + rowOffset
		col = self.team_no + 1

		cell = {'r': row,
		        'c' : col
		}

		return cell

	def score_cell(self, round_no):
		rowOffset = 3
		row = round_no*2 + rowOffset
		col = self.team_no + 1

		cell = {'r': row, 'c': col}

		return cell


def aXbY_list(no_teams):
	aXbY_desc = []
	for n in range(no_teams+1):
		aXbY_desc.append([f'{no_teams-n}X {n}Y'])

	return aXbY_desc


def scoring_matrix_range(col, matrix):
	start = f'{colnum_string(col)}4'
	end = f'{colnum_string(col)}{len(matrix)+3}'

	return(f'{start}:{end}')


def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string



def initialise_sheet(no_teams):
	init_scoreboard(no_teams)
	op = operator_cells(no_teams)
	matrix = op.create_scoring_matrix()
	sheetid = scoreSheet.id
	return op, matrix, sheetid
