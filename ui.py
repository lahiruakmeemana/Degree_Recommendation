import sys
import json
from PyQt5.QtWidgets import QGridLayout,QApplication, QWidget, QLabel, QPushButton, QMessageBox,QComboBox,QFormLayout,QLineEdit

import numpy as np
import pandas as pd
from tensorflow import keras
from sklearn.preprocessing import OneHotEncoder
from geopy.geocoders import Nominatim


class DegreeRecommendor:
    #pre-trained model is loaded and it is used to predict user inputs
    def __init__(self):
        self.model = keras.models.load_model('trained_model.h5')
        
        #to encode the inputs encoder are created
        data = pd.read_csv('degree_dataset.csv')        
        self.degree_names = np.sort(data['Degree_University'].unique())
        self.max_income = data['Parent_Income'].max()
        self.encoders = [OneHotEncoder(handle_unknown='ignore') for _ in range(4)]
        self.locator = Nominatim(user_agent="myGeocoder")
        self.max_lat = 9.81667
        self.max_lon = 81.84198
         
        for i,column in enumerate(columns):
            self.encoders[i].fit(np.array(fields[column]).reshape((-1,1)))
        
        
    def recommend(self,test):
        test = np.array(test)
        try:
            city_lat,city_lon = self.locator.geocode(test[3]+', Sri Lanka')[-1]
            dis_lat,dis_lon = self.locator.geocode(test[2]+' Sri Lanka')[-1]
            city_lat = abs(city_lat - dis_lat)
            city_lon = abs(city_lon - dis_lon)
            
            model_in = [int(test[4])/self.max_income, city_lat, city_lon, dis_lat/self.max_lat, dis_lon/self.max_lon]
        
            
            for i in range(3): #encoding inputs
                model_in.extend(self.encoders[i].transform(test[i].reshape((-1,1))).toarray().flatten())
            
            #predict
            model_out = self.model.predict(np.array(model_in).reshape((1,43)))
            degrees = self.degree_names[np.argsort(model_out.flatten())[-1:-5:-1]]
            
            print(degrees)
            return degrees.tolist()
        except ValueError:
            print('Please input valid input in LKR')
            return 'Please input valid input in LKR'
        except TypeError:
            print('Enter City name correctly')
            return 'Enter City name correctly'
        except:
            
            print('You are not connected to internet')
            return 'You are not connected to internet'
        

#for display options in drop down boxes 
with open("fields.json") as file:
    fields = json.load(file)
columns = ['A/L_Subjects', 'Your_choise', 'District']

#once recommend  button clicked this function will execute
def recommend():
    inputs = []
    for i in range(3):
        curr_txt = input_widgets[i].currentText()
        if curr_txt==' ':
            rec_label.setText('Please select '+ combo_labels[i])
            return
        inputs.append(curr_txt)
    inputs.append(city.text())
    inputs.append(income.text())
    
    rec_label.setText('Recommended Degrees:') 
    rec_degrees = degree_recommendor.recommend(inputs)
    if type(rec_degrees)==list:
        for i in range(4):
            out_labels[i].setText(' '+rec_degrees[i])
    else:
        rec_label.setText(rec_degrees)
        for i in range(4):
            out_labels[i].setText(' ')
    return 

if __name__ == "__main__":
    
    degree_recommendor = DegreeRecommendor()
    
    ui = QApplication(sys.argv)
    window = QWidget()
    window.resize(475,400)
    window.setWindowTitle('Higher Education Recommendation System')
    
    #ui layout
    layout = QFormLayout()
    layout.addRow("{:<25}".format('Name:'),QLineEdit())
    input_widgets = []
    combo_labels = ['A/L Subjects:', 'Your choise:', 'District:']
    for i in range(3):
        combobox = QComboBox()
        temp = fields[columns[i]].copy()
        temp.insert(0,' ')
        combobox.addItems(temp)
        input_widgets.append(combobox)
        layout.addRow("{:<25}".format(combo_labels[i]),combobox)
    city = QLineEdit()
    layout.addRow('City:',city)
    income = QLineEdit()
    layout.addRow("{:<25}".format('Parent Income:'),income)
    input_widgets.append(income)
    
    btn = QPushButton()
    btn.setText('Recommend Degree')
    btn.clicked.connect(recommend)
    layout.addRow(btn)
   
    rec_label = QLabel()
    layout.addRow(rec_label)
    
    out_labels = []
    for i in range(5):
        out_label = QLabel()
        out_labels.append(out_label)
        layout.addRow(out_label)
    
    window.setLayout(layout)
    window.show()
    sys.exit(ui.exec_())