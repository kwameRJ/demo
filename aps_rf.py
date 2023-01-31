import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import pickle
import db

# Train your model for different number of classifiers

# Load the data into a pandas DataFrame
categorical_columns = ["sex","address","Medu","Fedu","Mjob","Fjob","reason","guardian","traveltime","studytime","activities","higher"]

def train_models(columns, model_name):
    data = pd.read_csv('dataset.csv')
    # Drop any rows with missing values
    data = data.dropna()

    # Encode categorical variables using LabelEncoder
    

    
    for i in categorical_columns:
        for k,v in db.dictionaries[i].items():
                data[i] = data[i].apply(lambda x:x.lower() if isinstance(x,str) else x)
                data[i] = data[i].apply(lambda x: v if isinstance(x,str) and k in x else x)

    # Split the data into features and target variables
    features = data[columns]
    target = data['final_grade']

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # Train a random forest classifier on the training data
    clf = RandomForestClassifier(n_estimators=100, random_state=42)

    clf.fit(X_train, y_train)

    # Use the trained classifier to make predictions on the test data
    y_pred = clf.predict(X_test)

    # Evaluate the accuracy of the predictions
    accuracy = (y_pred == y_test).mean()
    save_model(clf,model_name)
    return

def save_model(model, name):
    with open(f"{name}.pkl", "wb") as file:
            pickle.dump(model, file)

def predict(model, data):
    prediction = model.predict(data)
    return prediction
    

def load_model(name):
    with open(f"{name}.pkl", "rb") as file:
        loaded_model = pickle.load(file)
    
    return loaded_model

