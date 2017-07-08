#!/usr/bin/python
# -*- coding: utf-8 -*-
from path_names import *
import glob, os
import ast
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import operator
import json
from pprint import pprint

unicode_faculty = [unicode(x, 'utf-8') for x in ['תויונמא', 'הרבחה יעדמ', 'םייחה יעדמ', 'תואירבו האופר','הסדנה','חורה יעדמ', 'םיטפשמ', 'לוהינ', 'םיקיודמ םיעדמ']]
unicode_gender = [unicode(x, 'utf-8') for x in ['רכז','הבקנ']]
emotion_list = ['smirk','engagement','surprise','attention','joy','valence', 'smile']

def extract_filename(full_filename):
    parts = full_filename.split('\\')
    return parts[1]

#todo

############################################################################################
####  Initialization- build data structure(reading data from .log files) and row_data   ####
############################################################################################

def initial(num_tablet, experiments,path,faculty):
    row_data = {}
    dict = {}
    dict2 = {}
    amount_of_data = {'out_of_day_per_tab': {},
                      'out_of_hour_per_tab': {},
                      'relevent_data_per_tab': {},
                      'curiosity_questions_not_full_amount': {},
                      'curiosity_questions_is_empty': {}}


    for i in range(num_tablet):
        current_tab = 'Tab'+str(i+1)
        row_data[current_tab]={}
        dict[current_tab] = {}
        # os.chdir(path+str(i+1))      #change the current working directory to the given path
        tab_path = path+str(i+1) + '/'
        all_log_files = glob.glob(tab_path + "*.log")

        for file in glob.glob(tab_path + "*.log"):        #glob.glob returns a list of path names that match the .log ending
            file= str(file)
            dict[current_tab][file]= { "experiment": None,
                                       "out_of_data": "",
                                       "personal_info":
                                           {"gender": "-1",
                                            "email": -1,
                                            "faculty": "-1",
                                            "age": -1},
                                       "buttons":{},
                                       "t0": -1,
                                       "wav": {},
                                       "listen_t": {},
                                       "list_fac":
                                           {"art": 0, "eng": 0, "exa": 0, "hum": 0, "law": 0, "lif": 0, "man": 0, "med": 0,
                                            "soc": 0},
                                       "curiosity_ques":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                       "curiosity_ques_stre": -1,
                                       "curiosity_ques_embr": -1,
                                       "learning_ques": {"questions":[],"ques-time":[] ,"learning %":-1},
                                       'trans_matrix':
                                                        {'count':0,
                                                         'prop':0,
                                                         'e_trans':0,},
                                         "wav_sorted":{},
                                         "fac_heard":
                                                        {"art":0,"eng":0,"exa":0,"hum":0,"law":0,"lif":0,"man":0,"med":0,"soc":0},
                                         "e_multidis":0,
                                         "faces":-1}

            # data = open(path+str(i+1)+"/"+str(file), 'r')
            data = open(str(file), 'r')
            data1=ast.literal_eval(data.readline())

            #evaluate an expression node/Unicode/Latin-1 encoded string
                                                    # containing a Python literal or container display

            for key in data1.keys():
                if key[5:10] == "02_03" or key[5:10] == '05_24':
                    data1[key]["data"] = json.loads(data1[key]["data"])['log'] #ast.literal_eval(data1[key]["data"])["log"]
                    #print(data1[key]["data"],"expr3")
                else:
                    data1[key]["data"] = json.loads(data1[key]["data"]) #ast.literal_eval(data1[key]["data"])
                    #print(data1[key]["data"],"expr1-2")

            row_data[current_tab][file] = data1
    return amount_of_data,row_data,dict



############################################################################
####            Mark out of data files according to date              ######
############################################################################
def out_of_data(num_tablet,amount_of_data,experiments,dict):
    file_start = len(path) + 2          # removes also tablet number and //
    for i in range(num_tablet):
        current_tab = 'Tab'+str(i+1)
        amount_of_data['relevent_data_per_tab'][current_tab] = {}
        amount_of_data['out_of_day_per_tab'][current_tab] = {}
        amount_of_data['out_of_hour_per_tab'][current_tab] = {}
        amount_of_data['curiosity_questions_not_full_amount'][current_tab] = {}
        amount_of_data['curiosity_questions_is_empty'][current_tab] = {}

        for expr in experiments:
            amount_of_data['relevent_data_per_tab'][current_tab][expr] = 0
            amount_of_data['out_of_day_per_tab'][current_tab][expr] = 0
            amount_of_data['out_of_hour_per_tab'][current_tab][expr] = 0
            amount_of_data['curiosity_questions_not_full_amount'][current_tab][expr] = 0
            amount_of_data['curiosity_questions_is_empty'][current_tab][expr] = 0

        for file in dict[current_tab].keys():

            #### OUT OF DATA dict[current_tab][file]['out_of_data']=
            for expr in experiments:
                if file[file_start:(file_start+10)] == experiments[expr][0]:
                    if (file[(file_start+11):(file_start+13)] in experiments[expr][1]):
                        amount_of_data['relevent_data_per_tab'][current_tab][expr] += 1

                        #### EXPERIMENT dict[current_tab][file]['experiment']=
                        dict[current_tab][file]["experiment"] = expr
                    else:
                        dict[current_tab][file]["out_of_data"] = "not at hour"
                        amount_of_data['out_of_hour_per_tab'][current_tab][expr] += 1

            if not dict[current_tab][file]["experiment"] and not dict[current_tab][file]["out_of_data"]:
                dict[current_tab][file]["out_of_data"] = "not at day"
                amount_of_data['out_of_day_per_tab'][current_tab][expr] +=1
    return amount_of_data

