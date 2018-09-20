import pyodbc
import Class_Files.MyInput

def GetStudentDataWithSQLQuery(connection):
    studentList = []

    cur = connection.cursor()
    cur.execute("select * from Students")

    for row in cur:
        studentList.append(row)

    return studentList

def GetStudentsWithSQLQuery(connection, pauseProgramExecution = False, showStudentID = False):
    studentList = GetStudentDataWithSQLQuery(connection)

    print("")
    print("Data hentet ud med 'Normal' SQL Query")
    print("")

    for row in studentList:
        if True == showStudentID:
            print("Student Navn : %s med StudentID : %d er %2.2f år gammel" % (row.StudentName, row.StudentID, row.StudentAge))
        else:
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
    studentListStoredProcedure = []

    curStoredProcedure = connection.cursor()
    curStoredProcedure.execute("execute Student_All_Stored_Procedure @StudentID = %d" % StudentID)

    print("")
    print("Data hentet ud med SQL Stored Procedure Query")
    print("")

    for row in curStoredProcedure:
        print("Student Navn : %s er %2.2f år gammel og har dette fag : %s med karakteren %d" % (
        row.StudentName, row.StudentAge, row.CourseName, row.Character))
        studentListStoredProcedure.append(row)

    curStoredProcedure.close()

    if True == pauseProgramExecution:
        print("")
        input("Tryk tast for videre programafvikling !!!")

    return studentListStoredProcedure

def GetCourses(connection, pauseProgramExecution = False, showCourses = True):
    curCourses = connection.cursor()
    curCourses.execute("Select * from Courses")
    courseList = []

    for row in curCourses:
        courseList.append(row)

    curCourses.close()

    if True == showCourses:
        print("")
        print("Liste af Fag")
        for row in courseList:
            print("%d : %s" % (row.CourseID, row.CourseName))
        print("")

    return courseList

def GetCourseID(connection, studentID, pauseProgramExecution = False):
    courseList = GetCourses(connection, pauseProgramExecution = False, showCourses = False)
    print("")
    thisStudentCourseList = GetStudentsWithSQLStoredProcedureQuery(connection, studentID)

    courseID = 0
    courseIDReturnValue = 0

    for row in thisStudentCourseList:
        print("%d : %s" % (row.CourseID, row.CourseName))
    print("")

    while True:
        breakSet = False
        courseID = Class_Files.MyInput.MyInput_Class.InputInt(
            "Indtast CourseID nummer : " )

        if 0 == courseID:
            break

        for courseIDReturnValue, d in enumerate(courseList):
            if d[0] == courseID:
                breakSet = True

        if True == breakSet:
            break

    if courseID > 0:
        return courseID
    else:
        return 0

def InsertStudentAndStudentCoursesInDatabase(connection):
    print("")

    print("Nu indsætter vi en elev i databasen")
    print("")

    courseList = GetCourses(connection, pauseProgramExecution = False)

    studentName = input("Indtast elev navn : ")
    studentAge = Class_Files.MyInput.MyInput_Class.InputFloat("Indtast elev alder : ")

    studentCourseCharacterList = []
    courseCounter = 0

    while True:
        studentCharacter = -1
        courseID = Class_Files.MyInput.MyInput_Class.InputInt(
            "Indtast Fag nummer (0 afslutter) (1 - %d) : " % (len(courseList)))
        if courseID > 0 and courseID <= len(courseList):
            courseCharacter = Class_Files.MyInput.MyInput_Class.InputInt("Indtast Fag karakter : ")
        # Konstruktionen her er lidt "risky", idet vi antager, at CourseID har fortløbende
        # værdier fra 1 og opefter i Courses tabellen i databasen. Dette skal/bør vi ændre
        # i version 2 af vores program !!!

        if courseID == 0:
            break
        else:
            if courseID > 0 and courseID <= len(courseList):
                studentCourseCharacterList.append([]);
                studentCourseCharacterList[courseCounter].append(0)
                # Vi kender ikke StudentID på nuværende tidspunkt. Så vi sætter den til 0 for alle fag.
                studentCourseCharacterList[courseCounter].append(courseID)
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

    curInsertStudentCourseCharacterRelations = connection.cursor()
    sqlLine = "insert into StudentCourseCollection(StudentID, CourseID, Character) VALUES(?, ?, ?)"

    try:
        numberOfRows = curInsertStudentCourseCharacterRelations.executemany(sqlLine, studentCourseCharacterList)
        connection.commit()
    except AttributeError:
        studentID = 0
        print("Fejlen er : %s" % AttributeError)

    curInsertStudentCourseCharacterRelations.close()

def UpdataStudentCharacters(connection):
    print("")
    print("Nu skal vi ændre en karakter for en studerende")
    print("")
    studentList = GetStudentsWithSQLQuery(connection, pauseProgramExecution=False, showStudentID=True)
    courseID = 0

    print("")
    studentID = 0
    studentIDReturnValue = -1

    while True:
        breakSet = False
        studentID = Class_Files.MyInput.MyInput_Class.InputInt(
            "Indtast StudentID nummer (0 afslutter) : " )
        for studentIDReturnValue, d in enumerate(studentList):
            if d[0] == studentID:
                breakSet = True

        if True == breakSet:
            break

    if studentID > 0:
        courseID = GetCourseID(connection, studentID, pauseProgramExecution = False)

        courseCharacter = Class_Files.MyInput.MyInput_Class.InputInt("Indtast ny karakter for Fag : ")

        curUpdateStudentCharacter = connection.cursor()

        sqlLine = "update StudentCourseCollection SET Character = ? WHERE StudentID = ? AND CourseID = ?"

        numberOfRows = curUpdateStudentCharacter.execute(sqlLine, courseCharacter, studentID, courseID)
        connection.commit()

    return studentID


if __name__ == '__main__':
    studentID = 0

    con = pyodbc.connect("Driver={SQL Server};server=PCM15715\SERVER1;database=H5ID080118;uid=sa;pwd=Buchwald_34")

    studentList = GetStudentsWithSQLQuery(con, pauseProgramExecution = True)

    GetStudentsWithSQLViewQuery(con)

    for row in studentList:
        GetStudentsWithSQLStoredProcedureQuery(con, row.StudentID)

    InsertStudentAndStudentCoursesInDatabase(con)

    GetStudentsWithSQLQuery(con, pauseProgramExecution = True)

    for row in studentList:
        GetStudentsWithSQLStoredProcedureQuery(con, row.StudentID)

    studentID = UpdataStudentCharacters(con)
    print("")
    print("Student data efter opdatering")
    GetStudentsWithSQLStoredProcedureQuery(con, studentID)

    con.close()
