import streamlit as st
from db import *
import pandas as pd
from st_aggrid import AgGrid, JsCode, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(page_title='APS',page_icon=":guardsman:", layout="wide")
session = st.session_state
mainSection = st.empty()
grid, edit = mainSection.columns([3, 1])
warningSection = st.empty()
ENTITIES = {
    'Administrator': Administrator,
    'Lecturer': Lecturer,
    'Student': Student
}

SCHOOL_PROGRAMS = {
    "Business Administration": "ABS",
    "Computer Science & IT": "ASSDAS",
    "Engineering": "SATES"
}

lec_keys = ('id', 'name', 'password', 'role', 'school', 'basket')
student_keys = ('id', 'name', 'password', 'role', 'program',
                'school', 'level', 'demographics', 'basket')
admin_keys = ('id', 'name', 'password', 'role')
course_keys = ('code', 'title', 'school', 'semester', 'lecturer')
gradesheet_keys = ('id', 'course_code', 'mid_score', 'mid_participation_score', 'mid_lab_score', 'final_grade')

# ------------LOGIN FUNCTIONS --------------#


def login_page():
    with mainSection.container():
        st.title("Login")
        id = st.text_input("ID")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Select Role",
                            ["Administrator", "Lecturer", "Student"])

        if st.button("Submit"):
            if id and password and role:
                # authenticate user here
                user = authenticate_user(id, password, role)
                if user:
                    session['current_user'] = user
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

    user = cls.select().where(cls.id == id,
                              cls.password == password)
    if user:
        return user.get()

    return None


def logout():
    # logic to log out the user and redirect to the login page
    session['current_user'] = None
    login_page()

# -------------ADMINISTRATOR PAGES--------------#


def admin_page():
    menus = ["Dashboard", "User Management",
             "Course Management", "Data Management", "Logout"]
    admin_pages = {
        menus[0]: {
        },
        menus[1]: {},
        menus[2]: {},
        menus[3]: {},
    }
    with mainSection.container():
        current_user = session['current_user']
        st.title("Admin Dashboard")

        option = st.sidebar.selectbox(
            "Select an option",
            menus, menus.index(session['main_page']) if session['main_page'] else 0)

        if option == menus[0]:
            session["main_page"] = menus[0]
            st.subheader("Welcome to the dashboard")
            # display dashboard statistics

        elif option == menus[1]:
            session['main_page'] = menus[1]
            user_management()

        elif option == menus[2]:
            course_management()
            # display options to manage data
            pass
        elif option == menus[3]:
            st.subheader("Data Management")
            data_management()
            

        else:
            logout()

# ----------User Management----------------#


def admin_CRUD():
    st.subheader("Admin CRUD")
    # CRUD operations for students here
    submenus = ['Add New Administrator', 'View All Administrators']
    add = st.sidebar.button(
        submenus[0], submenus[0], type="primary", on_click=set_subpage, args=([submenus[0]]))
    view = st.sidebar.button(
        submenus[1], submenus[1], type="primary", on_click=set_subpage, args=([submenus[1]]))
    st.write(session['subpage'])
    # Create New Student
    if session['subpage'] == submenus[0]:
        with st.form('Add New Lecturer', True):
            name = st.text_input("Name")
            id = st.text_input("Administrator ID")
            password = st.text_input("Password", type='password')
            submit = st.form_submit_button('Add Administrator')

            if submit:
                # Conduct checks on the data
                if check_data(id, password):
                    Administrator.create(
                        id=id, password=password, name=name.title(), role='Administrator')
                    st.success('Administrator Created Successfully')
                else:
                    st.warning('Please ensure that ID and Password are valid')

    if session['subpage'] == submenus[1]:
        user_data_view(Administrator, 'admin')


def admin_view(admin):
    with st.form('Edit Admin Details', True):
        st.subheader('Administrator Information')
        name = st.text_input("Name", admin.name)
        password = st.text_input("Password", admin.password, type='password')
        submit = st.form_submit_button('Submit')
        if submit:
            values = [admin.id, name, password, admin.role]
            values_dict = distribute(admin_keys, values, True)
            save_user(admin_page, **values_dict)
            st.success("Saved")


def change_selection():
    session['grid_multiple_select'] = session['grid_multiple_select']
    st.write('')


def change_grid(cls, cls_string):
    dataset = generate_data(cls, cls_string)
    df = pd.DataFrame.from_dict(dataset)
    del grid_table
    session['grid'] = generate_grid(df, cls_string)


