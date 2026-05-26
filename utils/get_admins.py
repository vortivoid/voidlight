def get_admins() -> list | None:
    admin_list: list = []
    try:
        with open("admins.txt", "r") as file:
            try:
                admin_list = [int(line.strip()) for line in file.readlines()]
            except ValueError:
                print("Invalid admin ID found!")
                return None
    except FileNotFoundError:
        print("Could not locate file!")
        return None
    return admin_list