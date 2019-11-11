import data
import os
import HelperFunctions
import HelperVariables

class CMakeBuilder():

    def __init__(self, filepath):
        self.writestream = open(filepath, mode='w')

    def writeNewlines(self, num=1):
        while num > 0:
            self.printToOwnStream()
            num -= 1

    def writeVersion(self, version):
        self.printToOwnStream("cmake_minimum_required( VERSION", version, ")")

    def writeProjectName(self, projectName):
        self.printToOwnStream("project(", projectName, ")")

    def writeCppStandards(self, allowedCppStandards, defaultCppStandard = ""):
        if not defaultCppStandard in allowedCppStandards or defaultCppStandard == "":
            defaultCppStandard = allowedCppStandards[0]

        self.printToOwnStream("\nset( CXX_COMPILER_STANDARD \"", defaultCppStandard, "\" CACHE STRING \"C++ compiler standard year\")", sep="")
        self.printToOwnStream("set_property( CACHE CXX_COMPILER_STANDARD PROPERTY STRINGS ", end="")

        for standard in allowedCppStandards:
            self.printToOwnStream("\"", standard, "\" ", sep="", end="")
        self.printToOwnStream(")")

        self.writeMessage("Using CXX compiler standard -std=c++${CXX_COMPILER_STANDARD}")

    def writeCStandards(self, allowedCStandards, defaultCStandard = ""):
        if not defaultCStandard in allowedCStandards or defaultCStandard == "":
            defaultCStandard = allowedCStandards[0]

        self.printToOwnStream("\nset( C_COMPILER_STANDARD \"", defaultCStandard, "\" CACHE STRING \"C compiler standard year\")", sep="")
        self.printToOwnStream("set_property( CACHE C_COMPILER_STANDARD PROPERTY STRINGS ", end="")

        for standard in allowedCStandards:
            self.printToOwnStream("\"", standard, "\" ", sep="", end="")
        self.printToOwnStream(")")

        self.writeMessage("Using C compiler standard -std=c${C_COMPILER_STANDARD}")

    def writeExecutableOutput(self, name, sourcesArr, includeDirsArr, exeOutputDir):
        outputTargetWriteName = HelperFunctions.getOutputCmakeName(name)
        outputTargetSourcesName = HelperFunctions.getOutputSourcesName(name)

        # Set CMake sources variable for this output
        # NOTE: This is not necessary for functionality, but will make
        # the file more human readable
        self.printToOwnStream("\nset(", outputTargetSourcesName)

        # We can assume that the sourcesArray should have at least one name in it
        # since compilation always requires at least one file
        for sourceFileName in sourcesArr:
            if sourceFileName[0] == '$':
                self.printToOwnStream("\t", sourceFileName, sep="")
            else:
                self.printToOwnStream("\t${PROJECT_SOURCE_DIR}/", sourceFileName, sep="")
        self.printToOwnStream(")")

        # Create the CMake executable
        self.printToOwnStream("\nadd_executable(", outputTargetWriteName, HelperFunctions.inBraces(outputTargetSourcesName), ")")

        # Add include dirs to the executable
        self.printToOwnStream("\ntarget_include_directories(", outputTargetWriteName, "PRIVATE")

        for includedDir in includeDirsArr:
            if includedDir[0] == '$':
                self.printToOwnStream("\t", includedDir, sep="")
            else:
                self.printToOwnStream("\t${PROJECT_SOURCE_DIR}/", includedDir, sep="")
        self.printToOwnStream(")")

        # Set output directories for the target
        self.printToOwnStream("\nset_target_properties(", outputTargetWriteName)
        self.printToOwnStream("\tPROPERTIES")
        self.printToOwnStream("\tRUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", exeOutputDir, "/${CMAKE_BUILD_TYPE}", sep="")
        self.printToOwnStream(")")

    def writeLibraryOutput(self, name, isStatic, sourcesArr, includeDirsArr, archiveOutputDir, libOutputDir):
        outputTargetWriteName = HelperFunctions.getOutputCmakeName(name)
        outputTargetSourcesName = HelperFunctions.getOutputSourcesName(name)
        libType = "STATIC" if isStatic else "SHARED"

        # Set CMake sources variable for this output
        # NOTE: This is not necessary for functionality, but will make
        # the file more human readable
        self.printToOwnStream("\nset(", outputTargetSourcesName)

        # We can assume that the sourcesArray should have at least one name in it
        # since compilation always requires at least one file
        for sourceFileName in sourcesArr:
            if sourceFileName[0] == '$':
                self.printToOwnStream("\t", sourceFileName, sep="")
            else:
                self.printToOwnStream("\t${PROJECT_SOURCE_DIR}/", sourceFileName, sep="")
        self.printToOwnStream(")")

        # Create the CMake executable
        self.printToOwnStream("\nadd_library(", outputTargetWriteName, libType, HelperFunctions.inBraces(outputTargetSourcesName), ")")

        self.printToOwnStream("\nset(", outputTargetWriteName + HelperVariables.INCLUDE_DIRS_SUFFIX)
        for includedDir in includeDirsArr:
            if includedDir[0] == '$':
                self.printToOwnStream("\t", includedDir, sep="")
            else:
                self.printToOwnStream("\t${PROJECT_SOURCE_DIR}/", includedDir, sep="")
        self.printToOwnStream(")")

        # Add include dirs to the executable
        self.printToOwnStream("\ntarget_include_directories(", outputTargetWriteName, "PRIVATE", HelperFunctions.inBraces(outputTargetWriteName + HelperVariables.INCLUDE_DIRS_SUFFIX), ")")

        # Set output directories for the target
        self.printToOwnStream("\nset_target_properties(", outputTargetWriteName)
        self.printToOwnStream("\tPROPERTIES")
        self.printToOwnStream("\tARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", archiveOutputDir, "/${CMAKE_BUILD_TYPE}", sep="")
        self.printToOwnStream("\tLIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/", libOutputDir, "/${CMAKE_BUILD_TYPE}", sep="")
        self.printToOwnStream(")")

    # Problem: if one library has multiple lib_files, then they should be written as separate library entries.
    # Ex: libname_0, libname_1
    def writeImportedLib(self, name, isStatic, libFilesArr, includeDirsArr, headerFilesArr):
        libType = "STATIC" if isStatic else "SHARED"

        # Add these include dirs to a variable
        self.printToOwnStream("\nset(", name + HelperVariables.INCLUDE_DIRS_SUFFIX)
        for includeDirName in includeDirsArr:
            self.printToOwnStream("\t" + HelperFunctions.inBraces("PROJECT_SOURCE_DIR") + "/" + includeDirName)
        self.printToOwnStream(")")

        # Add header files to a variable
        self.printToOwnStream("\nset(", name + HelperVariables.HEADER_FILES_SUFFIX)
        for headerFileName in headerFilesArr:
            self.printToOwnStream("\t" + HelperFunctions.inBraces("PROJECT_SOURCE_DIR") + "/" + headerFileName)
        self.printToOwnStream(")")

        # Write a library for each file (so it is valid in cmake).
        # Each file will be internally named as libname_0, libname_1, etc. by index.
        for libFileIndex in range(0, len(libFilesArr)):
            modifiedLibName = HelperFunctions.modifyNameWithIndex(name, libFileIndex)

            # Add the imported library
            self.printToOwnStream("\nadd_library(", modifiedLibName, libType, "IMPORTED", ")")

            indexOfLastSlash = libFilesArr[libFileIndex].rfind('/', 0, len(libFilesArr[libFileIndex]) - 2)
            pathPrefix = libFilesArr[libFileIndex][0:indexOfLastSlash + 1]
            libFileName = libFilesArr[libFileIndex][indexOfLastSlash + 1 :].replace('/', '')

            # If OS is Windows
            self.writeIf(HelperVariables.WINDOWS_OS_NAME)

            # Set the import location for the library
            self.printToOwnStream("set_target_properties(", modifiedLibName)
            self.printToOwnStream("\tPROPERTIES")
            if isStatic:
                self.printToOwnStream("\tIMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".a", sep="")
            else:
                self.printToOwnStream("\tIMPORTED_IMPLIB ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".dll.a", sep="")
            self.printToOwnStream(")")

            # Else if OS in UNIX (mainly linux or mac)
            self.writeElseIf(HelperVariables.UNIX_OS_NAME)

            # Set the import location for the library
            self.printToOwnStream("set_target_properties(", modifiedLibName)
            self.printToOwnStream("\tPROPERTIES")
            if isStatic:
                self.printToOwnStream("\tIMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".a", sep="")
            else:
                self.printToOwnStream("\tIMPORTED_IMPLIB ${PROJECT_SOURCE_DIR}/", pathPrefix + "lib" + libFileName + ".so", sep="")
            self.printToOwnStream(")")

            self.writeEndif()


    def writeBuildTarget(self, target, cFlags, cppFlags):
        # Compiler flags are defined per build_target
        self.writeNewlines()
        self.writeIf("${CMAKE_BUILD_TYPE} STREQUAL " + HelperFunctions.capFirstLowerRest(target))

        # C flag section
        self.printToOwnStream("\tset( C_FLAGS \"", end="")

        for flag in cFlags:
            self.printToOwnStream(flag, end=" ")
        self.printToOwnStream("\" CACHE STRING \"C Compiler options\" )")
        self.writeMessage("Using C compiler flags: ${C_FLAGS}", before="\t")
        self.writeNewlines(1)

        # CXX flag section
        self.printToOwnStream("\tset( CXX_FLAGS \"", end="")

        for flag in cppFlags:
            self.printToOwnStream(flag, end=" ")
        self.printToOwnStream("\" CACHE STRING \"CXX Compiler options\" )")
        self.writeMessage("Using CXX compiler flags: ${CXX_FLAGS}", before="\t")
        self.writeNewlines(1)

        self.writeMessage("Building project ${CMAKE_BUILD_TYPE} configuration", before="\t")
        self.writeEndif()

    def writeBuildTargetList(self, targets):
        self.printToOwnStream("\nset_property( CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS ", end="")

        for target in targets:
            self.printToOwnStream("\"", HelperFunctions.capFirstLowerRest(target), "\"", end=" ", sep="")
        self.printToOwnStream(")")

    def writeDefaultBuildTarget(self, targetName):
        if targetName != "":
            self.writeNewlines()
            self.writeIf("\"${CMAKE_BUILD_TYPE}\" STREQUAL \"\"")
            self.printToOwnStream("\tset( CMAKE_BUILD_TYPE \"", HelperFunctions.capFirstLowerRest(targetName), "\" )", sep="")
            self.writeEndif()

    # NOTE: When an imported library "name" has multiple 'lib_files' defined, make sure to pass each one as libname_0, libname_1, etc.
    def writeLinkedLibs(self, outputNameLinkingTo, libNamesLinking, importedLibsObject):
        self.printToOwnStream("\ntarget_link_libraries(", HelperFunctions.getOutputCmakeName(outputNameLinkingTo))
        for libName in libNamesLinking:
            # Write each index-modified library name if libName is found in the imported libraries
            if libName in importedLibsObject:
                for index in range(0, len(importedLibsObject[libName][HelperVariables.LIB_FILES_TAGNAME])):
                    self.printToOwnStream("\t", HelperFunctions.modifyNameWithIndex(libName, index), sep="")
            else:
                self.printToOwnStream("\t", HelperFunctions.getOutputCmakeName(libName), sep="")
        self.printToOwnStream(")")

    def writeMessage(self, message, before=""):
        self.printToOwnStream(before + "message( \"", message, "\" )", sep="")

    def writeIf(self, condition):
        self.printToOwnStream("if(", condition, ")")

    def writeElseIf(self, condition):
        self.printToOwnStream("elseif(", condition, ")")

    def writeElse(self):
        self.printToOwnStream("else()")

    def writeEndif(self):
        self.printToOwnStream("endif()")

    def printToOwnStream(self, *args, **kwargs):
        print(*args, **kwargs, file=self.writestream)