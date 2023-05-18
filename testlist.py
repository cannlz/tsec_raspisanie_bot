selectGroup = "rasp_tc"

foldersGroups = {
'rasp_ites': 'ИТЭС',
'rasp_tc': 'ТС',
'rasp_spsipb': 'СПСиПБ',
'rasp_rpco': 'РЦПО',
'rasp_ppkrc': 'ППКРС'
}
if selectGroup in foldersGroups:
    namegroup = foldersGroups[selectGroup]
    print(namegroup)