############################################################################
####   from ROW to Relevent information, filling the DATA Dictionary    ####
############################################################################
def build_data_dict(amount_of_data,dict,num_tablet,row_data):
    check_faculty = []
    check_t0 = []
    count=1
    amount_of_data['gender'] = {}
    amount_of_data['email'] = {}
    amount_of_data['faculty'] = {}
    amount_of_data['age'] = {}
    path2_face_expression = analysis_path + "affectiva_subject_stats.json"
    with open(path2_face_expression) as face_data:
        faces_data = json.load(face_data)
    #pprint(faces_data)

    for i in range(num_tablet):
        current_tab = 'Tab' + str(i + 1)
        amount_of_data['gender'][current_tab] = []
        amount_of_data['faculty'][current_tab] = []
        amount_of_data['email'][current_tab] = {}
        amount_of_data['age'][current_tab] = {}
        for file in dict[current_tab].keys():


            amount_of_data['email'][current_tab][file] = []
            amount_of_data['age'][current_tab][file] = []
            #if not dict[current_tab][file]["out_of_data"]: check only for OUT OF DATES with date reason and not quality reasons,
                                                            # in the following part, will also add out of data from other reasons like
                                                            # not fully answered curiosity_questions
            try:
                dict[current_tab][file]["faces"] = faces_data[current_tab.lower()][extract_filename(file)]
                #print (dict[current_tab][file],count)
                count+=1
            except:
                pass

            for key in row_data[current_tab][file].keys():
                current_value=row_data[current_tab][file][key]
                #print(current_value['data']['obj'])

                #### GENDER dict[current_tab][file]["personal_info"]['gender']=
                try:
                    if current_value['data']['obj'] in ['gender']:
                        if current_value['data']['comment'] in unicode_gender: # to prevent "pos": "(x,y)" comments
                            amount_of_data['gender'][current_tab].append(current_value['data']['comment'])
                            dict[current_tab][file]["personal_info"]['gender'] = current_value['data']['comment']
                except:
                    print(file,"gender")
                #### EMAIL dict[current_tab][file]["personal_info"]['email']=
                ## keeps a list of tuples (time stamp,email), will chose the relevent according to latest time stamp

                try:
                    if current_value['data']['obj'] in ['email']:
                         time=datetime.strptime(current_value['data']['time'], '%Y_%m_%d_%H_%M_%S_%f')
                         amount_of_data['email'][current_tab][file].append((time,current_value['data']['comment']))
                        #print(current_value['data']['comment'],file)
                except:
                    print(file,"email")


                #### FACULTY dict[current_tab][file]["personal_info"]['faculty']=
                try:
                    if current_value['data']['obj'] in ["faculty"]:
                        if current_value['data']['comment'] in unicode_faculty:
                            #print(current_value['data']['comment'])
                            dict[current_tab][file]["personal_info"]['faculty'] = current_value['data']['comment']
                            if dict[current_tab][file]["experiment"]== "expr2":
                                check_faculty.append((file,current_tab,dict[current_tab][file]["experiment"],current_value['data']['comment']))
                except:
                    print(file,"faculty")

                #### AGE dict[current_tab][file]["personal_info"]['age']=
                ## keeps a list of tuples (time stamp,age), will chose the relevent according to latest time stamp
                try:
                    if current_value['data']['obj'] in ['age']:
                        time = datetime.strptime(current_value['data']['time'], '%Y_%m_%d_%H_%M_%S_%f')
                        amount_of_data['age'][current_tab][file].append((time, current_value['data']['comment']))
                except:
                    print(file,"age")


                #### BUTTONS dict[current_tab][file]['buttons']=
                try:
                    if current_value['data']['obj'] in ['consent_button','consent_checkbox','final_button']:
                        time = datetime.strptime(current_value['data']['time'], '%Y_%m_%d_%H_%M_%S_%f')
                        time2 = datetime.strptime( key, '%Y_%m_%d_%H_%M_%S_%f')
                        dict[current_tab][file]["buttons"][current_value['data']['obj']] = time
                        dict[current_tab][file]["buttons"][current_value['data']['obj']+str(2)] = time2 # capture the key as time stamp
                except:
                    print(file,"buttons")

                #### TO dict[current_tab][file]['t0']=
                try:
                    if current_value['data']['obj'] in ['t0']:
                        t0_times = current_value['data']['comment'].split(',')
                        dict[current_tab][file]["t0"] = datetime.strptime(t0_times[1], '%Y_%m_%d_%H_%M_%S_%f') - datetime.strptime(t0_times[0], '%Y_%m_%d_%H_%M_%S_%f')
                        check_t0.append((file, current_tab, dict[current_tab][file]["experiment"], time))
                        #print(dict[current_tab][file]["t0"],"from log", file)
                        #print(file, dict[current_tab][file]['t0'])

                except:
                    print(file,"t0")

                #### PLAYING TIME dict[current_tab][file]["wav"]= (wav_full_name.WAV: [("play",play_time),("stop",stop_time)...]
                ## first part - saving playing and stop time
                try:
                    if current_value['data']['obj'].lower() in ["art","eng","exc","hum","law","life","man","med","soc"]:
                        if "pos" not in current_value['data']['comment']:
                            if current_value['data']['obj'].lower()=="life":
                                current_value['data']['obj']="lif"
                            if current_value['data']['obj'].lower()=="exa":
                                current_value['data']['obj']="exc"
                            if current_value['data']['comment'].lower() in dict[current_tab][file]['wav'].keys():
                                #print( current_value['data']['comment'])
                                dict[current_tab][file]['wav'][current_value['data']['comment'].lower()].append((
                                    current_value['data']['action'],current_value['data']['time']))
                            else:
                                dict[current_tab][file]['wav'][current_value['data']['comment'].lower()] = []
                                dict[current_tab][file]['wav'][current_value['data']['comment'].lower()].append((
                                    current_value['data']['action'],current_value['data']['time']))
                except:
                    print(file,"playing time")
                #### CURIOSITY QUESTIONS dict[current_tab][file]['"curiosity_ques"']=[0,0,0,0,0,0,0,0,0,0]
                try:
                    if "q" in current_value['data']['obj']:
                        ques = int(current_value['data']['obj'][1:3])
                        ans = current_value['data']['obj'][7]
                        dict[current_tab][file]['curiosity_ques'][ques-1]=ans
                except:
                    print(file,"questions")

                #### LEARNING QUESTIONS dict[current_tab][file]["learning_ques"]: {"questions":[],(_,_),(_,_)}
                try:
                    if "correct" in current_value['data']['obj'] or "wrong" in current_value['data']['obj']:
                        if current_value['data']['obj'] not in dict[current_tab][file]["learning_ques"]["questions"]:
                            dict[current_tab][file]["learning_ques"]["questions"].append(current_value['data']['obj'])
                            dict[current_tab][file]["learning_ques"]["ques-time"].append(
                                (datetime.strptime(current_value['data']['time'], '%Y_%m_%d_%H_%M_%S_%f'),current_value['data']['obj'].split(",")[0],current_value['data']['obj'].split(",")[1]))
                            dict[current_tab][file]["learning_ques"]["ques-time"] = sorted(dict[current_tab][file]["learning_ques"]["ques-time"], key=lambda x: x[0])
                except:
                    print(file,"LEARNING")

            #### EMAIL and AGE #2, needs a special process cause the data is saved every time typing
            #    for Exmaple : 1. ker 2. keren.bentob 3. keren.bentov@gmai 4. keren.bentov@gmail.com
            #    or: 1. 2   2. 27      3. 2      4. 28
            #    so we will save only the one with the latest time stamp

            amount_of_data['email'][current_tab][file]=sorted(amount_of_data['email'][current_tab][file], key=lambda x: x[0])

            if len(amount_of_data['email'][current_tab][file]) > 0:
                if "@" in amount_of_data['email'][current_tab][file][-1][1]:
                    amount_of_data['email'][current_tab][file]=amount_of_data['email'][current_tab][file][-1][1]
                    dict[current_tab][file]["personal_info"]['email']=amount_of_data['email'][current_tab][file]
                else:
                    amount_of_data['email'][current_tab][file]=""
            else:
                amount_of_data['email'][current_tab][file] = ""


            amount_of_data['age'][current_tab][file] = sorted(amount_of_data['age'][current_tab][file], key=lambda x: x[0])

            if len(amount_of_data['age'][current_tab][file]) > 0:
                if "pos" not in amount_of_data['age'][current_tab][file][-1][1]:
                    amount_of_data['age'][current_tab][file] = amount_of_data['age'][current_tab][file][-1][1]
                    dict[current_tab][file]["personal_info"]['age'] = amount_of_data['age'][current_tab][file]
                else:
                    amount_of_data['age'][current_tab][file] = "" #???
            else:
                amount_of_data['age'][current_tab][file] = ""


            #### PLAYING TIME #2   dict[current_tab][file]["listen_t"]= (wav, time delta between Stop and Play)
                                  #dict[current_tab][file]["list_fac"]["fac"]= total listening time per faculty
            ## second part - calculating the delta for each wav and also saving total listening time per faulty
            ## remove # to print and check
            for wav in dict[current_tab][file]['wav'].keys():
                if len(dict[current_tab][file]['wav'][wav]) == 2:
                    for p_s in dict[current_tab][file]['wav'][wav]:
                        if p_s[0] == "stop":
                            stop_t = datetime.strptime(p_s[1], '%Y_%m_%d_%H_%M_%S_%f')
                            #print(wav,"stop",stop_t)
                        elif p_s[0] == "play":
                            play_t = datetime.strptime(p_s[1], '%Y_%m_%d_%H_%M_%S_%f')
                            #print(wav,"play",play_t)
                    dict[current_tab][file]['listen_t'][wav.lower()] = stop_t - play_t
                    #print(wav,"['listen_t'][wav]",dict[current_tab][file]['listen_t'][wav])
                    dict[current_tab][file]["list_fac"][wav[6:9].lower()] += (stop_t - play_t).seconds
                    #print(wav[6:9],"[list_fac][wav[6:9]",dict[current_tab][file]["list_fac"][wav[6:9]])
                #else:
                    #print("less then 2",dict[current_tab][file]['wav'][wav])


            #### CURIOSITY & LEARNING QUESTIONS  #2    dict[current_tab][file]["curiosity_ques_stre"]=  /   dict[current_tab][file]["curiosity_ques_embr"]=
            if len(dict[current_tab][file]["learning_ques"]["ques-time"])>1:
                orig=dict[current_tab][file]["learning_ques"]["ques-time"]
            for i in dict[current_tab][file]["learning_ques"]["ques-time"]:
                for j in dict[current_tab][file]["learning_ques"]["ques-time"]:
                    if i[2]==j[2] and i[0]!=j[0]:
                        if i[0]>j[0]:
                            dict[current_tab][file]["learning_ques"]["ques-time"].remove(j)
                            #print(i, j, "2nd should bye")
                            #print(orig)

                        else:
                            dict[current_tab][file]["learning_ques"]["ques-time"].remove(i)
                            #print(i,j,"first should bye")
                            #print(orig)
            correct=0
            if dict[current_tab][file]["learning_ques"]["ques-time"]:
                for i in dict[current_tab][file]["learning_ques"]["ques-time"]:
                    if i[1]=="correct":
                        #print(i)
                        correct+=1
                dict[current_tab][file]["learning_ques"]["learning %"] = float(correct)/ float(len(dict[current_tab][file]["learning_ques"]["ques-time"]))



            dict[current_tab][file]["curiosity_ques_embr"] = sum(
                                                            int(dict[current_tab][file]['curiosity_ques'][j]) for j in [1, 3, 5, 7, 9])
            dict[current_tab][file]["curiosity_ques_stre"] = sum(
                                                            int(dict[current_tab][file]['curiosity_ques'][j]) for j in [0, 2, 4, 6, 8])

            #BFI_sign = [1,1,1,1,1,1,-1,1,-1,1]
            dict[current_tab][file]["BFI"] = -1

            for j in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                if dict[current_tab][file]['curiosity_ques'][j]!=0:
                    if j==16 or j==18:
                        dict[current_tab][file]["BFI"] += 6-float(dict[current_tab][file]['curiosity_ques'][j])
                        #print("-1",dict[current_tab][file]["BFI"],float(dict[current_tab][file]['curiosity_ques'][j]),file)
                    else:
                        dict[current_tab][file]["BFI"] += float(dict[current_tab][file]['curiosity_ques'][j])
                        #print("1", dict[current_tab][file]["BFI"],float(dict[current_tab][file]['curiosity_ques'][j]),file)
            if dict[current_tab][file]["BFI"] != -1:
                dict[current_tab][file]["BFI"] -= 10.0
                dict[current_tab][file]["BFI"] /= 40.0
                #print("tot", dict[current_tab][file]["BFI"],file)

            #print("embr", dict[current_tab][file]["curiosity_ques_embr"], "stre",
                #dict[current_tab][file]["curiosity_ques_stre"])

    # check CURIOSITY QUESTIONS list is full (has all answers), if not mark as out of data - but how come???

    for i in range(num_tablet):
        current_tab = 'Tab' + str(i + 1)
        for file in dict[current_tab]:
            c = 0
            for ques in dict[current_tab][file]["curiosity_ques"]:
                if ques!=0:
                    c+=1
            if c!=10 and c!=0 :
                dict[current_tab][file]["out_of_data"] = "curiosity_questions_not_full_amount, 1-9"
                if dict[current_tab][file]['experiment'] is not None:
                    amount_of_data['curiosity_questions_not_full_amount'][current_tab][dict[current_tab][file]['experiment']] += 1
                #print(row_data[current_tab][file])
            if dict[current_tab][file]['experiment']:
                if c==0:
                    dict[current_tab][file]["out_of_data"]="curiosity_questions_is_empty, 0"
                    if dict[current_tab][file]['experiment'] is not None:
                        amount_of_data['curiosity_questions_is_empty'][current_tab][dict[current_tab][file]['experiment']] +=1
                    #print(row_data[current_tab][file])
    #for key in amount_of_data:
        #if key=='curiosity_questions_not_full_amount' or key=='curiosity_questions_is_empty':
            #print(key,amount_of_data[key])
    # check why only 28 files has T0, also what are 2 time in comment - first screen to first touch?
    # for t0 in check_t0:
    #     print("t0",t0,len(check_t0))
    #     print("t0",t0,len(check_t0))

    return amount_of_data, dict, check_faculty, check_t0


