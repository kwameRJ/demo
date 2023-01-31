import random
import pandas as pd
import csv

def calculate_final_grade(mid_score, mid_participation_score, mid_lab_score):
    total_score = mid_score + mid_participation_score + mid_lab_score
    if total_score >= 14.5:
        return 'A+'
    elif total_score >= 13.5:
        return 'A'
    elif total_score >= 12.5:
        return 'A-'
    elif total_score >= 11.5:
        return 'B+'
    elif total_score >= 10.5:
        return 'B'
    elif total_score >= 9.5:
        return 'B-'
    elif total_score >= 8.5:
        return 'C+'
    elif total_score >= 7.5:
        return 'C'
    elif total_score >= 6.5:
        return 'C-'
    elif total_score >= 5.5:
        return 'D'
    elif total_score >= 4.5:
        return 'E'
    else:
        return 'F'




dictionaries = {
        "id" : "student_id as string",
    "course_code": ['CS102', 'ACCT101','ENG101', 'CS103', 'IT102', 'FRN101', 'UFS101'],
    "mid_score": 0,
    "mid_participation_score": 0,
    "mid_lab_score": 0,
    "final_grade": '',
        'sex': {'male':0, 'female':1},
        'age': 0,
        'address': {'rural': 0, 'urban': 1},
        'Medu': {'none':0, 'primary education': 1, 'junior high': 2, 'secondary education':3, 'higher education':4},
        'Fedu': {'none':0, 'primary education': 1, 'junior high': 2, 'secondary education':3, 'higher education':4},
        'Mjob': {'teacher':0, 'health':1, 'civil':2, 'at home':3, 'other':4},
        'Fjob': {'teacher':0, 'health':1, 'civil':2, 'at home':3, 'other':4},
        'reason': {'home':0, 'reputation': 1, 'course':2, 'other':3},
        'guardian': {'father':0, 'mother':1, 'other':2},
        'traveltime': {'1-15 mins':0, '15-30 mins':1, '30mins - 1 hour':2, '> 1hour': 3},
        'studytime':{'< 2hours':0,'2-5 hours':1,'5-10 hours':2,'>10 hours':3},
        'activities':{'no':0, 'yes':1}, 
        'higher':{'no':0, 'yes':1},
        'health': 0,
        'wassce': 0
    }

def generate_dataset(dictionaries, n=1):
    data = []
    for i in range(n):
        dataset = {}
        for key,val in dictionaries.items():
            if key =='id':
                dataset[key] = f'Stu{i}'
            elif key == 'mid_score':
                dataset[key] = round(random.uniform(0, 17.5), 2)
            elif key == 'mid_participation_score':
                dataset[key] = round(random.uniform(0, 5), 2)
            elif key == 'mid_lab_score':
                dataset[key] = round(random.uniform(0, 5), 2)
            elif key == 'final_grade':
                dataset[key] = calculate_final_grade(dataset['mid_score'],dataset['mid_lab_score'],dataset['mid_lab_score'])
            elif key == 'age':
                dataset[key] = random.randint(17, 60)
            elif key=='wassce':
                dataset[key] = random.randint(8, 54)
            elif key=='health':
                dataset[key] = random.randint(1, 10)
            
            else:
                
                values = [i for i in val]
                dataset[key] = random.choice(values)
        data.append(dataset)
    return(data)

def save_to_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(dictionaries.keys())
        writer.writerows([i.values() for i in data])


dataset = generate_dataset(dictionaries,1000)
save_to_csv("dataset.csv", dataset)