def check_data(*args):
    for i in args:
        if not i:
            return False
    return True


def confirm_delete():
    with st.sidebar.container():
        st.warning('Are you sure you want to delete all data')
        space1, yes, no, space2 = st.columns([1, 2, 2, 1])
        with yes:
            if st.button('Yes', type='primary'):
                return True
        with no:
            if st.button('No', type='primary'):
                return False


def distribute(keys, values, dictionary=False, array=False):
    if dictionary:
        values_dict = {}
        for i in range(len(keys)):
            values_dict[keys[i]] = values[i]

        return values_dict


def generate_data(cls, cls_string):
    dataset = list(cls.select().dicts())
    if 'search_term' in session:
        search_term = session['search_term'] if dataset else None
        if search_term:
            if cls_string == 'course':
                dataset = list(cls.filter(cls.code.contains(
                    search_term) | cls.title.contains(search_term)).dicts())
            else:
                dataset = list(cls.filter(cls.name.contains(
                    search_term) | cls.id.contains(search_term)).dicts())
    return dataset


def generate_grid(df, cls_string):
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)

    if 'grid_multiple_select' not in session:
        session['grid_multiple_select'] = False

    if session['grid_multiple_select']:
        gd.configure_selection(selection_mode="multiple", use_checkbox=True)
        editable = False
    else:
        gd.configure_selection(selection_mode="single", use_checkbox=False)
        editable = True

    gd.configure_default_column(editable=editable, groupable=True)
    if cls_string == 'course':
        gd.configure_column('code', editable=False)
    else:
        gd.configure_column('id', editable=False)

    gridOptions = gd.build()
    grid_table = AgGrid(df,
                        gridOptions=gridOptions,
                        fit_columns_on_grid_load=True,
                        height=500,
                        width='100%',
                        theme="streamlit",
                        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED | GridUpdateMode.GRID_CHANGED,
                        reload_data=editable,
                        allow_unsafe_jscode=True,
                        editable=editable,
                        enable_enterprise_modules=False
                        )

    return grid_table


def lecturer_CRUD():
    st.subheader("Lecturer CRUD")
    # CRUD operations for lecturers here
    # CRUD operations for students here
    submenus = ['Add New Lecturer', 'View All Lecturers']
    add = st.sidebar.button(
        submenus[0], submenus[0], type="primary", on_click=set_subpage, args=([submenus[0]]))
    view = st.sidebar.button(
        submenus[1], submenus[1], type="primary", on_click=set_subpage, args=([submenus[1]]))
    st.write(session['subpage'])

    # Create New Student
    if session['subpage'] == submenus[0]:
        with st.form('Add New Lecturer', True):
            name = st.text_input("Name")
            id = st.text_input("Lecturer ID")
            password = st.text_input("Password", type='password')
            school = st.selectbox('Department', SCHOOLS)
            submit = st.form_submit_button('Add Lecturer')

            if submit:
                # Conduct checks on the data
                if check_data(id, password):
                    Lecturer.create(id=id, password=password, name=name.title(
                    ), role='Lecturer', school=school, basket=[])
                    st.success('Lecturer Created Successfully')
                else:
                    st.warning('Please ensure that ID and Password are valid')

    if session['subpage'] == submenus[1]:
        user_data_view(Lecturer, 'lecturer')


def lecturer_view(lec):
    with st.container():
        st.subheader('Lecturer Information')
        name = st.text_input("Name", lec.name, on_change=title_case, args=(
            ['change_name']), key='change_name')
        password = st.text_input("Password", lec.password, type='password')
        school = st.selectbox('Department', SCHOOLS, SCHOOLS.index(lec.school))
        courses = [i.code for i in Course.select().where(
        Course.school == school).execute()]
        possibles = lec.basket if lec.school == school else None
        basket = st.multiselect("Basket", courses, possibles)
        submit = st.button('Submit', on_click=save_user, args=([lec]), kwargs=distribute(
            lec_keys, [lec.id, name, password, lec.role, school, basket], True))


def save_user(entity, **kwargs):
    for key, val in kwargs.items():
        if key == 'name':
            val = val.title()

        elif key == 'program':
            entity.program
            val
            if entity.program != val:
                setattr(entity, key, val)

        elif key == 'level':
            if entity.level != val:
                setattr(entity, key, val)

        else:
            setattr(entity, key, val)

    entity.save()
    assign_courses_to_students()
    st.success("Saved")


def set_subpage(page):
    session['subpage'] = page