############################################################################
####                   Processing Data into Measures                    ####
############################################################################
def data_processing(num_tablet,dict,faculty,faculty_en_to_heb ):
    # calculating the Total listening time per file dict[current_tab][file]["listen_t"]["tot"]=
    total_time = []
    e_multi_matrix = []
    for k, v in dict.items():
        for participant, value in v.items():
            t_time = 0
            for wav,t in value['listen_t'].items():

                t_time += t.seconds
            value['listen_t']["tot"] = t_time
            total_time.append(t_time)
    total_time = np.array(total_time)



    ####  E_MULTIDIS dict[current_tab][file]["fac_prop"}= {"art":0,"eng":0...}

    # prop per file and faculty
    for k, v in dict.items():
        for participant, value in v.items():
            for fac,p in value["fac_heard"].items():
                if value['listen_t']["tot"]!=0:
                    value["fac_heard"][fac]=value['list_fac'][fac]

    # calculating the Entropy(Multi Dis)  dict[current_tab][file]["e_multidis"}=
    e_m =[]
    for k, v in dict.items():
        for participant, value in v.items():
            number_heard = 0
            for fac,h in value["fac_heard"].items():
                if h!=0:
                    p = h /float(value['listen_t']["tot"])
                    #print((np.log2(p))*p)
                    value["e_multidis"] -=  (np.log2(p))*p
                    number_heard += 1
            #print("ch",(-1)*value["e_multidis"])
            # --- calculate normalization = equal hearing of all parts -------
            # --- norm_entropy ==> high heard all, low heard the same
            if number_heard < 2:
                value["e_multidis"] = 0.0
            else:
                p_normalization = 1.0 / float(number_heard)
                normalization = -np.log2(p_normalization)
                value["e_multidis"]= (value["e_multidis"] / normalization)
            e_m.append(value["e_multidis"])
    e_m = np.array(e_m)

    #print(len(e_m),'e_multidis',e_m)


    # adding to dict[file] a sorted dict prepration with play_time:wav for each 'play', dict[current_tab][file]["wav_sorted"]={}
    for i in range(num_tablet):
        current_tab = 'Tab' + str(i + 1)
        for file in dict[current_tab].keys():
            for wav in dict[current_tab][file]['wav'].keys():
                for p_s in dict[current_tab][file]['wav'][wav]:
                    if p_s[0]=="play":
                        #print(dict[current_tab][file]['wav'][wav],p_s[1],wav[6:9],wav)
                        dict[current_tab][file]['wav_sorted'][datetime.strptime(p_s[1],'%Y_%m_%d_%H_%M_%S_%f')]=wav[6:9]


    x = [["" for i in range(10)] for j in range(945)]
    r=0
    subject_with_faculty=0
    subject_with_faculty_equal_1st_wav = 0
    #the sorting step
    for i in range(num_tablet):
        current_tab = 'Tab' + str(i + 1)
        for file in dict[current_tab].keys():
            if dict[current_tab][file]['wav_sorted']:
                #print("before")
                #print(dict[current_tab][file]['wav_sorted'])
                #print("type_before")
                #print(type(dict[current_tab][file]['wav_sorted']))
                dict[current_tab][file]['wav_sorted']=sorted(dict[current_tab][file]['wav_sorted'].items(),key=operator.itemgetter(0)) # seconds - problems with seconds
                #dict[current_tab][file]["t0"] =datetime.strptime(dict[current_tab][file]['wav_sorted'][0][0], '%Y_%m_%d_%H_%M_%S_%f') - datetime.strptime(dict[current_tab][file]['buttons']['consent_button'], '%Y_%m_%d_%H_%M_%S_%f')
                if dict[current_tab][file]['buttons'] and dict[current_tab][file]["t0"] == -1:

                    dict[current_tab][file]["t0"] = dict[current_tab][file]['wav_sorted'][0][0] - \
                                                    dict[current_tab][file]['buttons']['consent_button']
                    #print(dict[current_tab][file]['experiment'],dict[current_tab][file]['wav_sorted'][0][0],dict[current_tab][file]['buttons']['consent_button'], "T0")
                    #print(dict[current_tab][file]["t0"], "consent_button", file)
                    #print(file,dict[current_tab][file]["t0"],"t0")
                #wav_sorted2 contain just the Fac name [eng,med,exa..]
                dict[current_tab][file]['wav_sorted2'] = []
                for wav in dict[current_tab][file]['wav_sorted']:
                    dict[current_tab][file]['wav_sorted2'].append(wav[1])
                dict[current_tab][file]['first_wav_faculty']=dict[current_tab][file]['wav_sorted2'][0]
                #print( faculty_en_to_heb[dict[current_tab][file]['first_wav_faculty']], dict[current_tab][file]['personal_info']['faculty'])
                if dict[current_tab][file]['personal_info']['faculty'] != -1:
                    subject_with_faculty+=1

                '''if faculty_en_to_heb[dict[current_tab][file]['first_wav_faculty']] == dict[current_tab][file]['personal_info']['faculty']:
                    dict[current_tab][file]['first_faculty_is_the_same'] = 1
                    subject_with_faculty_equal_1st_wav+=1
                else:
                    dict[current_tab][file]['first_faculty_is_the_same'] = 0'''
                #print(dict[current_tab][file]['first_faculty_is_the_same'], faculty_en_to_heb[dict[current_tab][file]['first_wav_faculty']], dict[current_tab][file]['personal_info']['faculty'])

                c = 0
                for y in (dict[current_tab][file]['wav_sorted2']):
                    #print(file,c,r,y)
                    x[r][c] = y
                    c+=1
                r+=1


    print("subject_with_faculty",subject_with_faculty)
    print("subject_with_faculty_equal_1st_wav",subject_with_faculty_equal_1st_wav)
    # print("% subject_with_faculty_equal_1st_wav/subject_with_faculty",subject_with_faculty_equal_1st_wav/subject_with_faculty)

    x = np.matrix(x)
    #x = e_multi_matrix
    #print(len(x))

   # for i in x:
   #     print(len(i))
    print(x.shape)
    #print(x[0])
    #print(x)
    #print(len(x))
    #print(len(x[0]))

    #np.savetxt("C://Users//kerenbt//Downloads//%PYTHON_HOME%//projects//open_day_2//multi.csv", np.matrix(e_multi_matrix),'%s', delimiter=",")


    ####  E_TRANSE dict[current_tab][file]["trans_matrix"}=

    # calculating the Entropy(transfers matrix) dict[current_tab][file]["trans_matrix"]["count"}=
                                                #dict[current_tab][file]["trans_matrix"]["prop"}=

    n_of_more_than_4_wavs=0
    for i in range(num_tablet):
        current_tab = 'Tab'+str(i+1)
        for file in dict[current_tab].keys():
            y = np.zeros((len(faculty),len(faculty)))
            num_transitions = 0
            for r in range(1,len(dict[current_tab][file]['wav_sorted'])):
                #print("sorted wav for participant:")
                #print(dict[current_tab][file]['wav_sorted'])
                #print("the trans step:",r,"to-",r+1)
                #print(faculty)
                f=list(dict[current_tab][file]['wav_sorted'])[r-1][1]
                s=list(dict[current_tab][file]['wav_sorted'])[r][1]
                #print("the trans faculties:")
                #print(f,s)
                #print("and indexes:")
                #print(faculty.index(f),faculty.index(s))
                #print(y,"before")
                y[faculty.index(list(dict[current_tab][file]['wav_sorted'])[r-1][1]),faculty.index(list(dict[current_tab][file]['wav_sorted'])[r][1])] += 1
                num_transitions += 1
                #print(y,'after')
            dict[current_tab][file]['trans_matrix']['count'] = y
            dict[current_tab][file]['trans_matrix']['num_transitions'] = num_transitions
            sum_y=np.sum(y)
            if sum_y>4:
                n_of_more_than_4_wavs+=1
            # CHANGED
            if num_transitions > 1:
                dict[current_tab][file]['trans_matrix']['prop'] = np.divide(y,sum_y)
            else:
                dict[current_tab][file]['trans_matrix']['prop'] = None
            #print(file,dict[current_tab][file]['trans_matrix']['count'],dict[current_tab][file]['trans_matrix']['prop'])

    e_t = []
    total_small = []
    total_big = []
    e_m_small = []
    e_m_big = []
    embr=[]
    stre=[]
    embr_big=[]
    stre_big=[]
    n_q=0
    faculties_num_small=[]

    for i in range(num_tablet):
        current_tab = 'Tab'+str(i+1)
        for file in dict[current_tab].keys():
            sum_prop = 0
            if dict[current_tab][file]["listen_t"]["tot"]!=0:
                total_big.append(dict[current_tab][file]["listen_t"]["tot"])
                e_m_big.append(dict[current_tab][file]["e_multidis"])
            if dict[current_tab][file]["curiosity_ques_embr"] \
                    and dict[current_tab][file]["curiosity_ques_stre"] \
                    and dict[current_tab][file]["curiosity_ques_embr"]!=0 \
                    and dict[current_tab][file]["curiosity_ques_stre"]!=0:
                n_q+=1
                stre_big.append(dict[current_tab][file]["curiosity_ques_stre"])
                embr_big.append(dict[current_tab][file]["curiosity_ques_embr"])
            if dict[current_tab][file]['trans_matrix']['prop'] is not None: #had more than 3 wavs
                for x in np.nditer(dict[current_tab][file]['trans_matrix']['prop']):
                    if x!=0:
                        sum_prop -=  (np.log2(x))*(x)
                # --- normalization of transition matrix = log2(1/num_transitions) ---
                # --- norm_entropy ==> high all transitions (chaos), low very ordered
                p_normalization = 1.0 / float(dict[current_tab][file]['trans_matrix']['num_transitions'])
                normalization = -np.log2(p_normalization)
                dict[current_tab][file]['trans_matrix']['e_trans']= sum_prop / normalization
                faculties_num=0
                for x in dict[current_tab][file]['fac_heard']:  #check how many diffrent faculties wav has benn listened
                    if dict[current_tab][file]['fac_heard'][x]>0:
                        faculties_num+=1
                faculties_num_small.append(np.log2(faculties_num))
                total_small.append(dict[current_tab][file]["listen_t"]["tot"])
                e_m_small.append(dict[current_tab][file]["e_multidis"])
                stre.append(dict[current_tab][file]["curiosity_ques_stre"]) #even for embracing and odd for stretching
                embr.append(dict[current_tab][file]["curiosity_ques_embr"])
                e_t.append((-1)*sum_prop)
    #########print('n_of_more_than_4_wavs',n_of_more_than_4_wavs,'n_q',n_q)
    return (total_time,e_m,e_t,e_m_small,total_small,e_m_big,total_big,embr_big,stre_big,embr,stre,faculties_num_small)


