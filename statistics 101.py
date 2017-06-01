import pandas as pd
from scipy import stats

def wilk_shapiro_test_if_normal(path,subjects_num,data_title):
    a= (pd.read_excel(path)).as_matrix()
    df = pd.DataFrame(a, index=list(range(subjects_num)) ,columns=data_title)
    # print("Shapiro-Wilk test for normality- Return: (The test statistic, The p-value for the hypothesis test)")
    '''for x in data_title:
        new = df[x][df[x].notnull()]
        #print(new, x)
        #print(x, stats.shapiro(new),stats.shapiro(new)[1]< 0.05 )'''
    return df



def anova_test(subjects_num,groups_list,measures,df):
    pairs = []
    for subject in range(subjects_num):
        for group in groups_list:
            for measure in measures:
                pairs.append( ((group,df[group][subject]),(measure,df[measure][subject])) )
                #print((group,df[group][subject]),(measure,df[measure][subject]))

    gender_stat= {}
    age_stat={}
    faculty_stat={}
    for point in pairs:
        if point[0][0] == 'gender':
            if not pd.isnull(point[1][1]) and not pd.isnull(point[0][1]):
                if (point[0][1],point[1][0]) in gender_stat.keys():
                    gender_stat[(point[0][1],point[1][0])].append((point[0][1],point[1][1]))
                    #print ((point[0][1],point[1][0]) , "key")
                    #print(point[1][1], "val")

                else:
                    gender_stat[(point[0][1], point[1][0])]=[]
                    gender_stat[(point[0][1],point[1][0])].append((point[0][1],point[1][1]))

        elif point[0][0] == 'age':
            if not pd.isnull(point[1][1]) and not pd.isnull(point[0][1]):
                if (point[0][1],point[1][0]) in age_stat.keys():
                    age_stat[(point[0][1],point[1][0])].append((point[0][1],point[1][1]))
                    #print ((point[0][1],point[1][0]) , "key")
                    #print(point[1][1], "val")

                else:
                    age_stat[(point[0][1], point[1][0])]=[]
                    age_stat[(point[0][1],point[1][0])].append((point[0][1],point[1][1]))
        else:
            if not pd.isnull(point[1][1]) and not pd.isnull(point[0][1]):
                if (point[0][1], point[1][0]) in faculty_stat.keys():
                    faculty_stat[(point[0][1], point[1][0])].append((point[0][1], point[1][1]))
                    # print ((point[0][1],point[1][0]) , "key")
                    # print(point[1][1], "val")

                else:
                    faculty_stat[(point[0][1], point[1][0])] = []
                    faculty_stat[(point[0][1], point[1][0])].append((point[0][1], point[1][1]))
    '''print('gender')
    for key in gender_stat.keys():
        print(key)
    print('age')
    for key in age_stat.keys():
        print(key)
    print('faculty')
    for key in faculty_stat.keys():
        print(key)'''

    final_stat={}
    dict_of_groups = [gender_stat,faculty_stat,age_stat]
    for measure in measures:
        dict_count=0
        for dict in dict_of_groups:
            #print (groups_list[dict_count]," VS ", measure)
            dict_count+=1
            #print(measure)
            groups = []
            values =[]
            for key in dict.keys():
                if key[1]==measure:
                    #print(len(dict[key]),"(group,measure value)",dict[key])
                    #print(len(list(list(zip(*dict[key]))[0])))
                    #print("(group) - list",list(list(zip(*dict[key]))[0]))
                    #print(len(list(list(zip(*dict[key]))[1])))
                    #print("(value) - list",list(list(zip(*dict[key]))[1]))
                    #print(list(list(zip(*dict[key]))[0])[0])
                    groups.append(list(list(zip(*dict[key]))[0])[0])
                    values.append(list(list(zip(*dict[key]))[1]))

            n=0
            for x in values:
                n+=1
                for y in values[n:]:
                    f_val, p_val = stats.f_oneway(x,y)
                    group_1 =groups[n-1]
                    group_2 = groups[values.index(y)]
                    group =groups_list[dict_count-1]
                    #print(group,group_1,group_2,measure)
                    #print("f_val - ",f_val)
                    #print("p_val - ", p_val)
                    f_val = float("%.3f" % f_val)
                    p_val = float("%.3f" % p_val)
                    if p_val < 0.05:
                        print("p_val is under 0.05 :)")
                    else:
                        print("p_val is too high :(")
                    if group_1<group_2:
                        final_stat[(group,(group_1,group_2),measure)] = (f_val,p_val)
                    else:
                        final_stat[(group,(group_2,group_1),measure)] = (f_val,p_val)

    '''for key in final_stat.keys():
        print(key)
        print(final_stat[key])'''
    return final_stat

def dict_to_table(path,final_stat,groups_list,measures):
    #df = pd.DataFrame(a, index=list(range(subjects_num)), columns=data_title)
    combinations=[]
    for key in final_stat.keys():
        if (key[0],key[1]) not in combinations:
            combinations.append((key[0],key[1]))
            #print((key[0],key[1]))


    df = pd.DataFrame(index=combinations, columns=measures)
    for key in final_stat.keys():
        df[key[2]][(key[0],key[1])] = final_stat[key]
    df.to_excel(path,sheet_name="results")


####################MAIN####################

path = "C://Users//kerenbt//Desktop//thesis//Correlation//11x136_EXPR3.xlsx"
path_res = "C://Users//kerenbt//Desktop//thesis//Correlation//11x136_EXPR3_RES.xlsx"

data_title = ['subject number', 'gender', 'faculty', 'age', 't0', 'total listening time', 'curiosity_ques_stretching',
              'curiosity_ques_embracing', 'CEI-II-total - embracing+ stretching', 'transition entropy',
              'Multi discipline entropy']
groups_list = ['gender','faculty','age']
measures = ['t0', 'total listening time','curiosity_ques_stretching','curiosity_ques_embracing','CEI-II-total - embracing+ stretching', 'transition entropy', 'Multi discipline entropy']
subjects_num = 136

df = wilk_shapiro_test_if_normal(path ,subjects_num,data_title)
final_stat = anova_test(subjects_num,groups_list,measures,df)
dict_to_table(path_res,final_stat,groups_list,measures)