def student_CRUD():
    # CRUD operations for students here
    submenus = ['Add New Student', 'View All Students']
    add = st.sidebar.button(
        submenus[0], submenus[0], type="primary", on_click=set_subpage, args=([submenus[0]]))
    view = st.sidebar.button(
        submenus[1], submenus[1], type="primary", on_click=set_subpage, args=([submenus[1]]))

    # Create New Student
    if session['subpage'] == submenus[0]:
        with st.form('Add New Student', True):
            st.subheader("Add New Student")
            name = st.text_input("Name")
            id = st.text_input("Student ID")
            password = st.text_input("Password", type='password')
            programme = st.selectbox("Programme", PROGRAMMES)
            Level = st.selectbox("Level", SEMESTERS)
            demographics = st.text_input("Demographics")
            submit = st.form_submit_button('Add Student', type='primary')
            if submit:
                # Conduct checks on the data
                if check_data(id, password):
                    school = SCHOOL_PROGRAMS[programme]
                    student = Student.create(id=id, password=password, name=name.title(
                    ), role='Student', program=programme, school=school, level=Level, demographics=demographics, basket=[])
                    st.success('Student Created Successfully')
                else:
                    st.warning('Please ensure that ID and Password are valid')

    if session['subpage'] == submenus[1]:
        user_data_view(Student, 'student')
        pass


def student_view(student):
    form = st.container()
    form.title('Student Information')
    name = form.text_input("Name", student.name, on_change=title_case, args=(
        ['change_name']), key='change_name')
    password = form.text_input(
        "Password", student.password, type='password', key='change_password')
    program = form.selectbox("Programme", PROGRAMMES, PROGRAMMES.index(
        student.program), key='change_program')
    school = SCHOOL_PROGRAMS[program]
    form.write(f'Department: {school}')
    level = form.selectbox("Level", SEMESTERS, SEMESTERS.index(
        student.level), key='change_level')
    demographics = form.text_input("Demographics", student.demographics)
    courses = [i.code for i in Course.select().where(
        Course.school == school, Course.semester == level).execute()]
    possibles = student.basket if student.school == school and student.level == level else None
    basket = form.multiselect(
        "Basket", courses, possibles, key='change_basket')

    submit = form.button('Submit', on_click=save_user, args=([student]), kwargs=distribute(student_keys, [
                         student.id, name, password, student.role, program, school, level, demographics, basket], True))


def title_case(name):
    session[name] = session[name].title()


def user_data_view(cls, cls_string):
    with st.spinner('Please wait'):
        session['selected_data'] = {}
        dataset = generate_data(cls, cls_string)
        
        search_term = st.text_input("Search by Name or ID", key='search_term')
        grid, edit = st.columns([4, 2])
        with grid:
            if dataset:
                df = pd.DataFrame.from_dict(dataset)

                grid_table = generate_grid(df, cls_string)
                if 'grid' not in session:
                    session['grid'] = grid_table

                selected_rows = grid_table['selected_rows']

                st.sidebar.write('\n\n\n\n\n\n\n')
                st.sidebar.subheader('Table Options')
                st.sidebar.checkbox(
                    'Select Multiple', key="grid_multiple_select", on_change=change_selection)

                if selected_rows:
                    primary_key = 'code' if cls_string == 'course' else 'id'
                    if len(selected_rows) == 1:
                        with edit:
                            if cls_string == 'student':
                                user = cls.get(
                                    cls.id == selected_rows[0][primary_key])
                                student_view(user)
                            elif cls_string == 'admin':
                                user = cls.get(
                                    cls.id == selected_rows[0][primary_key])
                                admin_view(user)
                            if cls_string == 'lecturer':
                                user = cls.get(
                                    cls.id == selected_rows[0][primary_key])
                                lecturer_view(user)
                            if cls_string == 'course':
                                user = cls.get(
                                    cls.code == selected_rows[0][primary_key])
                                course_view(user)

                    if st.sidebar.button('Delete Selected Data'):
                        warning = ''
                        for i in selected_rows:
                            st.write(i)
                            try:
                                user = cls.get(eval(f'cls.{primary_key}') == i[primary_key])
                                if user.id == session['current_user'].id:
                                    warning = "Cannot Delete current user"
                                    rerun = False
                                else:
                                    user.delete_instance()
                                    rerun = True
                            except:
                                warning = warning if warning else "User Not Found"
                                st.warning(warning)
                                rerun = False

                        if rerun:
                            dataset = generate_data(cls, cls_string)
                            df = pd.DataFrame.from_dict(dataset)
                            del grid_table
                            session['grid'] = generate_grid(df, cls_string)

                if st.sidebar.button('Delete All Data'):
                    response = confirm_delete()
                    if response:
                        pass

            # st.write(grid_table["selected_rows"])

            else:
                st.info('No user found')


