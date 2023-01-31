# DB  Functions
from peewee import *
from peewee_plus import *
import json

db = SqliteDatabase('aps.db')

class BaseModel(Model):
   class Meta:
      database=db

class User(BaseModel):
  id = CharField(primary_key=True, unique=True)
  name = CharField()
  password = CharField()
  role = CharField()
  
  def __init__(self, id, name, password,role, **kwargs):
    super().__init__(**kwargs)
    self.id = id
    self.name = name.title()
    self.password = password
    self.role = role


class Administrator(User):
  pass
  
class Student(User):
    program = CharField()
    level = IntegerField()
    demographics = JSONField()
    basket = JSONField()
    school = CharField()

    def __init__(self, id, name, password, program, level, demographics,  role, school,basket=[], **kwargs):
        super().__init__(id, name, password, role, **kwargs)
        self.program = program
        self.level = level
        self.demographics = demographics
        self.basket = basket
        self.school = school

class Lecturer(User):
  school = CharField()
  basket = JSONField()
  def __init__(self, id, name, password, school, basket, role,**kwargs):
    super().__init__(id, name, password, role, **kwargs)
    self.basket = basket
    self.school = school

class Course(BaseModel):
    id = CharField(primary_key=True,unique=True)
    name = CharField()
    school = CharField()
    semester = CharField()
    lecturer = CharField()

    def __init__(self, id, name, school, semester, lecturer, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name
        self.school = school
        self.semester = semester
        self.lecturer = lecturer
    
class Gradesheet(BaseModel):
    id = CharField()
    course_code = CharField()
    mid_score = FloatField(null=True)
    mid_participation_score = FloatField(null=True)
    mid_lab_score = FloatField(null=True)
    final_grade = CharField(null=True, default='')

    def __init__(self, id, course_code, mid_score, mid_participation_score, mid_lab_score, final_grade, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.course_code = course_code
        self.mid_score = mid_score
        self.mid_participation_score = mid_participation_score
        self.mid_lab_score = mid_lab_score
        self.final_grade = final_grade
      
class SemesterGrades(BaseModel):
    id = ForeignKeyField(Student, backref='semester_grades', on_delete='CASCADE')
    demographics = JSONField()
    semester_gpa_1 = FloatField()
    semester_gpa_2 = FloatField()
    semester_gpa_3 = FloatField()
    semester_gpa_4 = FloatField()
    semester_gpa_5 = FloatField()
    semester_gpa_6 = FloatField()
    semester_gpa_7 = FloatField()
    semester_gpa_8 = FloatField()

    def __init__(self, id, demographics, semester_gpa_1, semester_gpa_2, semester_gpa_3, semester_gpa_4, semester_gpa_5, semester_gpa_6, semester_gpa_7, semester_gpa_8, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.demographics = demographics
        self.semester_gpa_1 = semester_gpa_1
        self.semester_gpa_2 = semester_gpa_2
        self.semester_gpa_3 = semester_gpa_3
        self.semester_gpa_4 = semester_gpa_4
        self.semester_gpa_5 = semester_gpa_5
        self.semester_gpa_6 = semester_gpa_6
        self.semester_gpa_7 = semester_gpa_7
        self.semester_gpa_8 = semester_gpa_8

class TrainingData(Gradesheet):
  demographics = JSONField()
  def __init__(self, id, course_code, mid_score, mid_participation_score, mid_lab_score, final_grade, demographics, **kwargs):
        super().__init__(id, course_code, mid_score, mid_participation_score, mid_lab_score, final_grade,**kwargs)
        self.demographics = demographics
        


#-------------MAJOR ENTITIES-----------#
USER = {
  'ID': '',
  'PASSWORD': '',
  'NAME': '',
  'ROLE': ''
}

STUDENT = {
  'ID': '',
  'PROGRAMME': '',
  'LEVEL': '',
  'DEMOGRAPHICS': {},
  'COURSE_BASKET': {},
}

LECTURER = {
  'ID': '',
  'ASSIGNED_COURSES': {}
}


COURSE = {
  'CODE': '',
  'TITLE': '',
  'SCHOOL': '',
  'SEMESTER': '',
  'ASSIGNED': False
}

GRADESHEET = {
  'ID': '',
  'COURSE_CODE': '',
  'MIDSCORE': 0.00,
  'MID_PARTICIPATION_SCORE': 0.00,
  'MID_LAB_SCORE': 0.00,
  'FINAL_GRADE': '' 
}

#---------CHOICES---------------#
ROLES = ['Administrator', 'Lecturer', 'Student']
SCHOOLS = ['ABS','ASSDAS','SATES', 'GENERAL']
SEMESTERS = ['L100-1', 'L100-2','L200-1', 'L200-2', 'L300-1','L300-2', 'L400-1', 'L400-2']
GRADES = ['A+','A','A-','B+','B','B-','C+','C','C-','D','E','F']
UPPER_GRADES = ['A+','A','A-','B+','B','B-']
LOWER_GRADES = ['D','E','F']
PROGRAMMES = ['Business Administration', 'Computer Science & IT', 'Engineering']
dictionaries = {
        'sex': {'male':0, 'female':1},
        'age': {'integer': 'between 15 and 60 years'},
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
        'health':{'integer':'between 1 and 10'},
        'wassce': {'integer': 'between 8 and 59'}
    }

#---------FUNCTIONS---------#
# Create function
def create_entity(cls,**kwargs):
    entity = cls.create(**kwargs)
    entity.save()
    return entity

# Read function
def get_student(id):
    return Student.get(Student.id == id)

# Update function
def update_entity(entity, **kwargs):
    for key, value in kwargs.items():
        setattr(entity, key, value)
    entity.save()
    return entity

# Delete function
def delete_entity(cls,id):
    entity = cls.get(cls.id == id)
    entity.delete_instance()

db.create_tables([BaseModel, User, Administrator, Lecturer, Student, Course, Gradesheet, TrainingData])

def assign_courses_to_students():
  students = Student.select()

  for student in students:
    #check if there is any course in the basket
    school_courses = [i.id for i in Course.select().where(Course.school==student.school,Course.lecturer!='Unassigned').execute()]
    general_courses = [i.id for i in Course.select().where(Course.school=='GENERAL', Course.lecturer!='Unassigned').execute()]
    school_courses_level = [i.id for i in Course.select().where(Course.school==student.school, Course.semester == student.level, Course.lecturer!='Unassigned').execute()]
    general_courses_level = school_courses = [i.id for i in Course.select().where(Course.school=="GENERAL", Course.semester == student.level, Course.lecturer!='Unassigned').execute()]
    if student.basket:
      student.basket = [i for i in student.basket if i in school_courses_level or i in general_courses_level]
    else:
      #assign courses to empty baskets
      student.basket = school_courses_level + general_courses_level
    print(student.basket)
    student.save()


def assign_courses_to_lec():
    lecturers = {}
    for lecturer in Lecturer.select():
        lecturer.basket = []
        lecturers.setdefault(lecturer, [])

    for course in Course.select():

        if course.lecturer != 'Unassigned':
            lec = Lecturer.get(Lecturer.name == course.lecturer)
            if course.school != 'GENERAL' and course.school != lec.school:
              #print(course, course.lecturer)
              print(lecturers)
              course.lecturer = 'Unassigned'
              course.save()
            else:
              
              lecturers[lec].append(course.id)
                

    for key, val in lecturers.items():
        print(key, val)
        key.basket = val
        key.save()


assign_courses_to_lec()
assign_courses_to_students()


try:
  create_entity(Administrator, id='admin', password='admin01', name='Admin', role='Administrator')
except IntegrityError:
  pass

all_course_list = [i.id for i in Course.select()]
all_students_list = [i.id for i in Student.select()]
all_lecturer_list = [i.name for i in Lecturer.select()]