import streamlit as st
from db import *
import pandas as pd
import numpy as np
from playhouse.shortcuts import model_to_dict
from st_aggrid import AgGrid, JsCode, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import aps_rf as model


sns.set()


st.set_page_config(page_title="APS", page_icon=":guardsman:", layout="wide")

session = st.session_state

mainSection = st.empty()
mainPage = mainSection.container()
userform = mainPage.container()
grid, edit = mainSection.columns([3, 1])
warningSection = mainSection.container()


ENTITY = [
    "Administrator",
    "Lecturer",
    "Student",
    "Course",
    "Gradesheet",
    "TrainingData",
]
lec_keys = ("id", "name", "password", "role", "school", "basket")
student_keys = (
    "id",
    "name",
    "password",
    "role",
    "program",
    "school",
    "level",
    "demographics",
    "basket",
)
admin_keys = ("id", "name", "password", "role")
course_keys = ("id", "name", "school", "semester", "lecturer")
gradesheet_keys = (
    "id",
    "course_code",
    "mid_score",
    "mid_participation_score",
    "mid_lab_score",
    "final_grade",
)
training_keys = (
    "id",
    "course_code",
    "mid_score",
    "mid_participation_score",
    "mid_lab_score",
    "final_grade",
    "sex",
    "age",
    "address",
    "Medu",
    "Fedu",
    "Mjob",
    "Fjob",
    "reason",
    "guardian",
    "traveltime",
    "studytime",
    "activities",
    "higher",
    "health",
    "wassce",
)

model_keys = (
    "course_code",
    "mid_score",
    "mid_participation_score",
    "mid_lab_score",
    "sex",
    "age",
    "address",
    "Medu",
    "Fedu",
    "Mjob",
    "Fjob",
    "reason",
    "guardian",
    "traveltime",
    "studytime",
    "activities",
    "higher",
    "health",
    "wassce",
)

ds1 = ["mid_score",
    "sex",
    "age",
    "address",
    "Medu",
    "Fedu",
    "Mjob",
    "Fjob",
    "reason",
    "guardian",
    "traveltime",
    "studytime",
    "activities",
    "higher",
    "health",
    "wassce"]

ds2 = [
    "mid_score",
    "mid_participation_score",
    "mid_lab_score",
    "sex",
    "age",
    "address",
    "Medu",
    "Fedu",
    "Mjob",
    "Fjob",
    "reason",
    "guardian",
    "traveltime",
    "studytime",
    "activities",
    "higher",
    "health",
    "wassce",
]
ENTITIES = {
    ENTITY[0]: Administrator,
    ENTITY[1]: Lecturer,
    ENTITY[2]: Student,
    ENTITY[3]: Course,
    ENTITY[4]: Gradesheet,
    ENTITY[5]: TrainingData,
}

ENTITY_KEYS = {
    ENTITY[0]: admin_keys,
    ENTITY[1]: lec_keys,
    ENTITY[2]: student_keys,
    ENTITY[3]: course_keys,
    ENTITY[4]: gradesheet_keys,
    ENTITY[5]: training_keys,
}


SCHOOL_PROGRAMS = {
    "Business Administration": "ABS",
    "Computer Science & IT": "ASSDAS",
    "Engineering": "SATES",
}


# ------------LOGIN FUNCTIONS --------------#


def login_page():
    with mainSection.form("Login"):
        st.title("Login")
        id = st.text_input("ID")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["Administrator", "Lecturer", "Student"])

        if st.form_submit_button("Submit"):
            if id and password and role:
                # authenticate user here
                user = authenticate_user(id, password, role)
                if user:
                    session["current_user"] = user
                    st.success(f"Logged in as {role}")
                    # redirect to appropriate page
                    st.experimental_rerun()

                else:
                    st.error("Invalid credentials")
            else:
                st.error("Please fill all the fields")


def authenticate_user(id, password, role):
    # logic to authenticate user using the provided id and password
    cls = ENTITIES[role]

    user = cls.select().where(cls.id == id, cls.password == password)
    if user:
        return user.get()

    return None


def logout():
    # logic to log out the user and redirect to the login page
    session["current_user"] = None
    login_page()


# -------------ADMINISTRATOR PAGES--------------#


# ---------Entity Views----------#
def entity_view(entity, user=False):
    mode, func = set_values(entity, user)
    update = True if user else False
    with mainPage.form(f"{mode} {entity}", True):
        st.subheader(f"{mode} {entity}")
        ENTITY_VIEWS[entity](entity, update)
        submit = st.form_submit_button(
            f"{mode} {entity}", on_click=func, args=([entity])
        )


def add_admin(entity, update=False):
    id = st.text_input("Administrator ID", key=f"{entity}_id_field", disabled=update)

    name = st.text_input(
        "Name", key=f"{entity}_name_field", args=([f"{entity}_name_field"])
    )
    password = st.text_input(
        "Password", type="password", key=f"{entity}_password_field"
    )


