#------------------------------
import sqlite3
from datetime import datetime,date,timedelta
from abc import ABC,abstractmethod
from Exceptions import exceptions as ex
import csv
from models.guest import Guest as gt
from models.booking import Booking as bk
from models.room import RoomType,StandardRoom,DeluxeRoom,SuiteRoom

#Exceptions
class RoomException(Exception):
    pass

class DateException(Exception):
    pass

class InvalidStatusException(Exception):
    pass

class BookingException(Exception):
    pass


#creating tables
def create_tables():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    #Rooms Table
    cursor.execute('''
                Create Table If Not Exists Rooms(
                Room_id int Primary Key Not Null,
                Room_Type Text Not Null Check(Room_Type in ('STANDARD','DELUXE','SUITE')),
                Floor int Not null                
                )
            ''')

    print("Rooms Table Created Succesfully")

    #Guests Table
    cursor.execute('''
                Create Table If not Exists Guests(
                Guest_Name Text Not Null,
                Phone_Number Text Primary Key check(
                    length(Phone_Number) = 10 and 
                    (Phone_Number like '6%' or
                     Phone_Number like '7%' or
                     Phone_Number like '8%' or
                     Phone_Number like '9%' )
                ),

                Email Text check(Email like '%@gmail.com') Not Null
                
                )

                ''')
    print("Guests Table Created Successfully")

    #Bookings Table
    cursor.execute('''
                Create Table If Not Exists Bookings(
                Booking_Id int Primary Key Not Null,
                Guest_Name Text Not Null,
                Phone_Number Text check(
                                    length(Phone_Number) = 10 and 
                                    (Phone_Number like '6%' or
                                     Phone_Number like '7%' or
                                     Phone_Number like '8%' or
                                     Phone_Number like '9%' )
                                    ),
                Email Text check(Email like '%@gmail.com') Not Null,
                No_of_Guests int check(No_of_Guests > 0),
                Check_In Text Not Null,
                Check_Out Text Not Null,
                Room_id int Not Null,
                Status Text Check(Status in ('CONFIRMED','CHECKED_IN','CHECKED_OUT','CANCELLED')),
                Foreign Key(Room_id) references Rooms(Room_id),
                Foreign Key(Phone_Number) references Guests(Phone_Number)
                )

                    ''')
    print("Bookings Table Created Successfully")

#Showing Table data
def show_table(tablename):
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    que = f"select * from {tablename}"
    cursor.execute(que)
    data = cursor.fetchall()
    print(f"Table: {tablename}")
    for row in data:
        print(row)
    print()


#load rooms data
def load_rooms():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()
    logs = []
    rooms = set()
    rooms_type_obs = {}


    with open("rooms.csv","r") as file:
        content = csv.reader(file)

        next(content)        

        for row in content:
            room_id = row[0]
            room_type = row[1].strip().upper()
            floor = row[2]

            #print(f"Room No: {room_id} | Room Type :{room_type} | Floor : {floor}")

            try:
                room_id = int(row[0])
                
                if room_id in rooms:
                    raise RoomException(f"Room Id {room_id} already exists in Rooms Table")
                
                room_type = row[1].strip().upper()
                if room_type == "":
                    raise RoomException("Name Cannot be Empty")

                if room_type not in ["STANDARD","DELUXE","SUITE"]:
                    raise RoomException(f"Invalid Room Type {room_type}")

                #--------------------------                 
                floor = int(row[2])
                if floor == "":
                    raise RoomException("Floor is Empty")

                #---------------------
                

                rooms.add(room_id)

                #After Validating , Pushing the Values to Rooms Table
                query = "Insert into Rooms(Room_id,Room_Type,Floor) Values(?,?,?)"
                cursor.execute(query,(room_id,room_type,floor))
                #conn.commit()
                print(f"Data Inserted With Room No : {room_id}")
                print()

                #creating objects of specific RoomType and Keeping in dict
                if room_type == "STANDARD":
                    rooms_type_obs[room_id] = StandardRoom()
                elif room_type == "DELUXE":
                    rooms_type_obs[room_id] = DeluxeRoom()
                else:
                    rooms_type_obs[room_id] = SuiteRoom()



            except RoomException as e:
                logs.append(f"Rooms.csv | {room_id} | {e}")

            except ValueError as e:
                logs.append(f"Rooms.csv | {room_id} |{e}")

            except sqlite3.IntegrityError:
                print(f"Room Id : {room_id} Already Exists in Rooms Table")
    conn.commit()
    conn.close()
    #--------------------
    #creating errorlog file
    with open("app.log","w") as errorfile:
        for errors in logs:
            errorfile.writelines(errors + "\n")

    print("Error Logs sent to app.log ")
    

    print()
    show_table("Rooms")
    print()
    for errors in logs:
        print(errors)
    print()

    print("Room Type Objects")
    #print(rooms_type_dict)

    for id in rooms_type_obs:
        tarrif = rooms_type_obs[id].get_tarrif()
        roomtype = rooms_type_obs[id].roomtype
        print(f"Room No: {id} | Room Type: {roomtype} | Tarrif: {tarrif}")

