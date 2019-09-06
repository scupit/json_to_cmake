import data
import os
import HelperFunctions
import HelperVariables

class CMakeBuilder():

    def __init__(self, filepath):
        self.writestream = open(filepath, mode='w')

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

    def writeExecutableOutput(self, name, sourcesArr, includeDirsArr, exeOutputDir):
        outputTargetWriteName = HelperFunctions.getOutputCmakeName(name)
        outputTargetSourcesName = HelperFunctions.getOutputSourcesName(name)

        # Set CMake sources variable for this output
        # NOTE: This is not necessary for functionality, but will make
        # the file more human readable
        print("\nset(", outputTargetSourcesName, file=self.writestream)

        # We can assume that the sourcesArray should have at least one name in it
        # since compilation always requires at least one file
        for sourceFileName in sourcesArr:
            if sourceFileName[0] == '$':
                print("\t", sourceFileName, sep="", file=self.writestream)
            else:
                print("\t${PROJECT_SOURCE_DIR}/", sourceFileName, sep="", file=self.writestream)

        print(")", file=self.writestream)

        # Create the CMake executable
        print("\nadd_executable(", outputTargetWriteName, HelperFunctions.inBraces(outputTargetSourcesName), ")", file=self.writestream)

        # Add include dirs to the executable
        print("\ntarget_include_directories(", outputTargetWriteName, "PRIVATE", file=self.writestream)

        for includedDir in includeDirsArr:
            if includedDir[0] == '$':
                print("\t", includedDir, sep="", file=self.writestream)
            else:
                print("\t${PROJECT_SOURCE_DIR}/", includedDir, sep="", file=self.writestream)
        print(")", file=self.writestream)

        # Set output directories for the target
        print("\nset_target_properties(", outputTargetWriteName, file=self.writestream)
        print("\tPROPERTIES", file=self.writestream)

        print("\tRUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", exeOutputDir, "/${CMAKE_BUILD_TYPE}", sep="", file=self.writestream)
        print(")", file=self.writestream)

    def writeLibraryOutput(self, name, isStatic, sourcesArr, includeDirsArr, archiveOutputDir, libOutputDir):
        outputTargetWriteName = HelperFunctions.getOutputCmakeName(name)
        outputTargetSourcesName = HelperFunctions.getOutputSourcesName(name)
        libType = "STATIC" if isStatic else "SHARED"

        # Set CMake sources variable for this output
        # NOTE: This is not necessary for functionality, but will make
        # the file more human readable
        print("\nset(", outputTargetSourcesName, file=self.writestream)

        # We can assume that the sourcesArray should have at least one name in it
        # since compilation always requires at least one file
        for sourceFileName in sourcesArr:
            if sourceFileName[0] == '$':
                print("\t", sourceFileName, sep="", file=self.writestream)
            else:
                print("\t${PROJECT_SOURCE_DIR}/", sourceFileName, sep="", file=self.writestream)
        print(")", file=self.writestream)

        # Create the CMake executable
        print("\nadd_library(", outputTargetWriteName, libType, HelperFunctions.inBraces(outputTargetSourcesName), ")", file=self.writestream)

        print("\nset(", outputTargetWriteName + HelperVariables.INCLUDE_DIRS_SUFFIX, file=self.writestream)
        for includedDir in includeDirsArr:
            if includedDir[0] == '$':
                print("\t", includedDir, sep="", file=self.writestream)
            else:
                print("\t${PROJECT_SOURCE_DIR}/", includedDir, sep="", file=self.writestream)
        print(")", file=self.writestream)

        # Add include dirs to the executable
        print("\ntarget_include_directories(", outputTargetWriteName, "PRIVATE", HelperFunctions.inBraces(outputTargetWriteName + HelperVariables.INCLUDE_DIRS_SUFFIX), ")", file=self.writestream)

        # Set output directories for the target
        print("\nset_target_properties(", outputTargetWriteName, file=self.writestream)
        print("\tPROPERTIES", file=self.writestream)
        print("\tARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", archiveOutputDir, "/${CMAKE_BUILD_TYPE}", sep="", file=self.writestream)
        print("\tLIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", libOutputDir, "/${CMAKE_BUILD_TYPE}", sep="", file=self.writestream)
        print(")", file=self.writestream)

    # Problem: if one library has multiple lib_files, then they should be written as separate library entries.
    # Ex: libname_0, libname_1
    def writeImportedLib(self, name, isStatic, libFilesArr, includeDirsArr, headerFilesArr):
        libType = "STATIC" if isStatic else "SHARED"

        # Add these include dirs to a variable
        print("\nset(", name + HelperVariables.INCLUDE_DIRS_SUFFIX, file=self.writestream)
        for includeDirName in includeDirsArr:
            print("\t" + HelperFunctions.inBraces("PROJECT_SOURCE_DIR") + "/" + includeDirName, file=self.writestream)
        print(")", file=self.writestream)

        # Add header files to a variable
        print("\nset(", name+"_HEADER_FILES", file=self.writestream)
        for headerFileName in headerFilesArr:
            print("\t" + HelperFunctions.inBraces("PROJECT_SOURCE_DIR") + "/" + headerFileName, file=self.writestream)
        print(")", file=self.writestream)

        # Write a library for each file (so it is valid in cmake).
        # Each file will be internally named as libname_0, libname_1, etc. by index.
        for libFileIndex in range(0, len(libFilesArr)):
            modifiedLibName = HelperFunctions.modifyNameWithIndex(name, libFileIndex)

            # Add the imported library
            print("\nadd_library(", modifiedLibName, libType, "IMPORTED", ")", file=self.writestream)

            indexOfLastSlash = libFilesArr[libFileIndex].rfind('/', 0, len(libFilesArr[libFileIndex]) - 2)
            pathPrefix = libFilesArr[libFileIndex][0:indexOfLastSlash + 1]
            libFileName = libFilesArr[libFileIndex][indexOfLastSlash + 1 :].replace('/', '')

            # If OS is Windows
            self.writeIf(HelperVariables.WINDOWS_OS_NAME)

            # Set the import location for the library
            print("set_target_properties(", modifiedLibName, file=self.writestream)
            print("\tPROPERTIES", file=self.writestream)
            if isStatic:
                print("\tIMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".a", sep="", file=self.writestream)
            else:
                print("\tIMPORTED_IMPLIB ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".dll.a", sep="", file=self.writestream)
            print(")", file=self.writestream)

            # Else if OS in UNIX (mainly linux or mac)
            self.writeElseIf(HelperVariables.UNIX_OS_NAME)

            # Set the import location for the library
            print("set_target_properties(", modifiedLibName, file=self.writestream)
            print("\tPROPERTIES", file=self.writestream)
            if isStatic:
                print("\tIMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".a", sep="", file=self.writestream)
            else:
                print("\tIMPORTED_IMPLIB ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".so", sep="", file=self.writestream)
            print(")", file=self.writestream)

            self.writeEndif()


    def writeBuildTarget(self, target, cFlags, cppFlags):
        targetVar = target[0].upper() + target[1:].lower()

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

    def writeDefaultBuildTarget(self, targetName):
        if targetName != "":
            self.writeNewlines()
            self.writeIf("\"${CMAKE_BUILD_TYPE}\" STREQUAL \"\"")
            print("\tset( CMAKE_BUILD_TYPE \"", targetName[0].upper() + targetName[1:].lower(), "\" )", sep="", file=self.writestream)
            self.writeEndif()

    # NOTE: When an imported library "name" has multiple 'lib_files' defined, make sure to pass each one as libname_0, libname_1, etc.
    def writeLinkedLibs(self, outputNameLinkingTo, libNamesLinking, importedLibsObject):
        print("\ntarget_link_libraries(", HelperFunctions.getOutputCmakeName(outputNameLinkingTo), file=self.writestream)
        for libName in libNamesLinking:
            # Write each index-modified library name if libName is found in the imported libraries
            if libName in importedLibsObject:
                for index in range(0, len(importedLibsObject[libName]["lib_files"])):
                    print("\t", HelperFunctions.modifyNameWithIndex(libName, index), file=self.writestream)
            else:
                print("\t", HelperFunctions.getOutputCmakeName(libName), file=self.writestream)

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
