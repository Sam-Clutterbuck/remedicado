import hashlib
from secrets import token_hex

from src.sql_helpers import Helpers


class Acccount_Controller():

    def Create_Account(Username, Password):

        if (Username == "") or Username is None or (Password == "") or Password is None:
            print("Please enter a username and password")
            return False
        
        exists = Acccount_Controller.Find_User(Username)
        if exists is not None:
            print("Username already taken")
            return False
        
        random_salt = token_hex(64)
        hashed_password = hashlib.sha256((Password+random_salt).encode()).hexdigest()

        exit

        try:

            Helpers.sql_cursor.execute('''
                INSERT INTO accounts (
                    username, 
                    salt, 
                    password
                    ) VALUES (
                        %(username)s, 
                        %(salt)s, 
                        %(password)s
                        );
                ''', {"username" : Username,
                      "salt" : random_salt,
                      "password" : hashed_password})
            
            Helpers.db.commit()   

            return True

        except Exception as error: 
            print(error)
            return False
        

    def Find_User(Username):
        try:

            Helpers.sql_cursor.execute('''
                SELECT *
                FROM accounts
                WHERE username = %(username)s
                ''', {"username" : Username})
            
            user_details = Helpers.Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchone())

            return user_details


        except Exception as error: 
            print(error)
            return None
        
    
    def Login(Username, Password):
        
        if (Username == "") or Username is None or (Password == "") or Password is None:
            print("Please enter a username and password")
            return False
        
        User_Info = Acccount_Controller.Find_User(Username)
        if User_Info is None or (User_Info == {}):
            print("Username or Password is incorrect")
            return False
        
        hashed_password = hashlib.sha256((Password+User_Info['salt']).encode()).hexdigest()

        if (hashed_password != User_Info['password']):
            print("Username or Password is incorrect")
            return False

        print(f"Signed in as : {Username}")
        return True
    
    def Password_Reset(Username, Password):
        if (Username == "") or Username is None or (Password == "") or Password is None:
            print("Please enter a username and password")
            return False
        
        User_Info = Acccount_Controller.Find_User(Username)
        if User_Info is None or (User_Info == {}):
            print("User doesn't exist")
            return False
        
        random_salt = token_hex(64)
        hashed_password = hashlib.sha256((Password+random_salt).encode()).hexdigest()

        try:
            Helpers.sql_cursor.execute('''
                UPDATE accounts 
                SET salt=%(salt)s,
                    password=%(password)s
                WHERE account_id=%(account_id)s
                AND username=%(username)s;
                ''', {"username" : Username,
                      "salt" : random_salt,
                      "password" : hashed_password,
                      "account_id" : User_Info['account_id']})
            Helpers.db.commit()
            return True
        except Exception as error: 
            print(error)
            return False
        

    def Delete_user(Username):

        if (Username == "") or Username is None:
            print("Please enter a username")
            return False
        
        User_Info = Acccount_Controller.Find_User(Username)
        if User_Info is None or (User_Info == {}):
            print("User doesn't exist")
            return False

        try:

            Helpers.sql_cursor.execute('''
            DELETE FROM accounts 
            WHERE account_id=%(account_id)s
            AND username=%(username)s;
            ''', {"username" : Username,
                    "account_id" : User_Info['account_id']})
            Helpers.db.commit()
            return True

        except Exception as error: 
            print(error)
            return False
        
    def List_Users():

        Helpers.sql_cursor.execute('''
                SELECT username
                FROM accounts
                ''')
            
        username_list = Helpers.Multi_Sql_To_Dict(Helpers.sql_cursor.description, Helpers.sql_cursor.fetchall())

        return username_list