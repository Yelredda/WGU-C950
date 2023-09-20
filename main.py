# Yelredda
# main.py
# C950 Assessment
#
# main python class
# custom imports: ChainingHashTable.py, Truck.py, Packages.py

import csv
import datetime
import os
from Packages import Packages
from Truck import Truck
from ChainingHashTable import ChainingHashTable

############## Address data loading and functions ##############

# Open data/addresses.csv to read in address data
with open("data/addresses.csv") as csv_addr:
    addresses_data = csv.reader(csv_addr)
    addresses_data = list(addresses_data)

# get_address_id - matches an address string to an index based on data read in from data/addresses.csv
## Needed to link address indexes to distance indexes for distance calculations
def get_address_id(address):
    for line in addresses_data:
        if address in line[2]:
            return int(line[0])


############## Distance data loading and functions ##############

# Open data/distances.csv to read in distances between addresses for package deliveries
with open("data/distances.csv") as csv_dist:
    distances_data = csv.reader(csv_dist)
    distances_data = list(distances_data)

# get_distance() - returns distance between two addresses based on data read in from data/distances.csv
## if case required to accomodate inverse direction distance calculation
def get_distance(src, dst):
    src_id = get_address_id(src)
    dst_id = get_address_id(dst)

    distance = distances_data[src_id][dst_id]
    if distance == '':
        distance = distances_data[dst_id][src_id]

    return float(distance)


############## Package loading functions ##############

# Obective E:
#    Develop a hash table, without using any additional libraries or classes, that has an insertion function that takes the following components as input and inserts the components into the hash table:
#
#       package ID number
#       delivery address
#       delivery deadline
#       delivery city
#       delivery zip code
#       package weight
#       delivery status (e.g., delivered, en route)

# load_packages() - open data/packages.csv to read in package information, uses data to create Package objects stored in hash table
## sets status to pending, depart and arrive to "" until the times are updated during delivery
def load_packages(package_hash_data):
    with open("data/packages.csv") as csv_package:
        packages_data = csv.reader(csv_package)
        
        for package in packages_data:
            package_id = int(package[0])
            package_address = package[1]
            package_city = package[2]
            package_state = package[3]
            package_zip = package[4]
            package_deadline = package[5]
            package_weight = package[6]
            package_notes = package[7]
            package_status = "At the hub"
            package_depart = ""
            package_arrive = ""
            
            package = Packages(package_id, package_address, package_city, package_state, package_zip, package_deadline, package_weight, package_notes, package_status, package_depart, package_arrive)

            package_hash_data.insert(package_id, package)

# Objective F:  
#    Develop a look-up function that takes the following components as input and returns the corresponding data elements:
#
#       package ID number
#       delivery address
#       delivery deadline
#       delivery city
#       delivery zip code
#       package weight
#       delivery status (i.e., at the hub, en route, or delivered), including the delivery time

# find_package() - Function to output package details based on package ID parameter 
## needs the time parameter to set status of package at that point during the day
## if no time is provided, assumes 1700 (end of business)
def find_package(pkg_id, cur_time=datetime.timedelta(hours=17)):
    package = package_hash_data.search(pkg_id)
    package.set_status(cur_time)
    print( str(package) ) 

# Create package hash table to store package data
package_hash_data = ChainingHashTable() 
load_packages(package_hash_data)

############## Truck loading functions ##############