def val_dates(datetype,day,months,year):
    while True:
        try:
                    #Taking Checking input
                    checkinday = int(input("Enter checkin-day(DD) (1-31): "))
                    if checkinday <=0 or checkinday > 31:
                        raise DateException("Day number should be be betwwen  1 and 31")
                    
            
                    checkinmonth = int(input("Enter checkin-Month(MM) (1 - 12): "))
                    if checkinmonth <=0 or checkinmonth>12:
                        raise DateException("Month number should be be betwwen  1 and 12")
            
                    checkinyear = int(input("Enter checkin-Year(YYY): "))
                    if len(str(checkinyear)) !=4:
                        raise DateException("Please Provide Valid Year")
            
                    checkin = date(checkinyear,checkinmonth,checkinday)
                    checkin_fmt = checkin.strftime("%d-%m-%Y")
                    
                    if(checkin < today):
                        raise DateException("Check in day is less than today")
                    if checkin > today + timedelta(days=180):
                        raise DateException("Check In Date Cannot be more than 180 days from today")
                    print(f"Check-In Date {checkin_fmt}")
        
                    #Taking checkout
                    checkoutday = int(input("Enter checkout-day(DD) (1-31): "))
                    if checkoutday <=0 or checkoutday > 31:
                        raise DateException("Day number should be be betwwen  1 and 31")
                    
                    checkoutmonth = int(input("Enter checkout-Month(MM) (1 - 12): "))
                    if checkoutmonth <=0 or checkoutmonth>12:
                        raise DateException("Month number should be be betwwen  1 and 12")
                    
                    checkoutyear = int(input("Enter checkout-Year(YYY): "))
                    if len(str(checkoutyear)) !=4:
                        raise DateException("Please Provide Valid Year")
                    
                    checkout = date(checkoutyear,checkoutmonth,checkoutday)
        
                    checkout_fmt = checkout.strftime("%d-%m-%Y")
                    if(checkout <= checkin):
                        raise DateException("Check out should be greater than Check in")
        
                    nights = (checkout - checkin).days
                    if(nights> 30):
                        raise BookingException("Stay Cannot be more than 30 nights")
                    
                    print(f"Check-Out Date {checkout_fmt}")
        
                    break
            
            
            
        except DateException as e:
            print(e)
        except BookingException as e:
            print(e)
            
        except ValueError:
            print("Please Enter Valid input")




