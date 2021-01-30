import gspread
import time

gc = gspread.service_account(filename='creds.json')
sheetKey = '1Hjlmt2Xe7579b4ym9NkdDEE56T5sW6EwXJQGAF_tUqk'
wb = gc.open_by_key(sheetKey)

worksheet = wb.get_worksheet(0)

worksheet_list = wb.worksheets()

for i in range(1, len(worksheet_list)):
    wb.del_worksheet(worksheet_list[i])