############################################################################
####                       Measures_Control                             ####
############################################################################

def measures_control(dict,num_tablet,faculty):
    dict2=dict
    z= []
    n_of_more_than_4_wavs = 0

    for i in range(num_tablet):
        current_tab = 'Tab' + str(i + 1)

    for file in dict2[current_tab].keys():
            dict2[current_tab][file]['trans_matrix']['e_trans_100'] = []
            for i in range(100):
                #print("before")
                #print(dict2[current_tab][file]["wav_sorted"])
                #print(dict[current_tab][file]["wav_sorted"])
                if len(dict[current_tab][file]["wav_sorted"]) != 0:
                    dict2[current_tab][file]["wav_sorted"] = np.random.permutation(dict[current_tab][file]["wav_sorted"])

                #print("after")
                #print(dict2[current_tab][file]["wav_sorted"])

                y = np.zeros((len(faculty), len(faculty)))
                for r in range(1, len(dict2[current_tab][file]['wav_sorted'])):
                    y[faculty.index(list(dict2[current_tab][file]['wav_sorted'])[r - 1][1]), faculty.index(
                        list(dict2[current_tab][file]['wav_sorted'])[r][1])] += 1
                dict2[current_tab][file]['trans_matrix']['count'] = y
                sum_y = np.sum(y)
                if sum_y > 4:
                    n_of_more_than_4_wavs += 1
                    dict2[current_tab][file]['trans_matrix']['prop'] = np.divide(y, sum_y)

                sum_prop = 0
                if type(dict2[current_tab][file]['trans_matrix']['prop']) != int:  # had more than 3 wavs
                    for x in np.nditer(dict2[current_tab][file]['trans_matrix']['prop']):
                        if x != 0:
                            sum_prop += (np.log2(x)) * (x)
                    dict2[current_tab][file]['trans_matrix']['e_trans_100'].append((-1) * sum_prop)
            if type(dict2[current_tab][file]['trans_matrix']['prop']) != int:
                if np.std(dict2[current_tab][file]['trans_matrix']['e_trans_100']) !=0 :
                    dict2[current_tab][file]['trans_matrix']["z_value"]= (dict2[current_tab][file]['trans_matrix']['e_trans']-
                                                                          np.mean(dict2[current_tab][file]['trans_matrix']['e_trans_100']))/np.std(dict2[current_tab][file]['trans_matrix']['e_trans_100'])
                    z.append(dict2[current_tab][file]['trans_matrix']["z_value"])

                #print("mean",np.mean(dict2[current_tab][file]['trans_matrix']['e_trans_100']))
                #print("std",np.std(dict2[current_tab][file]['trans_matrix']['e_trans_100']))
                #print(dict2[current_tab][file]['trans_matrix']['z_value'])


                '''print(file)
                print("e_trans_100")
                print(dict2[current_tab][file]['trans_matrix']['e_trans_100'])
                print("e_trans")
                print(dict2[current_tab][file]['trans_matrix']['e_trans'])
                print("z_value")
                print(dict2[current_tab][file]['trans_matrix']['z_value'])'''
    #print("n_of_more_than_4_wavs",n_of_more_than_4_wavs/100)
    ###########print("z_e_trans",z)
    ###########print("lenz z_e_trans",len(z))

    #######################################
    #####  HIST - Z value  #####
    #######################################
    n, bins, patches = plt.hist(z, bins=20)
    plt.xlabel('z value for e_trans')
    plt.show()

