import pandas as pd
from scipy.stats import linregress
import math

#print (row_array)

df = pd.read_excel("C://Users//kerenbt//Desktop//thesis//Correlation//8x8.xlsx")
a= df.as_matrix()
a=a.transpose()
data_title= [ 't0', 'total listenning time','curiosity_ques_stretching','curiosity_ques_embracing','CEI-II-total - embracing+ stretching', 'transition entropy', 'Multi discipline entropy','% Currect']

name_of_couple = []   # name of which two variables you compute
corr_of_couple = []      # the actual results of the calculation
for i1, var1 in enumerate(a):
    for i2, var2 in enumerate(a):
        if i2 > i1: # go over only different variables, and only once

            var1a=[]
            var2a=[]

            counter=0
            for x in var1:
                if x!=-1 and x!=0 and not math.isnan(x):
                    if var2[counter]!=-1 and var2[counter]!=0  and not math.isnan(var2[counter]):
                        var1a.append(x)
                        var2a.append(var2[counter])
                counter+=1

            np[:,0] !=1 and np[:,0] !=0

            name_of_couple.append([i1,i2])
            corr_of_couple.append(linregress(var1a,var2a))
            #print(linregress(var1a,var2a))
            slope, intercept, r_value, p_value, std_err = linregress(var1a,var2a)
            print(data_title[i1],"AND",data_title[i2])
            print(var1a,var2a)
            print("r_square-  ","%.3f" % (r_value**2),"p_value-  ", p_value)


#print(name_of_couple,corr_of_couple)