def add_student(entity, update=False):
    demos = (
        "sex",
        "age",
        "address",
        "Medu",
        "Fedu",
        "Mjob",
        "Fjob",
        "reason",
        "guardian",
        "traveltime",
        "studytime",
        "activities",
        "higher",
        "health",
        "wassce",
    )

    st.subheader(f"Basic {entity} Information")
    name = st.text_input(f"{entity} Name", key=f"{entity}_name_field")
    col1, col2 = st.columns(2)
    with col1:
        id = st.text_input(f"{entity} ID", key=f"{entity}_id_field", disabled=update)
        program = st.selectbox("Programme", PROGRAMMES, key=f"{entity}_program_field")

        
    with col2:
        password = st.text_input(
            "Password", type="password", key=f"{entity}_password_field"
        )
        level = st.selectbox("Level", SEMESTERS, key=f"{entity}_level_field")
    possible_courses = list(
        Course.filter(
            Course.semester == level
            and (Course.school == SCHOOL_PROGRAMS[program] | Course.school == "GENERAL")
        ).dicts()
    )
    possible_courses
    #basket = st.multiselect(
    #    "Course Basket", possible_courses, key=f"{entity}_basket_field"
    #)

    st.subheader(f"{entity} Demographic Information")
    demoa, demob, democ = st.columns(3)
    with demoa:
        sex = st.selectbox(
            "Sex", get_list("sex", dictionaries), key=f"{entity}_sex_demo"
        )
        Medu = st.selectbox(
            "Mother's Education",
            get_list("Medu", dictionaries),
            key=f"{entity}_Medu_demo",
        )
        Fedu = st.selectbox(
            "Father's Education",
            get_list("Fedu", dictionaries),
            key=f"{entity}_Fedu_demo",
        )

    with demob:
        address = st.selectbox(
            "Address", get_list("address", dictionaries), key=f"{entity}_address_demo"
        )
        Mjob = st.selectbox(
            "Mother's Job", get_list("Mjob", dictionaries), key=f"{entity}_Mjob_demo"
        )
        Fjob = st.selectbox(
            "Father's Job", get_list("Fjob", dictionaries), key=f"{entity}_Fjob_demo"
        )

    with democ:
        age = st.number_input("Age", 15, 60, key=f"{entity}_age_demo")
        reason = st.selectbox(
            "Reason for choosing school",
            get_list("reason", dictionaries),
            key=f"{entity}_reason_demo",
        )
        guardian = st.selectbox(
            "Proper Guardian",
            get_list("guardian", dictionaries),
            key=f"{entity}_guardian_demo",
        )

    traveltime = st.selectbox(
        "How far is student from school?",
        get_list("traveltime", dictionaries),
        key=f"{entity}_traveltime_demo",
    )
    studytime = st.selectbox(
        "How long does student study?",
        get_list("studytime", dictionaries),
        key=f"{entity}_studytime_demo",
    )
    activities = st.radio(
        "Extracurricular Activities",
        get_list("activities", dictionaries),
        key=f"{entity}_activities_demo",
    )
    higher = st.radio(
        "Does the student plan on furthering his education?",
        get_list("higher", dictionaries),
        key=f"{entity}_higher_demo",
    )
    health = st.slider("Current Health Status", 1, 10, key=f"{entity}_health_demo")
    wassce = st.number_input("WASSCE Grade", 8, 72, key=f"{entity}_wassce_demo")

    a, b, c = st.columns([2, 1, 2])


def add_lecturer(entity, update=False):
    name = st.text_input(f"{entity} Name", key=f"{entity}_name_field")
    id = st.text_input(f"{entity} ID", key=f"{entity}_id_field", disabled=update)
    password = st.text_input(
        "Password", type="password", key=f"{entity}_password_field"
    )
    school = st.selectbox("Department", SCHOOLS, key=f"{entity}_school_field")
    possible_courses = list(
        Course.filter(Course.school == school | Course.school == "GENERAL").dicts()
    )
    basket = st.multiselect(
        "Course Basket", possible_courses, key=f"{entity}_basket_field"
    )


def add_course(entity, update=False):
    id = st.text_input(f"{entity} ID", key=f"{entity}_id_field", disabled=update)
    name = st.text_input("Course Title", key=f"{entity}_name_field")
    school = st.selectbox("Select School", SCHOOLS, key=f"{entity}_school_field")
    if school:
        lecturers = [
            i.name
            for i in list(Lecturer.select().where(Lecturer.school == school).execute())
        ]
        lecturers.sort()
        semester = st.selectbox(
            "Select Semester", SEMESTERS, key=f"{entity}_semester_field"
        )
        if update:
            assigned = st.selectbox(
                "Lecturer", ["Unassigned"] + lecturers, key=f"{entity}_lecturer_field"
            )