def user_management():
    user_types = ["Students", "Lecturers", "Administrators"]
    st.sidebar.write('\n\n\n\n\n\n')
    user_type = st.sidebar.radio("Select user type", user_types)
    st.sidebar.write('\n\n\n\n\n\n')
    if user_type == "Students":
        student_CRUD()
        pass
    elif user_type == "Lecturers":
        lecturer_CRUD()
        pass
    elif user_type == "Administrators":
        admin_CRUD()
        pass


# ---------Course Management Pages ---------#
def add_course():
    st.subheader("Add a new Course")
    code = st.text_input("Course Code")
    if code in all_course_list:
        st.error('Course already exists')
    else:   
        title = st.text_input("Course Title")
        school = st.selectbox("Select School", SCHOOLS)
        if school:
            lecturers = [i.name for i in list(
                Lecturer.select().where(Lecturer.school == school).execute())]
            lecturers.sort()
            semester = st.selectbox('Select Semester', SEMESTERS)
            assigned = st.selectbox('Lecturer', ['Unassigned'] + lecturers)
        submit = st.button('Add Course')

        if submit:
            # Conduct checks on the data
            if check_data(code, title, school):
                assigned_val = False if assigned == 'Unassigned' else True
                
            try:
                lecturer = Lecturer.select().where(Lecturer.name == assigned).get()
                lecturer.basket.append(code.upper())
                lecturer.basket = list(set(lecturer.basket))
                st.write(lecturer.basket)
                lecturer.save()

            except:
                lecturer  = None
            
            
            course = Course.create(code=code.upper(), title=title.title(
            ), school=school, semester=semester, lecturer='Unassigned')
            
            course.lecturer = lecturer.name if lecturer else 'Unassigned'
            course.save()
            st.success('Course Created Successfully')

        else:
            st.warning('Please ensure that Course Code and Title are valid')


def change_course_lecturer(course, lec='Unassigned'):
    if lec != 'Unassigned':
        lecturer = Lecturer.get(Lecturer.name == lec)
        lecturer = lecturer.name
    else:
        lecturer = lec

    st.write(lecturer)
    course.lecturer = lecturer
    course.save()


def course_management():
    submenus = ['Add New Course', 'View All Courses']
    submenu = st.sidebar.radio('Manage Courses', submenus)
    if submenu == submenus[0]:
        session['subpage'] = submenus[0]
        add_course()
    elif submenu == submenus[1]:
        session['subpage'] = submenus[1]
        user_data_view(Course, 'course')


def course_view(course):
    with st.container():
        st.subheader(course.code)
        title = st.text_input("Course Title", course.title)
        possibles = Lecturer.select() if course.school == 'GENERAL' else Lecturer.select(
        ).where(Lecturer.school == course.school).execute()
        lecturers = [i.name for i in list(possibles)]
        lecturers.sort()
        lecturers = ['Unassigned'] + lecturers
        assigned_lecturer = Lecturer.get(
            Lecturer.name == course.lecturer) if course.lecturer != 'Unassigned' else 'Unassigned'
        lec_index = lecturers.index(
            assigned_lecturer.name) if assigned_lecturer != 'Unassigned' else 0
        assigned = st.selectbox(
            'Change Assigned Lecturer', lecturers, lec_index)

        change_school = st.checkbox('Change School')
        if change_school:
            course.school = st.selectbox(
                "Select School", SCHOOLS, SCHOOLS.index(course.school))
            st.warning("Changing a School will cancel any assignments")

        change_sem = st.checkbox('Change Semester')
        if change_sem:
            course.semester = st.selectbox(
                'Select Semester', SEMESTERS, SEMESTERS.index(course.semester))
            st.warning("Changing semester will cancel any active students")

        submit = st.button('Update Course', on_click=save_course, args=([course]), kwargs=distribute(
            course_keys, [course.code, title, course.school, course.semester, assigned], True))


