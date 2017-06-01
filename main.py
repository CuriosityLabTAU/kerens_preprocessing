#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Dataprocessing2 import *

# dict of Experiments : {expr#:(Experiment_date,[Experiment_hours list]),...}
experiments = {"expr1": ('2016_02_05', ['08', '09', '10', '11', '12']), #
               "expr2": ('2016_05_25', ['13','14', '15', '16', '17']), #
               "expr3": ('2017_02_03', ['08','09', '10', '11', '12']), #8-13
               "expr4": ('2017_05_24', ['13','14', '15', '16', '17'])} #14-18
num_tablet = 5
path = "C://%PYTHON_HOME%//kerens//data//Tab"
faculty = ["art", "eng", "exa", "hum", "law", "lif", "man", "med", "soc"]
faculty_en_to_heb = {"art":"תויונמא", "eng":"הסדנה", "exa":"םיקיודמ םיעדמ", "hum":"חורה יעדמ", "law":"םיטפשמ", "lif":"םייחה יעדמ", "man":"לוהינ","med":"תואירבו האופר", "soc":"הרבחה יעדמ"}


amount_of_data, row_data, dict = initial(num_tablet, experiments, path, faculty)
amount_of_data = out_of_data(num_tablet, amount_of_data, experiments,dict)
amount_of_data, dict, check_faculty, check_t0 = build_data_dict(amount_of_data,dict,num_tablet,row_data)  # include checks and CURIOSITY QUESTIONS freeze prints
'''for i in range(num_tablet):
    current_tab = 'Tab' + str(i + 1)
    for file in dict[current_tab].keys():
        if dict[current_tab][file]["experiment"]=="expr3":
            print(file[5:10])'''
total_time,e_m,e_t,e_m_small,total_small,e_m_big,total_big,embr_big,stre_big,embr,stre,faculties_num_small = data_processing(num_tablet,dict,faculty,faculty_en_to_heb)



#graphs(total_time,e_m,e_t,e_m_small,total_small,e_m_big,total_big,embr_big,stre_big,embr,stre,faculties_num_small)
#measures_control(dict,num_tablet,faculty)
create_excel(dict)

'''np,column_titles=create_excel(dict)
for i in column_titles:
    print (i,column_titles.index(i))'''