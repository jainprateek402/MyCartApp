import json
import copy
import sys
import traceback
from datetime import datetime
from bson import json_util


with open("config.json", "r") as f:
    config = json.loads(f.read())

def sign_in(user_type, login_id, password):

    if login_id in config[user_type]:
        print(login_id)
        if password == config[user_type][login_id]["password"]:
            return True, "Sign in successfully"
        else:
            return False, "Invalid Password Entered"
    else:
        return False, "User ID doesn't exists"

def print_there(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def save_config_into_json(config, file_name):

    with open(file_name, "w") as f:
        f.write(json.dumps(config))

    return "Success"

def validate_data_type(data, expected_type, key):
    try:
        return eval("expected_type(data)")
    except ValueError:
        print(f"Enter value of {expected_type} data type")
        return validate_data_type(input(f"{key} -> "), expected_type, key)

def validate_date_input(data, key):

    try:
        return datetime.strptime(data,"%d-%m-%Y")
    except ValueError:
        print("Invalid date entered, please enter in DD-MM-YYYY format")
        return validate_date_input(input(f"{key} -> "), key)

class AdminAccount(object):
    """docstring for UserAccount"""
    def __init__(self, user_id, password):

        self.login_status = sign_in("ADMIN", user_id, password)
        self.login = self.login_status[0]

        try:
            with open("product_config_new.json","r") as f:
                self.product_config = json.loads(f.read())
        except FileNotFoundError:
                self.product_config = {}

        try:
            with open("coupan_config_new.json","r") as f:
                self.coupan_config = json.loads(f.read())
        except FileNotFoundError:
            self.coupan_config = {}
        except json.decoder.JSONDecodeError:
            self.coupan_config = {}

    def add_category_and_item(self):

        schema = copy.deepcopy(config["product_schema"])

        for i in schema:
            schema[i] = input(f"{i} -> ")

        schema["price"] = validate_data_type(schema["price"], float, "price")

        self.product_config.update({schema["product_id"]:schema})

        save_config_into_json(self.product_config, "product_config_new.json")

    def add_coupan(self):
        schema = {}

        schema["type"] = input("type -> ")
        schema["coupan_id"] = input("coupan_id -> ")
        schema["max_usage"] = validate_data_type(input("max_usage -> "), int, "max_usage")
        schema["percentage_discount"] = validate_data_type(input("percentage_discount -> "), float, "percentage_discount")
        schema["active_flag"] = validate_data_type(input("active_flag 0 / 1 -> "), int, "active_flag")

        schema["start_date"] = validate_date_input(input("start_date -> "), "start_date")
        schema["end_date"] = validate_date_input(input("end_date -> "), "end_date")

        schema["start_date"] = schema["start_date"].timestamp()
        schema["end_date"] = schema["end_date"].timestamp()
        schema["last_applied"] = ""


        self.coupan_config.update({schema["coupan_id"]:schema})

        save_config_into_json(self.coupan_config, "coupan_config_new.json")

    def processing(self, activity, **kwargs):
        switcher = {
            1: (self.add_category_and_item, ()),
            2: (self.add_coupan, ()),
            3: (self.print_available_choices, ()),
            4: (self.logout, ())
        }

        func, args = switcher.get(activity, (None, None))
        if func is not None:
            return func(*args)
        else:
            print("Invalid activity entered")
            return None

    def print_available_choices(self):

        print("*"*70)
        print("*\t\t<< WELCOME TO ADMIN ACCOUNT >>")
        print("*"*70)
        print("*\t\t1. Add Category and Item")
        print("*\t\t2. Add New Coupan")
        print("*\t\t3. Print Available Choices")
        print("*\t\t4. Logout")
        print("*"*70)
        print("\n")

    def logout(self):
        print("You have been successfully logged out")
        self.login = False

if __name__ == '__main__':

    user_id = input("Admin Login ID -> ")
    password = input("Admin Password -> ")

    obj = AdminAccount(user_id, password)

    if not obj.login:
        print(obj.login_status[1])
        sys.exit(1)
    
    for i in range(3,10):
        print_there(i,70,"*")

    obj.processing(3)


    while obj.login:
        try:
            activity = input("Enter Activity Number from Available Choices -> ")
            obj.processing(int(activity))
            print("++"*20,"\n")
        except ValueError:
            print("Invalid value entered, please select from available options \n")
            continue

        except Exception as e:
            traceback.print_exc()
