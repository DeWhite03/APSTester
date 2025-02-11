#!/usr/bin/env python3
import subprocess
import os
import sys
import time
import inputGeneration
import shutil
import platform
import argparse

workingOutputFolderName = "workingOutputs"
userOutputFolderName = "userOutput"

workingProgramsFolderName = "workingPrograms"

allOutputsFolderName = "allOutputs"

timeoutLimit = 2 # in seconds
testLimit = 0 # 0 means no limit

operatingSystem = platform.system()

selected_assignment = "5vreca"

slash = "/"

def runCPPProgram(programName, inputTxt):
    # Command to run the C++ program and get its output 
    # runArguments = [programName]
    # runCommand = "".join(str(x) for x in runArguments)
    # Run the C++ program 
    try:
        runProcess = subprocess.run([programName],input=inputTxt, capture_output=True, timeout=timeoutLimit, text=True, shell=True)
        if "timeout" in runProcess.stdout:
            print("Program " + programName + " timed out. This happened in a weird place in code so please report this to @GonnaDoStuff.")
            return "timeout"
        return runProcess.stdout
    # if the program times out catch the exception and just print timeout
    except subprocess.CalledProcessError as e:
        exit_code = e.returncode
        stderror = e.stderr
        print(exit_code, stderror)
        exit(1)
    except Exception as e:
        print(e)
        print("Program " + programName + " timed out.")
        return "timeout"

def giveExecutePermission(path):
    # Give execute permission to the program
    os.system("chmod -R +x " + path)
    

outputCounter = 0

def testProgram(userProgramName):
    global outputCounter
    global testLimit
    
    # Generate input file # Currently hardcoded for DN2
    ############################################################# CHANGE THIS ###################################################################
    inputTxt = ""
    if selected_assignment == "2Kzlitje":
        inputTxt = inputGeneration.Kzlitje()
    elif selected_assignment == "3neboticniki":
        inputTxt = inputGeneration.neboticniki()
    elif selected_assignment == "4mediane":
        inputTxt = inputGeneration.mediane()
    elif selected_assignment == "5vreca":
        inputTxt = inputGeneration.vreca()

    #### Generate output file by running the working programs with the generated input file
    workingProgramNames = os.listdir("." + slash + workingProgramsFolderName)
    
    if workingProgramNames == []:
        print("No working programs found in the workingPrograms folder. Please add some working programs and try again.")
        exit(1)
    
    # Get outputs of all the working programs
    atleastOneWorkingProgram = False
    prevOutput = ""
    for currWorkingProgram in workingProgramNames:
        path = workingProgramsFolderName + slash + currWorkingProgram
        output = runCPPProgram(path, inputTxt)
        with open(workingOutputFolderName + slash + currWorkingProgram + '.out', 'w') as f:
            f.write(output)
        
        # Simplest way to check if everything is working
        if output == "":
            print("Working program %s failed to generate output." % currWorkingProgram)
            continue
        atleastOneWorkingProgram = True
        
        if prevOutput != "" and prevOutput != output:
            print("Working programs disagree.")
        prevOutput = output
    
    if not atleastOneWorkingProgram:
        print("Working programs failed to generate output. This could be due to an error in the program or due to no working programs for this operating system in the workingPrograms folder.")
        exit(1)
    
    # Get the output of the program to be tested
    t1 = time.time()
    userOutput = runCPPProgram("." + slash + userProgramName, inputTxt)
    with open(userOutputFolderName+slash + "" + userProgramName + '.out', 'w') as f:
        f.write(userOutput)
    t2 = time.time()
    
    # Compare the outputs of the working programs with the output of the program to be tested
    workingOutputs = os.listdir("." + slash + "workingOutputs")
    outputsMatch = True
    for currWorkingOutput in workingOutputs:
        # Compare the outputs
        with open(workingOutputFolderName + slash + currWorkingOutput, 'r') as f:
            workingOutput = f.read()
            if workingOutput!=userOutput :
                outputsMatch = False
                break
    
    # Ignore everything past this point, i gave up
    passedOrNotFolderName = slash + "passed" + slash
    if outputsMatch:
        print(str(outputCounter) + ": " + "[\033[32m+\033[0m] Test passed", end="")
    else:
        print(str(outputCounter) + ": " + "[\033[31m-\033[0m] Test failed", end="")
        passedOrNotFolderName = slash + "failed" + slash

    print(" - Time taken: %.3f seconds." % (t2-t1))

    
    os.makedirs(allOutputsFolderName + passedOrNotFolderName+ str(outputCounter) + slash + "working")
    if not outputsMatch:
        os.makedirs(allOutputsFolderName + passedOrNotFolderName+ str(outputCounter) + slash + "user")
    for currWorkingOutput in workingOutputs:
        # Compare the outputs
        with open(allOutputsFolderName + passedOrNotFolderName + str(outputCounter) + slash + "working" + slash + currWorkingOutput, 'w') as fileToPrintTo:
            with open(workingOutputFolderName + slash + currWorkingOutput, 'r') as originalFile:
                textToWrite = originalFile.read()
                fileToPrintTo.write(textToWrite)
    
    if not outputsMatch:
        with open(allOutputsFolderName + passedOrNotFolderName + str(outputCounter) + slash + "user" + slash + userProgramName + ".out", 'w') as fileToPrintTo:
            fileToPrintTo.write(userOutput)
        
    with open(allOutputsFolderName + passedOrNotFolderName + str(outputCounter) + slash + "test.in", 'w') as fileToPrintTo:
        fileToPrintTo.write(inputTxt)
    
    outputCounter += 1
    if testLimit != 0 and outputCounter >= testLimit:
        print("Test limit reached. Exiting.")
        exit(0)

