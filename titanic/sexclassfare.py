'''
Created on 03/05/2013

@author: juaning
'''
import csv as csv 
import numpy as np

csv_file_object = csv.reader(open('csv/train.csv', 'rb')) 
test_file_object = csv.reader(open('csv/test.csv', 'rb'))
open_file_object = csv.writer(open("csv/genderclassbasedmodelpy.csv", "wb"))
train_header = csv_file_object.next()
test_header = test_file_object.next()

data=[]                          #Create a variable called 'data'
for row in csv_file_object:      #Run through each row in the csv file
    data.append(row)             #adding each row to the data variable
data = np.array(data)

# Create rules
fare_ceiling = 40
data[data[0::,8].astype(np.float) >= fare_ceiling, 8] = fare_ceiling-1.0
fare_bracket_size = 10
number_of_price_brackets = fare_ceiling / fare_bracket_size
number_of_classes = 3 #There were 1st, 2nd and 3rd classes on board 
# Define the survival table
survival_table = np.zeros((2, number_of_classes, number_of_price_brackets))

# Generate table
for i in xrange(number_of_classes):       #search through each class
    for j in xrange(number_of_price_brackets):   #search through each price
        women_only_stats = data[                      \
                         (data[0::,3] == "female")    \
                       &(data[0::,1].astype(np.float) \
                             == i+1)                  \
                       &(data[0:,8].astype(np.float)  \
                            >= j*fare_bracket_size)   \
                       &(data[0:,8].astype(np.float)  \
                            < (j+1)*fare_bracket_size)\
                          , 0]                                                   
                                                                                                 


        men_only_stats = data[                        \
                         (data[0::,3] != "female")    \
                       &(data[0::,1].astype(np.float) \
                             == i+1)                  \
                       &(data[0:,8].astype(np.float)  \
                            >= j*fare_bracket_size)   \
                       &(data[0:,8].astype(np.float)  \
                            < (j+1)*fare_bracket_size)\
                          , 0] 
        
    survival_table[0,i,j] = np.mean(women_only_stats.astype(np.float)) #Women stats
    survival_table[1,i,j] = np.mean(men_only_stats.astype(np.float)) #Men stats

survival_table[ survival_table != survival_table ] = 0.

survival_table[ survival_table < 0.5 ] = 0
survival_table[ survival_table >= 0.5 ] = 1 

for row in test_file_object:                    
    for j in xrange(number_of_price_brackets):
        try:
            row[7] = float(row[7])
        except: 
            bin_fare = 3-float(row[0])
            break
        if row[7] > fare_ceiling:
            bin_fare = number_of_price_brackets-1
            break
        if row[7] >= j*fare_bracket_size\
        and row[7] < \
            (j+1)*fare_bracket_size: 
            bin_fare = j
            break
    if row[2] == 'female':
        row.insert(0,
                   int(survival_table[0,float(row[0])-1, \
                                      bin_fare]))
        open_file_object.writerow(row)          
    else:
        row.insert(0,\
                   int(survival_table[1,float(row[0])-1, \
                                      bin_fare]))
        open_file_object.writerow(row)
                            