def add_gradesheet(entity, update=False):
        a,b = st.columns([3,2])
        c,d,e = st.columns(3)
        try:
            with a:
                
                    if update:
                        id = st.text_input(f"Student ID", key=f"{entity}_id_field", disabled=update)

                    else:
                        students =  [i.id for i in list(Student.select())]
                        id = st.selectbox(f"Student ID",students , key=f"{entity}_id_field")
                
                    
            with b:
                if update:
                    course = st.text_input("Course Title", key=f"{entity}_course_code_field", disabled = update)
                else:
                    course = st.selectbox("Course Title", [i.id for i in list(Course.select())], key=f"{entity}_course_code_field")
                    
                    
            with c:
                midscore = st.number_input('Midscore',min_value= -1.0, key=f"{entity}_mid_score_field")
            with d:
                midpart = st.number_input('Mid Participation Score', -1.0, key=f"{entity}_mid_participation_score_field")
            with e:
                midlab = st.number_input('Mid Lab Score', -1.0, key=f"{entity}_mid_lab_score_field")
            assigned = st.selectbox(
                    "Final Grade", ["None"] + GRADES, key=f"{entity}_final_grade_field"
                )
        except:
                pass

def assign_values(entity_title, entity):
    
    for key in ENTITY_KEYS[entity_title]:

        field_name = f"{entity_title}_{key}_field"
     
        if field_name in session:
            val = eval(f"entity.{key}")
            if 'score' in key and val == None:
                    session[field_name] = -1.0
            
            elif key == 'final_grade'  and (val == None or val == "nan" or val=='None'):
                    session[field_name] = "None"

            else:
                session[field_name] = eval(f"entity.{key}")

        if key == "demographics":
            for key in dictionaries.keys():
                try:
                    session[f"{entity_title}_{key}_demo"] = entity.demographics[key]
                except KeyError:
                    if key in training_keys:
                        entity.demographics[key] = 1
                        session[f"{entity_title}_{key}_demo"] = entity.demographics[key]


    

def set_values(entity, user):
    if user:
        assign_values(entity, user)

    mode = "Update" if user else "Add New"
    func = save_user if user else create_user

    return mode, func


def get_list(key, data):
    return [i.title() for i in data[key]]


def clear_fields(entity):
    for key in ["id", "name"]:
        field_name = f"{entity}_{key}_field"
        if field_name in session:
            if isinstance(session[field_name], str):
                session[field_name] = ""


def title_text(key):
    session[f"{key}_id_field"] = session[f"{key}_name_field"].title()


def upper_id(key):
    session[f"{key}_id_field"] = session[f"{key}_id_field"].upper()


# ----------------Database Functions-----------#
def create_user(entity_title, entity={}):
    for key in ENTITY_KEYS[entity_title]:
        if key == "name":
            title_text(entity_title)

        elif key == "id":
            upper_id(entity_title)

        elif key == "demographics":
            d = {}
            for key in dictionaries.keys():
                d[key] = session[f"{entity_title}_{key}_demo"]
            entity["demographics"] = d

        field_name = f"{entity_title}_{key}_field"
        if field_name in session:
            entity[key] = session[field_name]

        if key == "program":
            entity["school"] = SCHOOL_PROGRAMS[entity[key]]

        if 'score' in key and entity[key]<0:
                entity[key] = None

        if key == 'final_grade' and (entity[key]=='nan' or entity[key]=='None'):
                entity[key] = None

    entity["role"] = entity_title
    entity['basket'] = []
    entity['lecturer'] = 'Unassigned'
    try:
        entry = ''
        if not entity["id"]:
            raise ValueError
        
        if entity_title == 'Gradesheet':
            try:
                entry = Gradesheet.get(
                            Gradesheet.id == entity["id"].upper(),
                            Gradesheet.course_code == entity["course_code"].upper()
                            )
                update_entity(entry, **entity)
            except DoesNotExist:
                create_entity(ENTITIES[entity_title], **entity)
            
            
        else:
            create_entity(ENTITIES[entity_title], **entity)

        clear_fields(entity_title)
        st.success("User created successfully")
    except IntegrityError:
        st.error(f"{entity_title} ID already exists")
    except TypeError as e:
        st.error(e.args)
    except ValueError:
        st.error("ID is not valid")
    

def save_user(entity_title, entity={}):
    try:
        for key in ENTITY_KEYS[entity_title]:
            if key == "name":
                title_text(entity_title)

            elif key == "id":
                upper_id(entity_title)

            field_name = f"{entity_title}_{key}_field"

            if field_name in session:
                entity[key] = session[field_name]
            if key == "program":
                entity["school"] = SCHOOL_PROGRAMS[entity[key]]
                
                    
            if key == "demographics":
                d = {}
                for i in dictionaries.keys():
                    if i =='health':
                        st.write('here')
                    d[i] = session[f"{entity_title}_{i}_demo"]
                entity["demographics"] = d
        
            if 'score' in key and entity[key]<0:
                entity[key] = None

            if key == 'final_grade' and (entity[key]=='nan' or entity[key]=='None'):
                entity[key] = None
                

        model = ENTITIES[entity_title]
        
        update_entity(model.get(model.id == entity["id"]), **entity)
        st.success("User saved")

    except DoesNotExist:
        st.info('Please Try Again')

