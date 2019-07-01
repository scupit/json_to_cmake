import data
import os

def getOutputCmakeName(name):
    return name.upper() + "_CMAKE_OUTPUT"

def getOutputSourcesName(name):
    return name.upper() + "_SOURCES"

def inBraces(string):
    return "${" + string + "}"



class CMakeBuilder():

    def __init__(self, filepath):
        self.writestream = open(filepath, mode='w')

    # def close(self):
        # close(self.writestream)

    def writeNewlines(self, num=1):
        while num > 0:
            print(file=self.writestream)
            num -= 1

    def writeVersion(self, version):
        print("cmake_minimum_required( VERSION", version, ")", file=self.writestream)

    def writeProjectName(self, projectName):
        print("project(", projectName, ")", file=self.writestream)

    def writeCppStandards(self, allowedCppStandards, defaultCppStandard = ""):
        if not defaultCppStandard in allowedCppStandards or defaultCppStandard == "":
            defaultCppStandard = allowedCppStandards[0]

        print("\nset( CXX_COMPILER_STANDARD \"", defaultCppStandard, "\" CACHE STRING \"C++ compiler standard year\")", sep="",  file=self.writestream)

        print("\nset_property( CACHE CXX_COMPILER_STANDARD PROPERTY STRINGS", end="", file=self.writestream)

        for standard in allowedCppStandards:
            print(" \"", standard, "\"", sep="", end="", file=self.writestream)
        print(")", file=self.writestream)

        self.writeMessage("Using CXX compiler standard -std=c++${CXX_COMPILER_STANDARD}", before="\n")

    def writeCStandards(self, allowedCStandards, defaultCStandard = ""):
        if not defaultCStandard in allowedCStandards or defaultCStandard == "":
            defaultCStandard = allowedCStandards[0]

        print("\nset( C_COMPILER_STANDARD \"", defaultCStandard, "\" CACHE STRING \"C compiler standard year\")", sep="", file=self.writestream)

        print("\nset_property( CACHE C_COMPILER_STANDARD PROPERTY STRINGS", end="", file=self.writestream)

        for standard in allowedCStandards:
            print(" \"", standard, "\"", sep="", end="", file=self.writestream)
        print(")", file=self.writestream)

        self.writeMessage("Using C compiler standard -std=c${C_COMPILER_STANDARD}", before="\n")

    # TODO: Add support for linked libraries and linked imported libraries. (Once support
    # is added in the Data class)
    def writeExecutableOutput(self, name, sourcesArr, includeDirsArr, exeOutputDir):
        outputTargetWriteName = getOutputCmakeName(name)
        outputTargetSourcesName = getOutputSourcesName(name)

        # Set CMake sources variable for this output
        # NOTE: This is not necessary for functionality, but will make
        # the file more human readable
        print("\nset(", outputTargetSourcesName, file=self.writestream)

        # We can assume that the sourcesArray should have at least one name in it
        # since compilation always requires at least one file
        for sourceFileName in sourcesArr:
            print("\t${PROJECT_SOURCE_DIR}/", sourceFileName, sep="", file=self.writestream)

        print(")", file=self.writestream)

        # Create the CMake executable
        print("\nadd_executable(", outputTargetWriteName, inBraces(outputTargetSourcesName), ")", file=self.writestream)

        # Add include dirs to the executable
        print("\ntarget_include_directories(", outputTargetWriteName, "PRIVATE", file=self.writestream)

        for includedDir in includeDirsArr:
            print("\t${PROJECT_SOURCE_DIR}/", includedDir, sep="", file=self.writestream)
        print(")", file=self.writestream)

        # Set output directories for the target
        print("\nset_target_properties(", outputTargetWriteName, file=self.writestream)
        print("\tPROPERTIES", file=self.writestream)

        print("\tRUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", exeOutputDir, "/${CMAKE_BUILD_TYPE}", sep="", file=self.writestream)
        print(")", file=self.writestream)

        # TODO: Handle printing imported library data
        # TODO: Handle printing project-compiled library data

    def writeLibraryOutput(self, name, isStatic, sourcesArr, includeDirsArr, archiveOutputDir, libOutputDir):
        outputTargetWriteName = getOutputCmakeName(name)
        outputTargetSourcesName = getOutputSourcesName(name)
        libType = "STATIC" if isStatic else "SHARED"

        # Set CMake sources variable for this output
        # NOTE: This is not necessary for functionality, but will make
        # the file more human readable
        print("\nset(", outputTargetSourcesName, file=self.writestream)

        # We can assume that the sourcesArray should have at least one name in it
        # since compilation always requires at least one file
        for sourceFileName in sourcesArr:
            print("\t${PROJECT_SOURCE_DIR}/", sourceFileName, sep="", file=self.writestream)

        print(")", file=self.writestream)

        # Create the CMake executable
        print("\nadd_library(", outputTargetWriteName, libType,  inBraces(outputTargetSourcesName), ")", file=self.writestream)


        # Add include dirs to the executable
        print("\ntarget_include_directories(", outputTargetWriteName, "PRIVATE", file=self.writestream)

        for includedDir in includeDirsArr:
            print("\t${PROJECT_SOURCE_DIR}/", includedDir, sep="", file=self.writestream)
        print(")", file=self.writestream)

        # Set output directories for the target
        print("\nset_target_properties(", outputTargetWriteName, file=self.writestream)
        print("\tPROPERTIES", file=self.writestream)
        print("\tARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", archiveOutputDir, "/${CMAKE_BUILD_TYPE}", sep="", file=self.writestream)
        print("\tLIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", libOutputDir, "/${CMAKE_BUILD_TYPE}", sep="", file=self.writestream)
        print(")", file=self.writestream)

        # TODO: Handle printing imported library data
        # TODO: Handle printing project-compiled library data

    def writeBuildTarget(self, target, cFlags, cppFlags):
        targetVar = ""
        # TODO: handle scenario where an invalid target string is given
        if target.lower() == "debug":
            targetVar = "Debug"
        elif target.lower() == "release":
            targetVar = "Release"

        # In cmake file: do these things if the chosen build type is this one
        self.writeNewlines()
        self.writeIf("${CMAKE_BUILD_TYPE} STREQUAL " + targetVar)

        # C flag section
        print("\tset( C_FLAGS \"", end="", file=self.writestream)

        for flag in cFlags:
            print(flag, end=" ", file=self.writestream)
        print("\" CACHE STRING \"C Compiler options\" )", file=self.writestream)

        # CXX flag section
        print("\tset( CXX_FLAGS \"", end="", file=self.writestream)

        for flag in cppFlags:
            print(flag, end=" ", file=self.writestream)
        print("\" CACHE STRING \"CXX Compiler options\" )", file=self.writestream)

        self.writeMessage("Building project ${CMAKE_BUILD_TYPE} configuration", before="\t")
        self.writeEndif()

    def writeBuildTargetList(self, targets):
        print("\nset_property( CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS ", end="", file=self.writestream)

        for target in targets:
            print("\"", target[0].upper() + target[1:], "\"", end=" ", sep="", file=self.writestream)
        print(")", file=self.writestream)

    def writeMessage(self, message, before=""):
        print(before + "message( \"", message, "\" )", sep="", file=self.writestream)

    def writeIf(self, condition):
        print("if(", condition, ")", file=self.writestream)

    def writeElseIf(self, condition):
        print("elseif(", condition, ")", file=self.writestream)

    def writeElse(self):
        print("else()", file=self.writestream)

    def writeEndif(self):
        print("endif()", file=self.writestream)
