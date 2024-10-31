"""
Created on Sun Apr 28 22:16:09 2024
@author: alireza
Ver: 2.00 
Developed in Leris Lab
Presented in IEEE NFV-SDN 2024 Conference
"""


import os
import subprocess
import glob
import shutil 
import readline
import yaml
import subprocess
import glob


def print_header():
    terminal_width = shutil.get_terminal_size().columns
    header_width = terminal_width - 2  # Account for padding on both sides
    print("\n" + "*" * header_width)
    print("*" + " " * (header_width - 2) + "*")
    print("*" + " ****  ****  *****        *       *             *        *****  ".center(header_width - 2) + "*")
    print("*" + " ****  ****  *           * *     * *           ***       *   *  ".center(header_width - 2) + "*")
    print("*" + " ****  ****  *          *  *    *   *         *****      *      ".center(header_width - 2) + "*")
    print("*" + " ****  ****  *****     *    *   *    *       *******     *      ".center(header_width - 2) + "*")
    print("*" + " ****  ****      *    *      * *      *     *       *    *      ".center(header_width - 2) + "*")
    print("*" + " *     ****      *   *       ***       *   *         *   *   *  ".center(header_width - 2) + "*")
    print("*" + " *     ****  *****  *        ***        * *           *  *****  ".center(header_width - 2) + "*")

    print("*" + " " * (header_width - 2) + "*")
    print("*" + "DEMO - Network Traffic Classifier(TN) using DT and RF Models".center(header_width - 2) + "*")
    print("*" + "Traffic Classifier (TC) Module Ver.1.00 2204/11/06".center(header_width - 2) + "*")
    print("*" + "Developed by: LERIS Lab (UFSCar) ".center(header_width - 2) + "*")
    print("*" + "Supported by: Ericsson Telecomunica Ltda, FAPESP, and CPE SMARTNESS ".center(header_width - 2) + "*")
    print("*" + "Presented in IEEE NFV-SDN 2024 Conference ".center(header_width - 2) + "*")
    print("*" + " " * (header_width - 2) + "*")
    print("*" * header_width + "\n")



import subprocess
import multiprocessing

def run_ml_trained_file_receiver():
    print("Running ML trained file receiver...")
    subprocess.Popen(['python3', '/home/cls/my_receivier.py'])
    print("ML trained file receiver started.")

def run_classifier():
    print("Running classifier...")
    subprocess.Popen(['python3', '/home/cls/forwarding_ARCGOther.py'])
    print("Classifier started.")

def main_menu():
    print_header()
    while True:
        print("\nMain Menu:")
        print("1- Run only Online Learning!")
        print("2- Run only the Classifier & Forwarding Module!")
        print("3- Run both options (1) & (2) Cuncurrently!")
        print("4- Exit")

        choice = input("Enter the number of the menu option: ")

        if choice == '1':
            run_ml_trained_file_receiver()
        elif choice == '2':
            run_classifier()
        elif choice == '3':
            print("Running both scripts concurrently...")
            ml_process = multiprocessing.Process(target=run_ml_trained_file_receiver)
            cls_process = multiprocessing.Process(target=run_classifier)
            ml_process.start()
            cls_process.start()
            ml_process.join()
            cls_process.join()
            print("Both scripts finished.")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a valid menu option.")

if __name__ == "__main__":
    main_menu()