def add_csv(data):
    file = st.file_uploader(f"Upload {data} Data", type=["csv"])
    func = ENTITY_CHECKS[data]
    if file is not None:
        # check values
        df = pd.read_csv(file)
        df.dropna()
        try:
            df.columns = ENTITY_KEYS[data]
        except:
            pass
        drop = []
        messages = []
        df_dict = df.to_dict(orient="index")
        for i in range(len(df_dict)):
            response = func(df_dict[i])
            if response:
                drop.append(i)
                messages.append(response)

        if drop:
            bad_df = df.iloc[drop]
            bad_df["warnings"] = messages
            bad_df.index = drop
            df.drop(drop, axis=0, inplace=True)

            st.error("Please revise the following rows and re-upload")
            st.write(bad_df)

        # output data display_data:
        else:
            st.write(df)
            st.success("All Good!")
            df_dict = df.to_dict(orient="index")

            if st.button("Upload"):
                for i in range(len(df_dict)):
                    df_dict[i]["id"] = df_dict[i]["id"].upper()
                    ent = ENTITIES[data]
                    try:
                        entry = ent.get(
                            ent.id == df_dict[i]["id"].upper(),
                            ent.course_code == df_dict[i]["course_code"],
                        )
                        update_entity(entry, **df_dict[i])
                    except DoesNotExist:
                        if data == "TrainingData":
                            d = {"demographics": {}}
                            for key, val in df_dict[i].items():
                                if key in gradesheet_keys:
                                    d[key] = val
                                else:
                                    d["demographics"][key] = val
                            df_dict[i] = d
                        
                        create_entity(ent, **df_dict[i])

                if data == "TrainingData":
                    with st.spinner('Training Models, Please Wait'):
                        model.train_models(ds1,'ds1_model')
                        model.train_models(ds2,'ds2_model')
                        st.balloons()
                        st.success('Models Trained')
                            
                            
                    # create_entity(ent, **df_dict[i])

                st.success("Gradesheet successfully Uploaded")

    else:
        st.warning(
            """Ensure that the data file is in CSV format.
        The training data file should be structured exactly as shown below
        \nYou can download the template file by clicking the button below"""
        )
        if data == "Gradesheet":
            temp = "gradesheet_template.csv"
        elif data == "TrainingData":
            temp = "trainingdata_template.csv"

        df = pd.read_csv(temp)
        st.dataframe(df, width=1000)
        with open(temp) as f:
            st.download_button("Download Template", f, "template/csv")

        if data == "TrainingData":
            with st.expander("Click to see csv structure and values"):

                col1, col2 = st.columns(2)
                num = 0
                for key, val in dictionaries.items():
                    col = col1 if num % 2 == 0 else col2
                    with col:
                        st.subheader(f":red[{key}]")
                        for i, j in val.items():
                            st.write(f":blue[{i}]", j)
                        num += 1


def check_demographics(data):
    pass

# --------Data Checks------#
def check_gradedata(data):
    errors = {k: [True, ""] for k in data.keys()}

    def try_convert_to_float(a):
        try:
            a = float(a)
            return a
        except:
            return False

    if type(data["id"]) != str:
        message = "ID is not valid"
        errors["id"] = [False, message]
        errors["id"] = message

    if data["course_code"].strip(0).upper() not in all_course_list:
        message = "Course not registered."
        errors["course_code"] = [False, message]

    grades = ["mid_score", "mid_participation_score", "mid_lab_score"]

  
    if isinstance(data["final_grade"], str):
        if data["final_grade"].upper().strip() not in GRADES:
            message = "Final Grade Not Acceptable."
            errors["final_grade"] = [False, message]
    
    elif isinstance(data['final_grade'],float) :
        data['final_grade'] = None

    else:
        message = "Final Grade Not Acceptable."
        errors["final_grade"] = [False, message]

    for i in grades:
        if data[i]:
            a = try_convert_to_float(data[i])
            if isinstance(a, float):
                data[i] = a
            else:
                message = f"{i.title()} is not valid."
                errors[i] = [False, message]

    error_message = ""

    for k, v in errors.items():

        if not v[0]:
            error_message += f"{v[1]}\n"

    return error_message


