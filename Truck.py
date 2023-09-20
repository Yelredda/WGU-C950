# Theo Adderley - 011160022
# Truck.py
# C950 Assessment
#
# Truck class to hold information related to individual classes

# Creating a truck class to track the trucks
# Will store the packages as well 
# Speed is universally 18 MPH, could be added as an argument for further customizability
class Truck:
    def __init__(self, truck_number, packages, total_miles, cur_address, last_depart):
        self.truck_number = truck_number
        self.packages = packages
        self.total_miles = total_miles
        self.cur_address = cur_address
        self.last_depart = last_depart

    def __str__(self):
        return '%s, %s, %s, %s, %s' % (self.truck_number, self.packages, self.total_miles, self.cur_address, self.last_depart) 