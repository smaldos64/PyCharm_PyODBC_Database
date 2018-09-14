class MyInput_Class:
    def InputFloat(Message):
        while True:
            try:
                UserInput = float(input(Message))
            except ValueError:
                print("Du skal indtast et tal her !!!")
                continue
            else:
                return UserInput

    def InputInt(Message):
        while True:
            try:
                UserInput = int(input(Message))
            except ValueError:
                print("Du skal indtast et tal her !!!")
                continue
            else:
                return UserInput