def admin_page():
    with st.sidebar:
        menu_options = [
            "Administrators",
            "Lecturers",
            "Students",
            "Courses",
            "---",
            "Gradesheet",
            "Training Data",
            "Generate Predictions"
        ]
        selected = option_menu(
            "Main Menu",
            menu_options,
            icons=["person-plus-fill", 'mortarboard-fill','person-badge','person-workspace','kanban', 'pencil-square','clipboard-plus'],
            menu_icon="list",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "menu-title": {"text-align": "center"},
                'container':{'background-color':'#F0F2F6'},
                "menu-icon": {"display": "None"},
            },
        )

    if selected in menu_options[:4]:
        user_submenu(selected)

    elif selected in menu_options[5:7]:
        data_submenu(selected)
    else:
        predict_submenu()
       

def predict_submenu():
    with st.sidebar:
        submenu = [f"Student", "Lecturer", "Course"]
        selected = option_menu(
            f"Prediction Options",
            submenu,
            icons=["plus", "search", 'film'],
            menu_icon="list",
            styles={
                "menu-title": {"text-align": "center", "font-size": "1em", 'font-weight':'500'},
                "menu-icon": {"display": "None"},
                'container':{'background-color':'#F0F2F6'},
                'nav-link':{'font-size':'0.8em'},
                "nav-link-selected": {"background-color": "green", 'opacity': 0.8},
            },
        )
    
    if selected == submenu[0]:
        student = st.sidebar.multiselect('Select a Student', [i.id for i in Student.select()])
        if student:
            if st.sidebar.button('Predict'):
                predictPage(student = student)

    elif selected == submenu[1]:
        lec = st.sidebar.multiselect('Select a Lecturer',[i.name for i in Lecturer.select()])
        if lec:
            if st.sidebar.button('Predict'):
                predictPage(lecturer = lec)

    elif selected == submenu[2]:
        courses = st.sidebar.multiselect('Select Course you want to predict for', [i.id for i in Course.select()])
        #run prediction here
        if courses:
            if st.sidebar.button('Predict'):
                predictPage(courses)
        if st.sidebar.checkbox('Select All Courses'):
            if st.sidebar.button('Predict'):
                predictPage()


def user_submenu(entity):
    with st.sidebar:
        submenu = [f"Add New", "VIew all"]
        selected = option_menu(
            f"{entity} Options",
            submenu,
            icons=["plus", "search", 'film'],
            menu_icon="list",
            styles={
                "menu-title": {"text-align": "center", "font-size": "1em", 'font-weight':'500'},
                "menu-icon": {"display": "None"},
                'container':{'background-color':'#F0F2F6'},
                'nav-link':{'font-size':'0.8em'},
                "nav-link-selected": {"background-color": "green", 'opacity': 0.8},
            },
        )
    ent = entity[: len(entity) - 1]
    if selected == submenu[0]:
        mainPage.info(f'From here you can add new {ent.lower()}s')
        entity_view(ent)

    elif selected == submenu[1]:
        user_data_view(ENTITIES[ent], ent.lower())


def data_submenu(entity):
    with st.sidebar:
        submenu = [f"Add New", "View all", "Visualize Data"]
        selected = option_menu(
            f"{entity} Options",
            submenu,
            icons=["plus", "search", 'film'],
            menu_icon="list",
            styles={
                "menu-title": {"text-align": "center", "font-size": "1em", 'font-weight':'500'},
                "menu-icon": {"display": "None"},
                'container':{'background-color':'#F0F2F6'},
                'nav-link':{'font-size':'0.8em'},
                "nav-link-selected": {"background-color": "green", 'opacity': 0.8},
            },
        )
    entity = entity.replace(" ", "")
    if selected == submenu[0]:
        if entity == 'Gradesheet':
            with mainPage.expander('Add Single Entry'):
                entity_view(entity)
            with mainPage.expander('Upload gradesheet as CSV'):
                add_csv(entity)
    
    elif selected == submenu[1]:
        user_data_view(ENTITIES[entity], entity.lower())

    elif selected == submenu[2]:
        dataset = generate_data(ENTITIES[entity], entity.lower())
        df = pd.DataFrame.from_dict(dataset)
        if df.empty:
            st.info('No Data Found')
        else:
            obj_cols = [col for t, col in zip(df.dtypes, df.columns) if t == 'object']
            count_cols = [i for i in df.columns]
            obj_cols.remove('id')
            count_cols.remove('id')
            hue = st.sidebar.selectbox('Generate Hue Chart for: ',obj_cols)
            countplot = st.sidebar.selectbox('Generate countplot', count_cols )
            if hue:
                generate_hue(df,hue)
            if countplot:
                generate_countplot(df,countplot)



def generate_gradesheet_model(courses=all_course_list, ids=[], lecturers = []):
    values = list(Gradesheet.select().dicts())
    dataset = []
    
    if lecturers:
        courses = []
        for id in lecturers:
            user = Lecturer.get(Lecturer.name==id)
            courses += user.basket
        
    if ids:
        values = []
        for id in ids:
            values += list(Gradesheet.select().where(Gradesheet.id == id.upper()).dicts())
        
    
    for val in list(values):
        try:
            if val['final_grade'] == 'nan':
                val['final_grade']== None
            user = Student.get(Student.id == val['id'])
            dem = user.demographics
            entry = {**val, **dem}
            dataset.append(entry)
        except DoesNotExist:
            values.remove(val)

    
    for i in list(dataset):
        if i['final_grade'] != None:
            dataset.remove(i)
        elif i['mid_score'] == None:
            dataset.remove(i)


    
    df = pd.DataFrame.from_dict(dataset)
    if dataset:
        df = df.loc[df['course_code'].isin(courses)]

    return df