def setup():
    global workingProgramsFolderName
    global slash
    global timeoutLimit
    global selected_assignment
    global testLimit
    global pullChoice

    # Parameters for the program
    parser = argparse.ArgumentParser()
    parser.add_argument("-la", "--listassignments", help="List all the assignments that can be tested.", action="store_true")
    parser.add_argument("program", help="The name of the program to be tested including .cpp (Example: program.cpp).")
    parser.add_argument("-t", "--timeout", help="The timeout limit for the program in seconds. Default is %d seconds." % timeoutLimit, type=int)
    parser.add_argument("-a", "--assignment", help="The name of the assignment. Choose the name of the assignment you are working on. Default is: %s" % selected_assignment, type=str)
    parser.add_argument("-lm", "--limit", help="The limit of tests to run. Default is no limit.", type=int)
    parser.add_argument("-c", "--clear", help="Clear all temporary folders and previous outputs.", action="store_true")
    parser.add_argument("-stc", "--settestcounter", help="Set the test counter to a specific value. Default is 0. This mostly has no effect. Currently only helps with \"5vreca\".", type=int)
    parser.add_argument("-p", "--pull", help="Automatically update tester.", action="store_true")
    parser.add_argument("-max", "--max", help="Set the maximum numbers of inputs the program will be able to generate. Use at your own risk.", type=int)
    
    args = parser.parse_args()
    
    print("\n\033[34mRemember to use\033[0m \033[32m-h\033[0m \033[34mto see all the capabilities of this program!\033[0m\n")

    # Checks if repo is up to date--------------------------------------
    fetch = subprocess.run("git fetch", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    pullChoice = False
    if fetch.returncode != 0:
        print('\033[93m' + 'Cannot check if repository is up to date' + '\033[0m')
    else:
        if not args.pull:
            localHash = subprocess.run('git log -n 1 --pretty=format:"%H" master', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            originHash = subprocess.run('git log -n 1 --pretty=format:"%H" origin/master', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            if localHash.stdout != originHash.stdout:
                print('\033[93m' + 'Your repo is not up to date. Follow instructions or run the script with the -p flag' + '\033[0m')
                yes = {'yes','y', 'ye'}
                no = {'no','n', ''}
                while True:
                    pullChoice = input('Would you like to update [y/N]:').lower()
                    if pullChoice in yes:
                        pullChoice = True
                        break;
                    elif pullChoice in no:
                        pullChoice = False;
                        break;
                    else:
                        print("Please respond with 'yes' or 'no'")
            else:
                print('\033[93m' + 'You\'re up to date!' + '\033[0m')
        
        if args.pull or pullChoice:
            print('Pulling from repo...')
            pull = subprocess.run('git pull origin master', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True);
            if pull.returncode != 0:
                print('\033[93m' + 'Cannot pull from repo' + '\033[0m')
            else:
                print('\033[93m' + 'Successfully pulled from repo! Please start the program again.' + '\033[0m')
                exit(0)
    # END OF CHECK FOR UPDATE---------------------------------------------
    
    if args.timeout:
        timeoutLimit = args.timeout
    
    if args.limit:
        testLimit = args.limit
    
    if operatingSystem == "Windows":
        slash = "\\"
    
    if args.max:
        inputGeneration.setMaxInputs(args.max)
        
    if args.settestcounter:
        inputGeneration.setTestCounter(args.settestcounter)
        global outputCounter
        outputCounter = args.settestcounter
    
    if operatingSystem == "Darwin":
        print("\033[31mWARNING\033[0m")
        print("It seems you are using \033[36mMacOS\033[0m. This program is not tested on MacOS. If you encounter any issues please report them.")
        print("The working programs have been compiled on \033[32mM1\033[0m macs. The program might not work on \033[36mIntel\033[0m macs.")
        print("\033[31mWARNING END\033[0m\n")
    
    if args.clear:
        # Clear previous outputs
        print("Deleting old outputs...")
        if os.path.exists(workingOutputFolderName):
            shutil.rmtree(workingOutputFolderName)
        os.makedirs(workingOutputFolderName)
        if os.path.exists(userOutputFolderName):
            shutil.rmtree(userOutputFolderName)
        os.makedirs(userOutputFolderName)
        if os.path.exists(allOutputsFolderName):
            shutil.rmtree(allOutputsFolderName)
        os.makedirs(allOutputsFolderName)
        os.makedirs(allOutputsFolderName + slash + "passed")
        os.makedirs(allOutputsFolderName + slash + "failed")
        print("Cleared all temporary folders and previous outputs.")
        exit(0)
    
    # Get the correct folder name for the working programs
    if operatingSystem == "Linux":
        workingProgramsFolderName += slash + "linux"
    elif operatingSystem == "Windows":
        workingProgramsFolderName += slash + "windows"
    elif operatingSystem == "Darwin":
        workingProgramsFolderName += slash + "macos"
    else:
        print("Unsupported operating system. Run this program on linux, windows, or macos.\n")
        exit(1)
    
    # Get all the currently added assignments
    assignments = os.listdir("." + slash + workingProgramsFolderName)
    if args.listassignments:
        print ("List of assignments for your operating system:")
        for assignment in assignments:
            print(assignment)
        exit(0)
    
    
    # Get the correct assignment
    if args.assignment:
        if args.assignment in assignments:
            selected_assignment = args.assignment
        else:
            print("Assignment " + args.assignment + " does not exist. Make sure your wrote the name exactly. Use -la to list all the assignments.")
            exit(1)
    
    # Get the correct folder name for the working programs
    workingProgramsFolderName += slash + selected_assignment

    program = args.program
    programName = program.split(".")[0]
    programName+=".userCompiled"
    
    if not os.path.exists(program):
        print("Program " + program + " does not exist. Make sure you wrote the name correctly and that your program is located in the main folder.")
        exit(1)

    # Command to compile the C++ program 
    compileArr = ["g++ -std=c++20 -o", programName, program]
    compileCmd = " ".join(str(x) for x in compileArr)
    # Compile the C++ program 
    compileProcess = subprocess.run(compileCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # Check if everything compiled successfully, else exit
    if compileProcess.returncode == 0: 
        print("Compilation successful.") 
    else:
        print("Compilation failed.")
        print("There might be an error in your code. If you are sure that isn't the case reade further: \n")
        print("This is most likely due to an incorrect version of gcc on your system.")
        print("This program uses c++20, which comes with gcc 11 and above.")
        print("If you are on linux or macos, you might fix the issue by running the following commands in your terminal:")
        print("sudo apt-get update")
        print("sudo apt-get upgrade")
        print("sudo apt install build-essential")
        exit(1)


        
    # Clear previous outputs
    print("Deleting old outputs...")
    if os.path.exists(workingOutputFolderName):
        shutil.rmtree(workingOutputFolderName)
    os.makedirs(workingOutputFolderName)
    if os.path.exists(userOutputFolderName):
        shutil.rmtree(userOutputFolderName)
    os.makedirs(userOutputFolderName)
    if os.path.exists(allOutputsFolderName):
        shutil.rmtree(allOutputsFolderName)
    os.makedirs(allOutputsFolderName)
    os.makedirs(allOutputsFolderName + slash + "passed")
    os.makedirs(allOutputsFolderName + slash + "failed")
    print("Cleared all temporary folders and previous outputs.")
    
    workingProgramNames = os.listdir("." + slash + workingProgramsFolderName)
    # Give execute permission to the working programs
    if (operatingSystem == "Linux" or operatingSystem == "Darwin"):
        for currWorkingProgram in workingProgramNames:
            # In some cases the programs might not have execute permission, so do that first
            path = "." + slash + workingProgramsFolderName + slash + currWorkingProgram
            giveExecutePermission(path)
        print("Gave all working programs execute permissions")
        
    
    # Infinite loop for infinite test
    print("Starting test program.")
    while True:
        testProgram(programName);
        
        
setup()