#Checking Available Rooms
def check_available_rooms(type,guests,checkin,checkout):
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()
    avialable_rooms = []

    # while True:
    #     print("----Checking Availability------")
    #     try:
    #         roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()

    #         if(roomtype==""):
    #             print("Room Type Cannot Be Empty")
    #             continue
    #         if roomtype not in ["STANDARD","DELUXE","SUITE"]:
    #             raise RoomException("Please Enter Valid RoomType")

        

    #         guests = int(input("Enter No.of Guests: "))

    #         if guests < 1:
    #             raise RoomException("Guests Should be More than or equal to 1")

    #         checkin = input("Enter Check-In Date: ").strip()
    #         req_checkin_fmt = datetime.strptime(checkin,"%d-%m-%Y")

    #         checkout = input("Enter Check-Out Date: ").strip()
    #         req_checkout_fmt = datetime.strptime(checkout,"%d-%m-%Y")

    #         break

    #     except RoomException as e:
    #         print(e)
    #     except ValueError:
    #         print("Please Enter Valid Input")

    req_checkin_fmt = datetime.strptime(checkin,"%d-%m-%Y")
    req_checkout_fmt = datetime.strptime(checkout,"%d-%m-%Y")

    query = "Select * from Rooms Where Room_Type = ?"
    cursor.execute(query,(type,))
    roomsdata = cursor.fetchall()
    for row in roomsdata:
        is_available = True
        rid = row[0]

        query = "Select Check_In,Check_Out from Bookings where Room_id = ?"
        cursor.execute(query,(rid,))
        data = cursor.fetchall()
        for row in data:
            exist_checkin = datetime.strptime(row[0],"%d-%m-%Y")
            exist_checkout = datetime.strptime(row[1],"%d-%m-%Y")

            if req_checkin_fmt < exist_checkout and req_checkout_fmt > exist_checkin:
                is_available = False
                break

        if is_available:
            avialable_rooms.append(rid)

    print(f"Available Rooms:{avialable_rooms} ")

    return avialable_rooms



            





    # query = "Select Room_id,Room_Type from rooms where Room_Type = ? "
    # cursor.execute(query,(type,))
    # data = cursor.fetchall()
    # print("-----Available Rooms-----")
    # for row in data:
    #     room_id = row[0]
    #     room_type = row[1]
    #     print(f"Room Id : {room_id} | Room Type:{room_type}")