def generate_data(cls, cls_string):
    if cls_string == "trainingdata":
        values = list(cls.select().dicts())
        dataset = []
        for data in values:
            entry = {}
            dem = data["demographics"].copy()
            del data["demographics"]
            entry = {**data, **dem}
            dataset.append(entry)
    else:
        dataset = list(cls.select().dicts())

    if "search_term" in session:
        search_term = session["search_term"] if dataset else None
        if search_term:
            dataset = list(
                cls.filter(
                    cls.name.contains(search_term) | cls.id.contains(search_term)
                ).dicts()
            )
    return dataset


def generate_grid(df, cls_string):
    #gd = GridOptionsBuilder.from_dataframe(df)
    #gd.configure_pagination(enabled=True)

    #if "grid_multiple_select" not in session:
        #session["grid_multiple_select"] = False

    #if session["grid_multiple_select"]:
        #gd.configure_selection(selection_mode="multiple", use_checkbox=True)
        #editable = False
    #else:
        #gd.configure_selection(selection_mode="single", use_checkbox=False)
        #editable = True

    #gd.configure_default_column(editable=editable, groupable=True)
    #gd.configure_column("id", editable=False)

    #gridOptions = gd.build()
    
    return grid_table


def change_selection():
    session["grid_multiple_select"] = session["grid_multiple_select"]


def column_selection():
    session["grid_columns_select"] = session["grid_columns_select"]


def user_data_view(cls, cls_string):
    with mainPage:
        session["selected_data"] = {}
        dataset = generate_data(cls, cls_string)

        search_term = st.text_input("Search by Name or ID", key="search_term")
        if "grid_columns_select" not in session:
            session["grid_columns_select"] = False

        if dataset:
            df = pd.DataFrame.from_dict(dataset)
            data = df
            if session["grid_columns_select"]:
                if cls_string == 'tradingdata':
                    columns = gradesheet_keys
                else:
                    columns = df.columns
                show = st.multiselect(
                    "Include/Exclude Columns", df.columns, list(columns)
                )
                data = df[show] if show else df

            
            grid_table = st.experimental_data_editor(df, key="data_editor",num_rows='dynamic')
            
            edited_table = session["data_editor"]
            
            
            if st.button('Save Changes'):
                edited_cells = edited_table['edited_cells']
                added_rows = edited_table['added_rows']
                deleted_rows = edited_table['deleted_rows']
                if edited_cells:
                    for key, val in edited_cells.items():
                        data_index, col_index =key.split(':')
                        col = list(df.columns)[int(col_index)-1]
                        if col not in ['role', 'id']:
                            data = dataset[int(data_index)-1]
                            #st.write(data_index, col_index,  col, data, val)
                            user = cls.get(cls.id == data['id'])
                            data[col] = val
                            update_entity(user, **data)

                if added_rows:
                    for row in added_rows:
                        data = {}
                        for i in ENTITY_KEYS[cls_string]:
                            data[i] = row[str(ENTITY_KEYS[cls_string].index(i))]

                        create_entity(cls, **data)
            
                        
                if deleted_rows:
                    for row in deleted_rows:
                        try:
                         if cls_string == 'gradesheet':
                             Gradesheet.delete().where((cls.id) == i['id'], cls.course_code==i['course_code']).execute()
                         else:
                             if user.id == session["current_user"].id:
                                 warning = "Cannot Delete current user"
                                 rerun = False

                             else:
                                 user.delete_instance()
                        except:
                            warning = warning if warning else "User Not Found"
                            st.warning(warning)
            
            

            #selected_rows = grid_table["selected_rows"]

            st.sidebar.write("\n\n\n\n\n\n\n")
            st.sidebar.subheader("Table Options")
            st.sidebar.checkbox(
                "Select Multiple",
                key="grid_multiple_select",
                on_change=change_selection,
            )
            columns_check = st.sidebar.checkbox(
                "Include/Exclude Columns",
                key="grid_columns_select",
                on_change=column_selection,
            )
            
         #if selected_rows:
         #    primary_key = "id"
         #    if len(selected_rows) == 1:
         #        user = cls.get(cls.id == selected_rows[0][primary_key])
         #        if st.sidebar.checkbox('Edit'):
         #                if cls_string != "trainingdata":
         #                    entity_view(cls_string.title(), user)

         #    if st.sidebar.button("Delete Selected Data"):
         #        warning = ""
         #        for i in selected_rows:
         #            try:
         #                if cls_string == 'gradesheet':
         #                    Gradesheet.delete().where(eval(f"cls.{primary_key}") == i[primary_key], cls.course_code==i['course_code']).execute()
         #                else:
         #                    if user.id == session["current_user"].id:
         #                        warning = "Cannot Delete current user"
         #                        rerun = False

         #                    else:
         #                        user.delete_instance()

         #                rerun = True
         #                st.success("User Deleted Successfully")

         #            except:
         #                warning = warning if warning else "User Not Found"
         #                st.warning(warning)
         #                rerun = False

         #        if rerun:
         #            dataset = generate_data(cls, cls_string)
         #            df = pd.DataFrame.from_dict(dataset)
         #            del grid_table
         #            session["grid"] = generate_grid(df, cls_string)
         #with st.sidebar.expander("Delete All Data"):
         #    rerun = False
         #    response = st.button('Confirm Deletion')
         #    if response:
         #        cls.delete().execute()
         #        st.success('All Data Deleted')
                

        # st.write(grid_table["selected_rows"])

        else:
            st.info("No Data Found")


