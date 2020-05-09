import xlsxwriter
import excel2img
import time


start = time.time()

devoirs = ["Devoir 1", "Devoir 2", "Devoir 3", "Devoir 4"]
eleves = {
    "Zeus": {
        "Devoir 1": "Non rendu",
        "Devoir 2": "Le 05/06 à 11h53",
        "Devoir 3": "Non rendu",
        "Devoir 4": "Non rendu"
    },
    "Thanatos": {
        "Devoir 1": "Le 05/06 à 11h53",
        "Devoir 2": "Non rendu",
        "Devoir 3": "Non rendu",
        "Devoir 4": "Non rendu"
    },
    "Doom Slayer": {
        "Devoir 1": "Non rendu",
        "Devoir 2": "Non rendu",
        "Devoir 3": "Non rendu",
        "Devoir 4": "Le 05/08 à 12h53"
    },
    "Araki": {
        "Devoir 1": "Le 05/06 à 11h53",
        "Devoir 2": "Le 05/06 à 11h53",
        "Devoir 3": "Non rendu",
        "Devoir 4": "Le 05/06 à 11h53"
    }
}



workbook = xlsxwriter.Workbook("testmodule.xlsx")
worksheet = workbook.add_worksheet()

hmw_format = workbook.add_format({"bg_color":"#70AD47", "align":"right", "border":1})
recv_header_format = workbook.add_format({"bg_color":"#70AD47", "align":"justify", "border":1})
sended_format = workbook.add_format({"bg_color":"#A9D08E", "align":"right", "border":1})
not_sended_format= workbook.add_format({"bg_color":"#a19e9e", "align":"right", "border":1, "font_color":"#3e3e3e", "italic":"true"})

std_header_format = workbook.add_format({"bg_color":"#5B9BD5", "align":"justify", "border":1})
std_format = workbook.add_format({"bg_color":"#9BC2E6", "align":"justify", "border":1})

worksheet.set_column("A:A", 18)
worksheet.set_column("B:I", 20)

row = 0
col = 0


# Write hmw
for devoir in devoirs:
    col+=1
    worksheet.write(row, col, devoir, hmw_format)
    #worksheet.write(row+1, col, "Rendu", recv_header_format)

col = 0
worksheet.write(row, 0, "Élèves", std_header_format)

for eleve, status in eleves.items():
    col = 0
    row += 1
    worksheet.write(row, col, eleve, std_format)
    for devoir in devoirs:
        col+=1
        if status[devoir] == "" or status[devoir] == "Non rendu":
            worksheet.write(row, col, status[devoir], not_sended_format)
        else:
            worksheet.write(row, col, status[devoir], sended_format)


workbook.close()
excel2img.export_img("testmodule.xlsx","testmodule.png")

print("temps : ", time.time() - start)