#creating booking
def make_booking():
    conn = sqlite3.connect("stayeasy.db")
    cursor = conn.cursor()

    cursor.execute("Select max(Booking_Id) from bookings")
    data = cursor.fetchone()
    # print(data)
    if data[0] is None:
        bkid = 1
    else:
        bkid = data[0]+1

    
        

    print("-----Booking Details----")
    name = input("Enter Guest Name: ").strip().upper()

    while name == "":
        print("Name Cannot be Empty")
        name = input("Enter Guest Name: ").strip().upper()

    
    phone = input("Enter Phone Number: ").strip()
    while (len(phone) != 10) or not phone.isdigit():
        print("Phone Number does not have 10 digits")
        phone = input("Enter Phone Number: ").strip()
    while not( phone.startswith("6") or  phone.startswith("7")  or phone.startswith("8") or  phone.startswith("9") ):
        print("Phone Number does not start with 6 or 7 or 8 or 9")
        phone = input("Enter Phone Number: ").strip()
    
    email = input("Enter Email: ").strip().lower()
    while(not email.endswith("@gmail.com")):
        print("Please Enter Valid Email")
        email = input("Enter Email: ").strip().lower()
    
    guests = int(input("Enter No.of Guests: "))
    while guests < 1:
        print("guests should be more than 0")
        guests = int(input("Enter No.of Guests: "))
    
    roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()
    while roomtype not in ["STANDARD","DELUXE","SUITE"]:
        print("Please Enter Valid Room Type")
        roomtype = input("Enter Room Type(Standard/Deluxe/Suite): ").strip().upper()
    
        
    
    today = date.today()
    today_fmt = today.strftime("%d-%m-%Y")
    print(f"Today Date: {today_fmt}")
    
    #Validating Checkin and Checkout   
    while True:
        try:
            #Taking Checking input
            checkinday = int(input("Enter checkin-day(DD) (1-31): "))
            if checkinday <=0 or checkinday > 31:
                raise DateException("Day number should be be betwwen  1 and 31")
            
    
            checkinmonth = int(input("Enter checkin-Month(MM) (1 - 12): "))
            if checkinmonth <=0 or checkinmonth>12:
                raise DateException("Month number should be be betwwen  1 and 12")
    
            checkinyear = int(input("Enter checkin-Year(YYY): "))
            if len(str(checkinyear)) !=4:
                raise DateException("Please Provide Valid Year")
    
            checkin = date(checkinyear,checkinmonth,checkinday)
            checkin_fmt = checkin.strftime("%d-%m-%Y")
            
            if(checkin < today):
                raise DateException("Check in day is less than today")
            if checkin > today + timedelta(days=180):
                raise DateException("Check In Date Cannot be more than 180 days from today")
            print(f"Check-In Date {checkin_fmt}")

            #Taking checkout
            checkoutday = int(input("Enter checkout-day(DD) (1-31): "))
            if checkoutday <=0 or checkoutday > 31:
                raise DateException("Day number should be be betwwen  1 and 31")
            
            checkoutmonth = int(input("Enter checkout-Month(MM) (1 - 12): "))
            if checkoutmonth <=0 or checkoutmonth>12:
                raise DateException("Month number should be be betwwen  1 and 12")
            
            checkoutyear = int(input("Enter checkout-Year(YYY): "))
            if len(str(checkoutyear)) !=4:
                raise DateException("Please Provide Valid Year")
            
            checkout = date(checkoutyear,checkoutmonth,checkoutday)

            checkout_fmt = checkout.strftime("%d-%m-%Y")
            if(checkout <= checkin):
                raise DateException("Check out should be greater than Check in")

            nights = (checkout - checkin).days
            if(nights> 30):
                raise BookingException("Stay Cannot be more than 30 nights")
            
            print(f"Check-Out Date {checkout_fmt}")

            break
    
    
    
        except DateException as e:
            print(e)
        except BookingException as e:
            print(e)
    
        except ValueError:
            print("Please Enter Valid input")

    available_rooms = check_available_rooms(roomtype,guests,checkin_fmt,checkout_fmt)
    allocated_room = available_rooms[0]

    



    booking_object = bk(name,phone,email,guests,roomtype,allocated_room,checkin_fmt,checkout_fmt)
    bkid = booking_object.bookingid
    bk_status = booking_object.status
    # bk.bookings[booking_object.bookingid] = {
    #     "Name" : name,
    #     "Phone" : phone,
    #     "Email" : email,
    #     "Guests" : guests,
    #     "RoomType" : roomtype,
    #     "Check-In" : checkin_fmt,
    #     "Check-Out" : checkout_fmt,
    #     "Status" : booking_object.status
    # }

    #inserting data into bookings table
    query = "insert into bookings(Booking_Id,Guest_Name,Phone_Number,Email,No_of_Guests,Check_In,Check_Out,Room_id,Status) Values(?,?,?,?,?,?,?,?,?)"

    cursor.execute(query,(bkid,name,phone,email,guests,checkin_fmt,checkout_fmt,allocated_room,bk_status))
    conn.commit()
    show_table("Bookings")

    #storing in dictionary
    bk.bookings[bkid] = booking_object
    print()
    for bookings in bk.bookings.values():
        print(bookings)
    
#Entry Point 
def start_program():

    # conn = sqlite3.connect("stayeasy.db")
    # cursor = conn.cursor()

    # cursor.execute("Drop Table Bookings ")
    # print("Table Data Deleted Succesfully\n")

    # # #cursor.execute('''Insert into Bookings Values(1,"Yash",9121959158,"yk@gmail.com",2,'12-11-2026','15-11-2026',101,'CONFIRMED')''')
    # # # print("Data Inserted")
    # conn.commit()
    # conn.close()


    
    #-------------------------------
    print()
    create_tables()
    print()
    print("---------------------")
    #show_table("Rooms")
    
    #make_booking()
    #print(bk.bookings)
    #check_available_rooms()
    #show_table("Rooms")


    #load_rooms()
    show_table("Bookings")

start_program()