def generate_countplot(data,header):
        fig = plt.figure(figsize=(10, 4))
        sns.countplot(x=header, data= data)
        st.pyplot(fig)

def generate_hue(data,header):
    fig = plt.figure(figsize=(10, 4))
    sns.countplot(x='final_grade',hue=header,data=data)
    st.pyplot(fig)

def predictPage(courses=all_course_list, student = [], lecturer = []):
            #run prediction model here
            if student:
                id_list = [i for i in student]
                df=generate_gradesheet_model(ids = id_list)
            elif lecturer:
                id_list = [i for i in lecturer]
                df=generate_gradesheet_model(lecturers= id_list)
            else:
                df = generate_gradesheet_model(courses)
            if not df.empty:
                if df['mid_participation_score'].isnull().any() or df['mid_lab_score'].isnull().any():
                    predictor= model.load_model('ds1_model')
                    keys = ds1
            
                else:
                    predictor= model.load_model('ds2_model')
                    keys = ds2
                
                if predictor:
                    df2 = df.copy()
                    df2.drop( [i for i in df.columns if i not in keys],axis=1, inplace=True)
                    for i in model.categorical_columns:
                        for k,v in dictionaries[i].items():
                                df2[i] = df2[i].apply(lambda x:x.lower() if isinstance(x,str) else x)
                                df2[i] = df2[i].apply(lambda x: v if isinstance(x,str) and k in x else x)
                    # Create a ColumnTransformer to handle the categorical variables
                    predictions = []
                    for i in range(len(df2)):
                        row = df2.iloc[i, :]
                    # Use the transform method of the ColumnTransformer to convert the selected row
                        data = row.to_numpy().reshape(1, -1)
                        prediction = model.predict(predictor,data)
                        predictions.append(prediction[0])
                    
                    #df = df[list(gradesheet_keys)]
                    df['Predicted Grade'] = predictions
                    
                    if len(predictions) == 1:
                        generate_report(df)
                    else:
                        
                        show = list(gradesheet_keys)
                        data = df[show+['Predicted Grade']] if show else df
                        a,b,c = st.columns([1,8,1])
                        with b:
                            st.subheader('Predicted Results Per Your Selection')
                            st.dataframe(data.style.apply(highlight_survived, axis=1))
                            #st.dataframe(data.style.applymap(color_survived, subset=['Predicted Grade']))
                        
                            csv = convert_df(data)
                            st.download_button(
                                label = "Download Report",
                                data = csv,
                                file_name=f"report.csv",
                                mime = 'text/csv'
                            )
                        st.balloons()
            else:   
                st.info("No Data For this User")

def highlight_survived(s):
    return ['background-color: green; color:white']*len(s) if s['Predicted Grade'] in UPPER_GRADES else ['background-color: red; color:white']*len(s)

def color_survived(val):
    color = '#0f0a' if val else 'red'
    return f'background-color: {color}'

def predict_student(student):
    generate_gradesheet_model(student['basket'], student['id'])


ENTITY_VIEWS = {
    ENTITY[0]: add_admin,
    ENTITY[1]: add_lecturer,
    ENTITY[2]: add_student,
    ENTITY[3]: add_course,
    ENTITY[4]: add_gradesheet
}

def lecturer_page():
    with st.sidebar:
        menu_options = [
            "Dashboard",
            "Predictions",
        ]
        selected = option_menu(
            "Main Menu",
            menu_options,
            icons=["person-plus-fill",'kanban'],
            menu_icon="list",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "menu-title": {"text-align": "center"},
                'container':{'background-color':'#F0F2F6'},
                "menu-icon": {"display": "None"},
            },
        )



ENTITY_CHECKS = {ENTITY[4]: check_gradedata, ENTITY[5]: check_demographics}