'''print(file)
print(dict2[current_tab][file]["out_of_data"],"o_o_data")
print("wav_sorted")
print(dict[current_tab][file]["wav_sorted"])
print("wav_sorted2")
print(dict2[current_tab][file]["wav_sorted"])'''

def graphs(total_time,e_m,e_t,e_m_small,total_small,e_m_big,total_big,embr_big,stre_big,embr,stre,faculties_num_small):
    #######################################
    #####  HIST - tot listening time  #####
    #######################################
    n, bins, patches = plt.hist(total_time)
    plt.xlabel('tot listening time')
    plt.show()

    #######################################
    #####      HIST - e_multidis      #####
    #######################################
    n, bins, patches = plt.hist(e_m)
    plt.xlabel('e_multidis')
    plt.show()

    #######################################
    #####        HIST - e_trans       #####
    #######################################
    e_t = np.array(e_t)
    #print(len(e_t),'e_trans')
    n, bins, patches = plt.hist(e_t,8)
    plt.xlabel('e_trans')
    plt.show()

    ##############################################################
    #####  e_trans VS e_multi(small - only more_than_4_wavs) #####
    ##############################################################
    plt.plot(e_t,e_m_small,'ro')
    plt.xlabel('e_trans')
    plt.ylabel('e_multi')
    plt.show()

    ##########################################################################
    ##### e_trans VS total listening time(small - only more_than_4_wavs) #####
    ##########################################################################
    plt.plot(e_t,total_small,'ro')
    plt.xlabel('e_trans')
    plt.ylabel('tot listening time')
    plt.show()


    #########################################################################
    #### e_multi VS total listening time(all, not only more_than_4_wavs) ####
    #########################################################################
    plt.plot(e_m_big,total_big,'ro')
    plt.xlabel('e_multi')
    plt.ylabel('tot listening time')
    plt.show()


    #########################################################################
    #### embracing_all VS stretching_all(all, not only more_than_4_wavs) ####
    #########################################################################
    plt.plot(embr_big,stre_big,'ro')
    plt.xlabel('embracing_all')
    plt.ylabel('stretching_all')
    plt.show()

    ########################################################
    #### embracing VS stretching(only more_than_4_wavs) ####
    ########################################################
    plt.plot(embr,stre,'ro')
    plt.xlabel('embracing')
    plt.ylabel('stretching')
    plt.show()

    #########################################################################
    #### embracing VS tot listening time(small - only more_than_4_wavs)  ####
    #########################################################################

    plt.plot(embr,total_small,'ro')
    plt.xlabel('embracing')
    plt.ylabel('tot listening time')
    plt.show()

    #########################################################################
    #### stretching VS tot listening time(small - only more_than_4_wavs)  ###
    #########################################################################
    plt.plot(stre,total_small,'ro')
    plt.xlabel('stretching')
    plt.ylabel('tot listening time')
    plt.show()

    ##############################################################
    #### embracing VS e_multi(small - only more_than_4_wavs)  ####
    ##############################################################
    plt.plot(embr,e_m_small,'ro')
    plt.xlabel('embracing')
    plt.ylabel('e_m_small')
    plt.show()

    ##############################################################
    #### stretching VS e_multi(small - only more_than_4_wavs)  ###
    ##############################################################
    plt.plot(stre,e_m_small,'ro')
    plt.xlabel('stretching')
    plt.ylabel('e_m_small')
    plt.show()

    ##############################################################
    #### embracing VS e_trans(small - only more_than_4_wavs)  ####
    ##############################################################
    plt.plot(embr,e_t,'ro')
    plt.xlabel('embracing')
    plt.ylabel('e_trans')
    plt.show()

    ##############################################################
    #### stretching VS e_trans(small - only more_than_4_wavs)  ####
    ##############################################################
    plt.plot(stre,e_t,'ro')
    plt.xlabel('stretching')
    plt.ylabel('e_trans')
    plt.show()



    ##################################################################################
    #### stretching VS Log2(num of faculties wav)(small - only more_than_4_wavs)  ####
    ##################################################################################
    plt.plot(stre,faculties_num_small,'ro')
    plt.xlabel('stretching')
    plt.ylabel('Log2(faculties')
    plt.show()

    #################################################################################
    #### embracing VS Log2(num of faculties wav)(small - only more_than_4_wavs)  ####
    #################################################################################
    plt.plot(embr,faculties_num_small,'ro')
    plt.xlabel('embracing')
    plt.ylabel('Log2(faculties')
    plt.show()