def save_course(course, **kwargs):
    for key, val in kwargs.items():

        if key == 'title':
            val = val.title()
            setattr(course, key, val)
            course.save()

        if key == 'school':
            if course.school != val:
                change_course_lecturer(course)

        if key == 'semester':
            if course.semester != val:
                # remove course from each student's basket
                # exceptlthose to whom it has been manually assigned
                students = Student.filter(Student.basket.contains(
                    course.code), Student.level != course.semester)

                if students:
                    for i in students:
                        i.basket.pop(course.code)
                        i.save()
                # remove from gradesheet as well
                course.save()

        if key == 'lecturer':
            if course.lecturer != val:
                change_course_lecturer(course, val)

        if key == 'code':
            setattr(course, key, val)
            course.save()

    course.save()
    assign_courses_to_lec()
    assign_courses_to_students()
    # st.success("Course Updated")


#-------------Data Management------------#
def data_management():
    data_types = ["Gradesheet", "Training Data", "Visualization"]
    st.sidebar.write('\n\n\n\n\n\n')
    user_type = st.sidebar.radio("Select user type", data_types)
    st.sidebar.write('\n\n\n\n\n\n')
    if user_type == data_types[0]:
        gradesheet_CRUD()
        pass
    elif user_type == "Lecturers":
        lecturer_CRUD()
        pass
    elif user_type == "Administrators":
        admin_CRUD()
        pass

def check_gradedata(data):

    errors = {k:[True, ''] for k in data.keys()}
    def try_convert_to_float(a):
        try:
            a = float(a)
            return a
        except:
            return False
    
    if type(data['id']) != str:
        message = 'ID is not valid'
        errors['id'] = [False, message]
        errors['id'] = message
        


    if data['course_code'] not in all_course_list:
        message = 'Course not registered.'
        errors['course_code'] = [False, message]
    
    grades = ['mid_score', 'mid_participation_score', 'mid_lab_score']
    
    if isinstance(data['final_grade'], str):
        
        if data['final_grade'].upper().strip() not in GRADES:
            message = 'Final Grade Not Acceptable.'
            errors['final_grade'] = [False, message]
        
    else:
        message = 'Final Grade Not Acceptable.'
        errors['final_grade'] = [False, message]
        

    for i in grades:
        if data[i]:
            a = try_convert_to_float(data[i])
            if isinstance(a,float):
                data[i] = a
            else:
                message = f'{i.title()} is not valid.'
                errors[i] = [False, message]

    error_message = ''

    for k,v in errors.items():
    
        if not v[0]:
            error_message += f'{v[1]}\n'
            
    return error_message
    
    

def gradesheet_CRUD():
    #select_course
    #upload_gradesheet
    add, view = st.tabs(['Add Grades', 'View Grades'])
    with add:
        gradesheet_file = st.file_uploader("Upload Gradesheet", type=['csv'])
        
        if gradesheet_file is not None:
        #check values
            df = pd.read_csv(gradesheet_file)
            try:
                df.columns = gradesheet_keys
            except:
                pass
            drop = []
            messages = []
            df_dict = df.to_dict(orient='index')
            for i in range(len(df_dict)):
                
                response = check_gradedata(df_dict[i])
                if response:
                    drop.append(i)
                    messages.append(response)
            
            if drop:
                bad_df = df.iloc[drop]
                bad_df['messages'] = messages
                bad_df.index = drop
                df.drop(drop, axis=0, inplace=True)

                st.error('Please revise the following rows and re-upload')
                st.write(bad_df)

            #output data display_data:
            else:
                st.success('All Good!')
                df_dict = df.to_dict(orient='index')

                upload = st.button('Upload')
                if upload:
                    for i in range(len(df_dict)):
                        create_entity(Gradesheet, **df_dict[i])

        
                

            
        else:
            st.warning('''Ensure that the data file is in CSV format.
            The training data file should be structured exactly as shown below
            \nYou can download the template file by clicking the button below''')
            st.dataframe(pd.read_csv('gradesheet_template.csv'), width=1000)
            with open('gradesheet_template.csv') as f:
                st.download_button('Download Training Data Template', f, 'template/csv')

    with view:
        user_data_view(Gradesheet, 'gradesheet')


def gradesheet_view():
    pass

if __name__ == "__main__":
    current_user = None
    if 'main_page' not in session:
        session['main_page'] = None
    
    if 'subpage' not in session:
        session['subpage'] = None

    if 'current_user' in session:
        current_user = session['current_user']
        if current_user.role == "Student":
            # student_page()
            pass

        elif current_user.role == "Administrator":
            # assign_courses_to_students()
            admin_page()
            pass

        elif current_user.role == 'Lecturer':
            # lecturer_page()
            pass
    else:
        login_page()