def generate_report(data):
    
    # Check if the input is a pandas DataFrame
    if not isinstance(data, pd.DataFrame):
        st.error("Input is not a pandas DataFrame")
        return

    # Check if the required columns are present in the DataFrame
    required_columns = [
        "id",
        "course_code",
        "mid_score",
        "mid_participation_score",
        "mid_lab_score",
        "sex",
        "age",
        "address",
        "Medu",
        "Fedu",
        "Mjob",
        "Fjob",
        "reason",
        "guardian",
        "traveltime",
        "studytime",
        "activities",
        "higher",
        "health",
        "wassce",
        "Predicted Grade"
    ]
    for col in required_columns:
        if col not in data.columns:
            st.error(f"Column '{col}' not found in the input DataFrame")
            return

    # Check if the input data is for a single student or multiple students
    if data["id"].nunique() == 1:
        # Input data is for a single student
        student_id = data["id"].iloc[0]


        # Show the demographic factors
        st.header(f':blue[{student_id}]')
        st.subheader(":blue[Demographic Information]")
        demographic_factors = [
            "sex",
            "age",
            "address",
            "Medu",
            "Fedu",
            "Mjob",
            "Fjob",
            "reason",
            "guardian",
            "traveltime",
            "studytime",
            "activities",
            "higher",
            "health",
            "wassce"
        ]
        with st.expander('Show Demographic information'):
            col1, col2,col3  = st.columns(3)
            for c,factor in enumerate(demographic_factors):
                if c % 3 == 0:
                    col = col1
                elif c % 3 == 1:
                    col = col2
                else:
                    col = col3
                with col:
                    disp = factor.title().replace('_',' ')
                    
                    new_title = f"""
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

                    <div class="row">
                        <div class="col-sm-3">
                        <h6 class="mb-0 text-danger">{disp}:</h6>
                        </div>
                        <div class="col-sm-9 text-success">
                        {data[factor].iloc[0]}
                        </div>
                    </div>
                    <hr>
                """
                    st.markdown(new_title, unsafe_allow_html=True)

        # Show the predicted grades for each course
        st.subheader("Predicted Grades:")
        st.write(data[["course_code", "Predicted Grade"]])

    # Add a download button for the report
    csv = convert_df(data)

    st.download_button(
        label = "Download Report",
        data = csv,
        file_name=f"{student_id}_report.csv",
        mime = 'text/csv'
        )

def lecturer_dashboard():

    st.header(f"{session['current_user'].name}, Welcome to your dashboard ")
    st.write("Here you can view all the courses you're currently taking and predict grades.")

    # Get the list of courses
    courses = session['current_user'].basket
    
    with st.expander('Active Courses'):
        st.subheader('Active Courses')
        for i in courses:
            st.checkbox(i, key=i)
    
    predict = []
    for i in courses:
        if i in session:
            if session[i]:
                predict.append(i)
    
    if predict and st.button('Make Predictions'):
        predictPage(predict)
    

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

# Create the student dashboard
def student_dashboard(student ):
    # Select the student
    # Generate the report
    predictPage(student=[student.id])


if __name__ == "__main__":
    assign_courses_to_lec()
    assign_courses_to_students()
    all_course_list = [i.id for i in Course.select()]
    all_students_list = [i.id for i in Student.select()]
    all_lecturer_list = [i.name for i in Lecturer.select()]
    current_user = None
    if "main_page" not in session:
        session["main_page"] = None

    if "subpage" not in session:
        session["subpage"] = None

    if "current_user" in session:
        current_user = session["current_user"]
        if current_user.role == "Student":
            html =f"""
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
             <div class="card">
                <div class="card-body">
                  <div class="d-flex flex-column align-items-center text-center">
                    <img src="https://bootdey.com/img/Content/avatar/avatar7.png" alt="Admin" class="rounded-circle" width="150">
                    <div class="mt-1">
                      <h4>{current_user.name}</h4>
                      <p class="text-secondary  fw-bold mb-1">{current_user.role}</p>
                      <p class="text-muted font-size-sm">{current_user.school}</p>
                    </div>
                  </div>
                </div>
              </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            student_dashboard(current_user)
            pass

        elif current_user.role == "Administrator":
            html =f"""
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
             <div class="card">
                <div class="card-body">
                  <div class="d-flex flex-column align-items-center text-center">
                    <img src="https://bootdey.com/img/Content/avatar/avatar7.png" alt="Admin" class="rounded-circle" width="150">
                    <div class="mt-1">
                      <h4>{current_user.name}</h4>
                      <p class="text-secondary  fw-bold mb-1">{current_user.role}</p>
                    </div>
                  </div>
                </div>
              </div>
            """
            st.sidebar.markdown(html, unsafe_allow_html=True)
            admin_page()

        elif current_user.role == "Lecturer":
            lecturer_dashboard()
            
    else:
        login_page()

# create a string of HTML and CSS