# load_trucks() - assigns packages based on special notes and then by proximity to special packages
## initial manual loading of the trucks was too complicated and deadlines were consistently missed 
## developed a solution that loads the trucks based on pre-defined criteria...
## initial attempts to use the packages[] for both priority and misc assignment resulted in packages
## getting skipped; opted to create a misc[] for non-priority packages
def load_trucks():

    truck1_package_list = []
    truck2_package_list = []
    truck3_package_list = []

    packages = []
    misc_packages = [] 

    # Add all packages to a temporary list for assignment
    for pkg_id in range (1,41): # Unable to use len() for hash table; upper limit of 40 is hard coded; could implement item count in hash table
        packages.append( package_hash_data.search(pkg_id) )

    # "Priority" package assignment loop
    # Assignment priority:
    # Give MOST delayed packages to truck 2, which starts when the packages arrive
    # Delayed until 1020 is a special case that gets assigned to truck 3
    # Give all of the other packages with a deadline to truck 1, the early truck
    # Some deadlines have "must ship with..." groupings so I'm treating groups like 1 unit for simplicity
    # Assign "TRUCK2" special notes to truck 2
    for temp_package in packages: 

        if temp_package.notes == 'DELAYED_905': # Delayed packages go to the truck leaving at 905 (truck2) 
            truck2_package_list.append(temp_package)
        elif temp_package.notes == 'DELAYED_1020': # Special case; give to "EOD truck" (truck3)
            truck3_package_list.append(temp_package)
        elif temp_package.notes == 'GROUP': # All "must ship with..." go to truck 1 for simplicity
            truck1_package_list.append(temp_package)
        elif temp_package.deadline != 'EOD': # Packages w/ deadlines go to early truck (truck1)
            truck1_package_list.append(temp_package)
        elif temp_package.notes == 'TRUCK2' : # Packages that have to ship on truck 2
            truck2_package_list.append(temp_package)
        else:
            misc_packages.append(temp_package)

    ## Debugging Check
    #print('Post-priority assignment numbers: ')
    #print('Truck1: ' + str(len(truck1_package_list)))
    #print('Truck2: ' + str(len(truck2_package_list)))
    #print('Truck3: ' + str(len(truck3_package_list)))
    #print( 'Remaining packages: ' + str(len(misc_packages)))

    # Assignment to trucks 1 and 2 if the distance is less than 2.0, otherwise it gets assigned to 3
    for temp_package in misc_packages:
    
        for assigned_package in truck1_package_list:
            if get_distance(assigned_package.address,temp_package.address) < 2.0 and len(truck1_package_list) < 16: # If truck is already delivering there
                truck1_package_list.append(temp_package)
                misc_packages.remove(temp_package)
                break

    for temp_package in misc_packages:
        for assigned_package in truck2_package_list:
            if get_distance(assigned_package.address,temp_package.address) < 2.0 and len(truck2_package_list) < 16: # If truck is already delivering there
                truck2_package_list.append(temp_package)
                misc_packages.remove(temp_package)
                break

    for temp_package in misc_packages:
        truck3_package_list.append(temp_package)
    
    ## Debugging Check
    #print('Post-miscellaneous assignment numbers: ')
    #print('Truck1: ' + str(len(truck1_package_list)))
    #print('Truck2: ' + str(len(truck2_package_list)))
    #print('Truck3: ' + str(len(truck3_package_list)))

    return truck1_package_list,truck2_package_list,truck3_package_list


# simulate_deliveries() - "delivers" the package by calculating departure and arrival times for each package
## Orders the packages in the truck using nearest neighbor, then uses the data
## to calculate the departure and arrival times of the packages, simulating a delivery
def simulate_deliveries(truck):
    # Empty queue to hold packages for sorting
    temp = [] 

    for package in truck.packages:
        temp.append(package)

    truck.packages.clear()

    # Sort temp list, adding closest one. Note: this is slow and iterates through the entire list.
    # I don't like this method, but it's the only way that I can think of to find the closest. 
    # O(n**2) so not optimal
    while len(temp) > 0:
        closest_address = 999
        closest_package = None

        for package in temp:
            package_distance = get_distance(truck.cur_address, package.address)

            if package_distance <= closest_address:
                closest_address = package_distance
                closest_package = package

        # closest_package should be the closest delivery to the truck at this point
        # add back to truck, remove from temp, repeat cycle
        truck.packages.append(closest_package.pkg_id)
        temp.remove(closest_package)

        # "delivering" the package
        # truck is "en route," update the package time to show that the truck is heading there
        closest_package.depart = truck.last_depart
        
        # truck is "on site," add the miles to the truck and show that the truck is on site
        truck.cur_address = closest_package.address 
        truck.total_miles += closest_address

        # set package arrival to truck's arrival time; package is now delivered and truck is departing
        truck.last_depart += datetime.timedelta(hours=closest_address/18)
        closest_package.arrive = truck.last_depart


############## User interaction functions ##############

# print_banner() - prints initial program banner, prompts the user for 1 of 4 options
def print_banner():
    print()
    print('Yelredda')
    print('C950 Assessment - WGUPS')
    print('****************************************')
    print('1. Print ALL package statuses and total mileage per truck (End of Shift)')
    print('2. Print ONE Package Status at a specified time')
    print('3. Print ALL package statuses at a specified time')
    print('4. Exit the program')
    print('****************************************')

