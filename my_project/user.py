import json
from datetime import datetime
import pandas as pd
import sys
import copy
import traceback
from admin import save_config_into_json, print_there, sign_in




class UserAccount(object):
    """docstring for UserAccount"""

    def __init__(self, user_id, password):

        self.login_status = sign_in("USER", user_id, password)
        self.login = self.login_status[0]

        self.checkout_flag = False
        self.cart = []
        self.coupan_applied = False
        self.selected_product_id = ""
        self.coupan = ""
        self.total_amount = 0
        self.checkout_list = []
        self.discount_applied = 0

        try:
            with open("product_config_new.json", "r") as f:
                self.product_config = json.loads(f.read())
        except FileNotFoundError:
            self.product_config = {}

        try:
            with open("coupan_config_new.json", "r") as f:
                self.coupan_config = json.loads(f.read())
        except FileNotFoundError:
            self.coupan_config = {}

        self.available_pids = self.product_config.keys()

    def list_item(self):
        print("-"*25,"Available Items","-"*25)
        print(pd.DataFrame(self.product_config.values()))
        print("-"*50,"\n")

    def list_category(self):
        print(self.get_available_categories(),"\n")

    def get_available_categories(self):
        available_cats = list(set([i["category"] for i in self.product_config.values()]))
        return available_cats

    def get_all_product_under_category(self):
        category = input("Enter category -> ")

        if category not in self.get_available_categories():
            print("Available category is not available \n")
        else:
            products = list(set([i["product_name"] for i in self.product_config.values() if i["category"] == category]))
            print(products,"\n")

    def get_product_details(self, product_id=""):
        if not product_id:
            product_id = input("Enter Product ID -> ")
        print(self.product_config.get(product_id, "Wrong Product ID"),"\n")

    def add_product_to_cart(self):
        if input("Enter anyting if you want to see list or else just press enter if you know product id -> ") not in [""]:
            self.list_item()

        selected_pid = input("Enter product id to add into cart -> ")
        if selected_pid in self.available_pids:
            self.cart.append(selected_pid)
        else:
            print("Invalid Product ID provided, please select from below")
            self.add_product_to_cart()
        print(f"Item {selected_pid} has been added to cart!!!")
        self.checkout_list = self.cart

    def buy_item_from_cart(self):

        if not self.cart:
            print("No Items Available in your cart \n")
            return

        print("Below are Available Items in your cart \n")
        print(self.cart,"\n")

        self.checkout_list = copy.deepcopy(self.cart)
        
        selected_pid = input("Enter comma seperated product id to add into checkout_list -> ")
        self.checkout_list = selected_pid.split(",")
        self.checkout_list = [i.strip() for i in self.checkout_list]

    def remove_item_from_cart(self):

        if not self.cart:
            print("No Items are available in your cart\n")
            return

        print(f"Existing products in cart {self.cart}")
        selected_pid = input("Enter product id to remove from cart -> ")
        if selected_pid in self.cart:
            self.cart.remove(selected_pid)
        else:
            print("Invalid Product ID provided, please select from below")
            self.remove_item_from_cart()

        self.checkout_list = self.cart

    def get_available_coupans(self):
        df = pd.DataFrame(self.coupan_config.values())
        df["start_date"] = pd.to_datetime(df["start_date"], unit='s')
        df["end_date"] = pd.to_datetime(df["end_date"], unit='s')        
        df["last_applied"] = pd.to_datetime(df["last_applied"], unit='s')        
        print("-*"*15,"Available Coupans","*-"*15)
        print(df)
        print("-*"*35)

    def apply_coupan(self, total_amount, coupan):
        self.get_available_coupans()

        coupan_info = self.coupan_config.get(coupan,{})

        if not coupan_info:
            return [False, "Invalid Coupan", total_amount]


        if coupan_info["max_usage"] == 0:
            return [False, "Coupan usage reached it's maximum limit", total_amount]

        if coupan_info["active_flag"] == 0:
            if datetime.now().timestamp() >= coupan_info["last_applied"] + 4*60:
                coupan_info["active_flag"] == 1
            else:
                return [False, "Coupan is inactive, kindly try after some time", total_amount]

        if (coupan_info["start_date"] <= datetime.now().timestamp() <= coupan_info["end_date"]) and (coupan_info["active_flag"] == 1):

            percentage_discount = float(coupan_info["percentage_discount"])

            self.discount_applied = (total_amount * percentage_discount) / 100

            final_amount = (total_amount - self.discount_applied)

            self.coupan_config[coupan]["active_flag"] = 0
            self.coupan_config[coupan]["max_usage"] -= 1
            self.coupan_config[coupan]["last_applied"] = datetime.now().timestamp()

            save_config_into_json(self.coupan_config, "coupan_config_new.json")

        else:
            return [False, "Coupan is not activated yet or has been expired", total_amount]

        return [True, "Coupan applied successfully", final_amount]

    def list_billing_details(self):

        bought_products = [self.product_config[i] for i in self.checkout_list]

        df = pd.DataFrame(bought_products)

        print("-*"*10,"Billing Details", "-*"*10)
        print(df)
        print("Applied discount -> ", self.discount_applied)
        print("-*"*30)

    def checkout(self):

        if not self.checkout_list:
            print("There is no item in your cart\n")
            return

        total_amount = sum([self.product_config.get(i, {}).get("price", 0) for i in self.checkout_list])

        coupan = input("Enter coupan code if you want to apply, else press Enter -> ")

        if coupan.lower() not in [""]:
            coupan_response = self.apply_coupan(total_amount, coupan)
            print(coupan_response[1])   
            total_amount = coupan_response[2]
            self.coupan_applied = True

        if not self.coupan_applied and total_amount >= 10000:
            total_amount -= 500
            self.discount_applied = 500


        self.list_billing_details()

        print("-*"*35)
        print(f"\n\n\t Thank you for shopping with MyCart, your final billing amount is {total_amount}\n")
        self.logout()

    def print_available_choice(self):

        print("*"*70)
        print("*\t\t<< WELCOME TO MY CART >>")
        print("*"*70)
        print("*\t\t Available choices are below")
        print("*\t\t 0 -> list_item")
        print("*\t\t 1 -> list_category")
        print("*\t\t 2 -> get_product_details")
        print("*\t\t 3 -> add_product_to_cart")
        print("*\t\t 4 -> get_available_coupans")
        print("*\t\t 5 -> remove_item_from_cart")
        print("*\t\t 6 -> buy_item_from_cart")
        print("*\t\t 7 -> checkout")
        print("*\t\t 8 -> logout")
        print("*\t\t 9 -> get_all_product_under_category")
        print("*\t\t 10 -> print_available_choice")
        print("*"*70)

    def logout(self):
        print("You have been successfully logged out")
        self.login = False

    def processing(self, activity, **kwargs):
        switcher = {
            0: (self.list_item, ()),
            1: (self.list_category, ()),
            2: (self.get_product_details, (kwargs)),
            3: (self.add_product_to_cart, ()),
            4: (self.get_available_coupans, ()),
            5: (self.remove_item_from_cart, ()),
            6: (self.buy_item_from_cart, ()),
            7: (self.checkout, ()),
            8: (self.logout, ()),
            9: (self.get_all_product_under_category,()),
            10: (self.print_available_choice,())
        }

        func, args = switcher.get(activity, (None, None))
        if func is not None:
            return func(*args)


if __name__ == '__main__':

    user_id = input("User Login ID -> ")
    password = input("User Password -> ")

    obj = UserAccount(user_id, password)

    if not obj.login:
        print(obj.login_status[1])
        sys.exit(1)


    for i in range(3,17):
        print_there(i,70,"*")
    obj.processing(10)

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