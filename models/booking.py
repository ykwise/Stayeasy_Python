from datetime import datetime,date

class Booking:
    bookings = {}

    bookingid = 0
    
    def __init__(self,name,phone,email,guests,roomtype,allocated_room,checkin,checkout):
        Booking.bookingid += 1
        self.bookingid = Booking.bookingid
        self.name = name
        self.phone = phone
        self.email = email
        self.guests = guests
        self.roomtype = roomtype
        self.allocated_room = None
        self.checkin = checkin
        self.checkout = checkout
        self.status = "CONFIRMED"

    def __str__(self):
        return f"Booking Id: {self.bookingid} | Guest Name: {self.name} | Phone: {self.phone} | No.of Guests: {self.guests} | RoomType: {self.roomtype} | Check In : {self.checkin} | Check Out : {self.checkout} | Status: {self.status}"