def create_excel(dict):
    # convert from dict to numpy array, convert to Excel file
    print(' ------ ')
    faculty_list_non_unicode = ["-1", 'תויונמא', 'הרבחה יעדמ', 'םייחה יעדמ', 'תואירבו האופר', 'הסדנה',
     'חורה יעדמ', 'םיטפשמ', 'לוהינ', 'םיקיודמ םיעדמ', '']
    faculty_list = [unicode(x, 'utf-8') for x in faculty_list_non_unicode]
    gender_list_non_unicode = ["-1",'רכז','הבקנ']
    gender_list = [unicode(x, 'utf-8') for x in gender_list_non_unicode]
    experiments_list = [None,"expr1","expr2","expr3","expr4"]
    #out_of_data_list=["","not at hour","not at day","curiosity_questions_not_full_amount, 1-9","curiosity_questions_is_empty, 0"]
    age_list=[-1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,
              31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,
              59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,
              87,88,89,90,91,92,93,94,95,96,97,98,99,100,185,""]
    for i in age_list:
       age_list[age_list.index(i)]=str(i)

    count=0
    number_of_subjects = 0
    for v in dict.values():
        for k, v2 in v.items():
            number_of_subjects += 1
    print('number_of_subjects: ', number_of_subjects)

    x_size = 53 + 2*len(emotion_list) + 1
    x = np.ndarray((number_of_subjects, x_size)).astype(object)
    column_titles = []   #columns_titles
    subject_number = -1  #columns_amount
    subject_files = [] #rows,participants
    for v in dict.values(): #tablets
        for k, v2 in v.items(): #files,data
            subject_number += 1
            subject_files.append(k)
            c = 0
            #sub_num
            x[subject_number, c] = float(subject_number)
            c += 1
            if subject_number == 0: # save the title only for the first file
                column_titles.append('subject number')

            #file
            x[subject_number, c] = k
            c += 1
            if subject_number == 0: # save the title only for the first file
                column_titles.append('file name')

            #experiment
            x[subject_number, c] = float(experiments_list.index(v2['experiment']))
            c += 1
            if subject_number == 0:
                column_titles.append('experiment')

            #if subject_number == 0:


        #     #email
        #     x[subject_number, c] = v2['personal_info']['email']
        # #print(x[subject_number, c])
        #     c += 1
        #     if subject_number == 0:
        #          column_titles.append('email')

            #gender
            x[subject_number, c] = float(gender_list.index(v2['personal_info']['gender']))
            c += 1
            if subject_number == 0:
                column_titles.append('gender')


            #faculty
            x[subject_number, c] = float(faculty_list.index(v2['personal_info']['faculty']))
            #print(v2['personal_info']['faculty'])
            c += 1
            if subject_number == 0:
                column_titles.append('faculty')


            #age
            if v2['personal_info']['age']==-1:
                v2['personal_info']['age']="-1"
            x[subject_number, c] =  float(age_list.index(v2['personal_info']['age']))
            c += 1
            if subject_number == 0:
                column_titles.append('age')

            # buttons   --- needed???

            #t0  - normalized to [0,60] ==> [0, 1]
            if v2['t0']!= -1:
                x[subject_number, c]= (v2['t0'].seconds)
                x[subject_number, c] /= 60.0
            else:
                x[subject_number, c] = -1 #(v2['t0'])
            c += 1
            if subject_number == 0:
                column_titles.append('t0')

            #total listenning time
            x[subject_number, c] = float(v2['listen_t']['tot']) / 60.0
            c += 1
            if subject_number == 0:
                column_titles.append('total listenning time')


            #curiosity_questions
            for i, q in enumerate(v2['curiosity_ques']):
                x[subject_number, c] = float(q)
                c += 1
                if i in [16,18] and q!=0:
                    #print(i, q)
                    x[subject_number, c] = 6-float(q)
                    #print(x[subject_number, c] )

                if subject_number == 0:
                    column_titles.append('curiosity question ' + str(i+1))

            #curiosity_questions stre- normalized [0.0, 1.0]
            if float(v2["curiosity_ques_stre"]) > 0:
                x[subject_number, c] = float(v2["curiosity_ques_stre"])
                x[subject_number, c] = (x[subject_number, c] - 5.0) / 20.0
            else:
                x[subject_number, c] = -1
            c += 1
            if subject_number == 0:
                column_titles.append('curiosity_ques_stretching')

            #curiosity_questions embr - normalized [0.0, 1.0]
            if float(v2["curiosity_ques_embr"]) > 0:
                x[subject_number, c] = float(v2["curiosity_ques_embr"])
                x[subject_number, c] = (x[subject_number, c] - 5.0) / 20.0
            else:
                x[subject_number, c] = -1
            c += 1
            if subject_number == 0:
                column_titles.append('curiosity_ques_embracing')

            #curiosity_questions TOTAL- normalized [0.0, 1.0]
            if float(v2["curiosity_ques_stre"]) > 0 and float(v2["curiosity_ques_embr"]) > 0:
                x[subject_number, c] = float(v2["curiosity_ques_embr"]) + float(v2["curiosity_ques_stre"])
                x[subject_number, c] = (x[subject_number, c] - 10.0) / 40.0
            else:
                x[subject_number, c] = -1
            c += 1
            if subject_number == 0:
                column_titles.append('curiosity_ques_embr+strt TOTAL')

            #transition count-?

            #transition proportion-?

            #transition entropy
            x[subject_number, c] = float(v2['trans_matrix']['e_trans'])
            c += 1
            if subject_number == 0:
                column_titles.append('transition entropy')


            #len(wav_sorted)
            x[subject_number, c] =  float(len(v2["wav_sorted"]))
            c += 1
            if subject_number == 0:
                column_titles.append('wavs amount')


             #listening time - per faculty
            for i in v2['fac_heard']:
                x[subject_number, c] =  float(v2['fac_heard'][i])
                c += 1
                if subject_number == 0:
                    column_titles.append('listening per faculty:' + str(i))


            #Multi entropy
            x[subject_number, c] =  float(v2["e_multidis"])
            c += 1
            if subject_number == 0:
                column_titles.append('Multi discipline entropy')

            #learning questions
            q_num=0
            if v2["learning_ques"]["ques-time"]:
                for i in v2["learning_ques"]["ques-time"]:
                    x[subject_number, c+q_num] = str(i[2])
                    x[subject_number, c+q_num+1] = str(i[1])
                    q_num += 2

            if subject_number == 0:
                for j in range(4):                                    # 4 or 5
                    column_titles.append('learning ' + str(j+1))
                    column_titles.append('learning ' + str(j + 1) + "- answer")
            c +=8

            x[subject_number, c] =  float(v2["learning_ques"]["learning %"])
            c += 1
            if subject_number == 0:
                column_titles.append('learning %')


            # BFI - normalized [0.0, 1.0]
            x[subject_number, c] = float(v2["BFI"])
            #x[subject_number, c] /= 5.0
            c += 1
            if subject_number == 0:
                column_titles.append('BFI')

            # faces normalized [0.0, 1.0]
            if subject_number == 0:
                for emotion in emotion_list:
                    column_titles.append(emotion + " mean")
                    column_titles.append(emotion + " std")
            if v2['faces']!=-1:
                count += 1
                for emotion in emotion_list:
                    if emotion in v2['faces']:
                        #print("***",emotion)
                        #print("*******",v2['faces'][emotion])
                        x[subject_number, c] = (v2['faces'][emotion]['mean']) / 100.0
                        x[subject_number, c+1] = (v2['faces'][emotion]['std'])
                    c += 2
            else:
                c+=2*len(emotion_list)

            # normalized total listenning time
            if v2['t0'] != -1:
                if float(v2['listen_t']['tot'])<=60.0-float(v2['t0'].seconds):
                    x[subject_number, c] = float(v2['listen_t']['tot']) / (60.0 - float(v2['t0'].seconds))

            else:
                x[subject_number, c] = -1
            c += 1
            if subject_number == 0:
                column_titles.append('normalized total listenning time')

    #print(x.shape())
    x[:,0]=x[:,0]+1
    x[:,:]=x[:,:x_size]

    #clean O and more
    for i in range(x.shape[0]): #row index
         for j in range(x.shape[1]):  #column index
             if j == 5: #age
                 if x[i, j] == 101:
                     x[i, j] = ""
                 if x[i, j] == 102:
                     x[i, j] = ""
             if j == 6:  # t0
                 if x[i, j] == -1:
                     x[i, j] = ""
                 if x[i, j] > 1.0:
                     x[i, j] = ""
                 # if x[i,6] > x[i,7]:
                 #     x[i, j] = ""
             if j == 7:  # total listening time
                 if x[i, j] > 1.0:
                     x[i, j] = ""
             if j in [28,29,30]:  # CEI ,STR,EMR,TOT
                 if x[i, j] < 0.0:
                     x[i, j] = ""
             # if x[i,6] > 0 and x[i, 6] > x[i, 7]:
                 #     x[i, j] = ""
             if j == 4:  # expr 2 had no faculty, bug fix
                 if x[i,2] == 2:
                     x[i, j] = ""
             if j == (x_size-1):    # normalized total listening time
                 if x[i, j] < 0.0 or x[i, j] > 1.0 : # or x[i, j] > 0.5:
                     x[i, j] = ""
             if j in range(3,x_size):
                 if x[i,j]== -1:
                     x[i,j]=""
             if j == 52:  # BFI
                if x[i, j] < 0.0:
                    x[i, j] = ""

    x=np.insert(x,0,np.array(column_titles),0)
    #print("counter!!!!",count)

    np.savetxt(analysis_path + "ALL_DATA_normalized.csv", x,'%s', delimiter=",")
    print(column_titles)


    return np,column_titles
    #np.savetxt("C://Users//kerenbt//Downloads//%PYTHON_HOME%//projects//open_day_2//1&2_with_faces.csv", y, delimiter=",")







