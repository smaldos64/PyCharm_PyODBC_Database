import pyodbc
import Class_Files.MyInput
import Class_Files.Student_Course_Character
from Class_Files.Student_Course_Character import Student_Course_Charecter_Class

def GetStudentDataWithSQLQuery(connection):
    studentList = []

    cur = connection.cursor()
    cur.execute("select * from Students")

    for row in cur:
        studentList.append(row)

    return studentList

def GetStudentsWithSQLQuery(connection, pauseProgramExecution = False):
    studentList = GetStudentDataWithSQLQuery(connection)

    print("")
    print("Data hentet ud med 'Normal' SQL Query")
    print("")

    for row in studentList:
        print("Student Navn : %s er %2.2f år gammel" % (row.StudentName, row.StudentAge))
        print("")

    if True ==  pauseProgramExecution:
        print("")
        input("Tryk tast for videre programafvikling !!!")

    return (studentList)

def GetStudentsWithSQLViewQuery(connection, pauseProgramExecution = False):
    studentList = GetStudentDataWithSQLQuery(connection)
    studentListView = []

    curView = connection.cursor()
    curView.execute("select * from Student_All_View")

    print("")
    print("Data hentet ud med SQL View Query")
    print("")

    for row in curView:
        studentListView.append(row)
        print("Student Navn : %s er %2.2f år gammel og har faget : %s med karakteren %d" %
              (row.StudentName, row.StudentAge, row.CourseName, row.Character))
        print("")

    curView.close()

    print("")
    print("Data filtreret ud fra View")
    print("")

    for row in studentList:
        print("Student Navn : %s er %2.2f år gammel og har disse fag : " % (row.StudentName, row.StudentAge))
        for row1 in studentListView:
            if row.StudentID == row1.StudentID:
                print("%s med karakter : %d" % (row1.CourseName, row1.Character))
        print("")

    if True == pauseProgramExecution:
        print("")
        input("Tryk tast for videre programafvikling !!!")

def GetStudentsWithSQLStoredProcedureQuery(connection, StudentID, pauseProgramExecution = False):
    curStoredProcedure = connection.cursor()
    curStoredProcedure.execute("execute Student_All_Stored_Procedure @StudentID = %d" % StudentID)

    print("")
    print("Data hentet ud med SQL Stored Procedure Query")
    print("")

    for row in curStoredProcedure:
        print("Student Navn : %s er %2.2f år gammel og har dette fag : %s med karakteren %d" % (
        row.StudentName, row.StudentAge, row.CourseName, row.Character))

    curStoredProcedure.close()

    if True == pauseProgramExecution:
        print("")
        input("Tryk tast for videre programafvikling !!!")

def InsertStudentAndStudentCoursesInDatabase(connection):
    print("")

    print("Nu indsætter vi en elev i databasen")
    print("")

    curCourses = connection.cursor()
    curCourses.execute("Select * from Courses")
    courseList = []

    for row in curCourses:
        courseList.append(row)

    curCourses.close()

    studentName = input("Indtast elev navn : ")
    studentAge = Class_Files.MyInput.MyInput_Class.InputFloat("Indtast elev alder : ")

    studentCourseCharacterList = []
    courseCounter = 0

    print("")
    print("Liste af Fag")
    for row in courseList:
        print("%d : %s" % (row.CourseID, row.CourseName))
    print("")

    while True:
        studentCharacter = -1
        CourseID = Class_Files.MyInput.MyInput_Class.InputInt(
            "Indtast Fag nummer (0 afslutter) (1 - %d) : " % (len(courseList)))
        if CourseID > 0 and CourseID <= len(courseList):
            courseCharacter = Class_Files.MyInput.MyInput_Class.InputInt("Indtast Fag karakter : ")

        if CourseID == 0:
            break
        else:
            if CourseID > 0 and CourseID <= len(courseList):
                studentCourseCharacterList.append([]);
                studentCourseCharacterList[courseCounter].append(0)
                # Vi kender ikke StudentID på nuværende tidspunkt. Så vi sætter den til 0 for alle fag.
                studentCourseCharacterList[courseCounter].append(CourseID)
                studentCourseCharacterList[courseCounter].append(courseCharacter)
                courseCounter += 1

    curInsertStudent = connection.cursor()
    sqlLine = "insert into Students(StudentName, StudentAge) VALUES('%s', '%f')" % (studentName, studentAge)

    numberOfRows = curInsertStudent.execute(sqlLine)
    connection.commit()

    studentID = 0
    if 1 == int(numberOfRows.arraysize):
        try:
            curInsertStudent.execute("SELECT SCOPE_IDENTITY()")
            idRow = curInsertStudent.fetchone()
            studentID = idRow[0]
        except AttributeError:
            studentID = 0

    print("Ny elev indsat med ID : %d" % studentID)

    for row in studentCourseCharacterList:
        row[0] = studentID
    # Nu kan vi indsætte den korrekte værdi for StudentID

    curInsertStudent.close()

    curInsertStudentCourseCharacterRelations = con.cursor()
    sqlLine = "insert into StudentCourseCollection(StudentID, CourseID, Character) VALUES(?, ?, ?)"

    try:
        numberOfRows = curInsertStudentCourseCharacterRelations.executemany(sqlLine, studentCourseCharacterList)
        connection.commit()
    except AttributeError:
        studentID = 0
        print("Fejlen er : %s" % AttributeError)

    curInsertStudentCourseCharacterRelations.close()



if __name__ == '__main__':
    con = pyodbc.connect("Driver={SQL Server};server=PCM15715\SERVER1;database=H5ID080118;uid=sa;pwd=Buchwald_34")

    studentList = GetStudentsWithSQLQuery(con, True)

    GetStudentsWithSQLViewQuery(con)

    for row in studentList:
        GetStudentsWithSQLStoredProcedureQuery(con, row.StudentID)

    InsertStudentAndStudentCoursesInDatabase(con)

    GetStudentsWithSQLQuery(con, True)

    con.close()
