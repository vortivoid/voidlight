def get_admins() -> list | None:
    admin_list: list = []
    try:
        with open("admins.txt", "r") as file:
            admin_list = file.readlines()
    except FileNotFoundError:
        print("Could not locate file!")
        return None
    return admin_list