'''
############################################################################
                        ####   GOREN    ####
############################################################################
# check why few files has FACULTY in the second expr? only life science faculty
print("check faculty",check_faculty,len(check_faculty))

#check out of data amount
t=0
f=0
for i in range(5):
    for file in dict[current_tab].keys():
        if dict[current_tab][file]["out_of_data"]:
            t+=1
            print(file)
        else:
            f+=1
print(t,f)


# check why only 28 files has T0, also what are 2 time in comment - first screen to first touch?
for t0 in check_t0:
    print(t0)

# check CURIOSITY QUESTIONS list is full (has all answers), if not mark as out of data - but how come???

#check GENDER
male,female=0,0

for i in range(num_tablet):
    current_tab = 'Tab' + str(i + 1)
    for gen in amount_of_data['gender'][current_tab]:
        if gen == "רכז":
            male+=1
        else:
            female+=1
print(male,female)

# check BUTTONS -  why some files has final_b before consent_b ? also check file with no buttons saved,

has_some_buttons_info=0
has_both_consent_and_final=0
has_no_buttons_info=0

for i in range(num_tablet):
    current_tab = 'Tab' + str(i + 1)
    for file in dict[current_tab]:
        if dict[current_tab][file]["buttons"]:
            print(dict[current_tab][file]["experiment"])
            has_some_buttons_info+=1
            if 'final_button' in dict[current_tab][file]["buttons"].keys() and 'consent_button' in dict[current_tab][file]["buttons"].keys():
                final_b=dict[current_tab][file]["buttons"]['final_button']
                consent_b=dict[current_tab][file]["buttons"]['consent_button']
                print("***final_b:",final_b,"***consent_b:",consent_b,"**gap",final_b-consent_b )
                has_both_consent_and_final+=1
            #### If we take the time stamp from KEY and not from current_value['data']['time'] this is relevant
                # I think it isn't relevant sense the change is in milliseconds, see second print
                # final_b2=dict[current_tab][file]["buttons"]['final_button2']
                # consent_b2=dict[current_tab][file]["buttons"]['consent_button2']
                # print("***final_b2:",final_b2,"***consent_b2:",consent_b2,"**gap2",final_b2-consent_b2)
                # print(final_b-consent_b == final_b2-consent_b2,consent_b == consent_b2,final_b == final_b2 )
        else:
            has_no_buttons_info+=1

print("has_some_buttons_info:",has_some_buttons_info,"has_both_consent_and_final",has_both_consent_and_final,
      "has_no_buttons_info",has_no_buttons_info)


# check EMAIL
# need to be only UNDER filling infomation part!!!IF NOT - Overrides and errors!

for i in range(num_tablet):
    current_tab = 'Tab' + str(i + 1)
    c=0
    for file in amount_of_data['email'][current_tab]:
        email= amount_of_data['email'][current_tab][file]
        if "@" in email:
           c +=1
    amount_of_data['email'][current_tab] = c
    print(amount_of_data['email'][current_tab])


# check AGE
# need to be only UNDER filling infomation part!!!IF NOT - Overrides and errors!

for i in range(num_tablet):
    current_tab = 'Tab' + str(i + 1)
    c=0
    for file in amount_of_data['age'][current_tab]:
        age= amount_of_data['age'][current_tab][file]
        if age:
            c +=1
    amount_of_data['age'][current_tab] = c


#check OUT OF DATA

for i in range(num_tablet):
    current_tab = 'Tab'+str(i+1)
    print(amount_of_data['relevent_data_per_tab'][current_tab],current_tab,'relevent_data_per_tab')
    print(amount_of_data['out_of_day_per_tab'][current_tab], current_tab, 'out_of_day_per_tab')
    print(amount_of_data['out_of_hour_per_tab'][current_tab], current_tab, 'out_of_hour_per_tab')

#OLD - NEEDED???
# total per faculty - (ALL participants)
fac_time={"art":0,"eng":0,"exa":0,"hum":0,"law":0,"lif":0,"man":0,"med":0,"soc":0}
for k, v in dict.items():
    for participant, value in v.items():
        for fac,t in value["list_fac"].items():
            fac_time[fac]+=value["list_fac"][fac]
'''