# print_package_header() - print header for packages; makes the main program code cleaner
def print_package_header():
    print('Pkg_Id, Address, City, State, ZipCode, Deadline, Weight, Notes, Status, Departure Time, Arrival Time')
    print('****************************************************************************************************')

# Objective G:  
#    Provide an interface for the user to view the status and info (as listed in part F) of any package at any time, and the total mileage traveled by all trucks. 
#    (The delivery status should report the package as at the hub, en route, or delivered. Delivery status must include the time.)

##################### Beginning of main program logic #####################
class Main:
 
    # Create truck instances; previous runs show that truck 1 finishes by 930, so assigning truck 3 to start 1 hour later
    # Could potentially modify Truck class to track their last package delivery time to assign that as the start time for truck3
    truck1 = Truck(1, [], 0, '4001 South 700 East', datetime.timedelta(hours=8) )
    truck2 = Truck(2, [], 0, '4001 South 700 East', datetime.timedelta(hours=9, minutes=5) )
    truck3 = Truck(3, [], 0, '4001 South 700 East', datetime.timedelta(hours=10, minutes=30) )
    
    # Load trucks
    truck1.packages,truck2.packages,truck3.packages = load_trucks()
    
    # Simulate truck deliveries
    simulate_deliveries(truck1)
    simulate_deliveries(truck2)
    simulate_deliveries(truck3)

    ## Debugging check
    #print('Truck1: ' + str(truck1))
    #print('Truck2: ' + str(truck2))
    #print('Truck3: ' + str(truck3))

    # Beginning of user interaction; prompt loops until the user chooses valid input (including exit)
    while(True):
        print_banner()

        choice = input('Please select your desired option: ')

        if choice == '1': # Print all packages, assuming "end of shift" time of 1700, allowing for 0800-1700 window for deliveries
            print()
            print('Displaying ALL package statuses by the end of the business day (1700): ')
            print('Truck1: ' + str(truck1.total_miles) + ' miles total. ')            
            print_package_header()

            for pkg_id in truck1.packages:
                find_package(pkg_id, datetime.timedelta(hours=17))

            print()
            print('Truck2: ' + str(truck2.total_miles) + ' miles total. ')
            print_package_header()

            for pkg_id in truck2.packages:
                find_package(pkg_id, datetime.timedelta(hours=17))

            print()
            print('Truck3: ' + str(truck3.total_miles) + ' miles total. ')
            print_package_header()

            for pkg_id in truck3.packages:
                find_package(pkg_id, datetime.timedelta(hours=17))

        elif choice == '2': # Print one package's status at a specified time
            print()
            pkg_id = int(input('Please select your desired package: '))
            package = package_hash_data.search(choice)

            choice = input('Please specify your time (HH:MM:SS) : ')
            (h, m, s) = choice.split(':')

            print()
            print(f'Displaying package {pkg_id} at the time ({h}:{m}:{s})' )
            print_package_header()
            find_package(pkg_id, datetime.timedelta(hours=int(h),minutes=int(m),seconds=int(s)))

        elif choice == '3': # Print ALL packages' status at a specified time
            print()
            choice = input('Please specify your time (HH:MM:SS) : ')
            (h, m, s) = choice.split(':')
            print()
            print(f'Displaying all packages at the time ({h}:{m}:{s})' )
            print()
            print('Truck1: ' + str(truck1.total_miles) + ' miles total. ')            
            print_package_header()

            for pkg_id in truck1.packages:
                find_package(pkg_id, datetime.timedelta(hours=int(h),minutes=int(m),seconds=int(s)))

            print()
            print('Truck2: ' + str(truck2.total_miles) + ' miles total. ')
            print_package_header()

            for pkg_id in truck2.packages:
                find_package(pkg_id, datetime.timedelta(hours=int(h),minutes=int(m),seconds=int(s)))

            print()
            print('Truck3: ' + str(truck3.total_miles) + ' miles total. ')
            print_package_header()

            for pkg_id in truck3.packages:
                find_package(pkg_id, datetime.timedelta(hours=int(h),minutes=int(m),seconds=int(s)))

        elif choice == '4': # Exit request
            exit()




