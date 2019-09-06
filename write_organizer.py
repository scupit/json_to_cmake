from json.decoder import JSONDecodeError
from data import Data
from file_write import CMakeBuilder

import HelperFunctions
import HelperVariables

def writeProjectVersion(fileWriter, jsonDataObject):
    fileWriter.writeVersion(jsonDataObject.cmake_tag_version)

def writeProjectName(fileWriter, jsonDataObject):
    fileWriter.writeProjectName(jsonDataObject.project_name)

def writeProjectOutputs(fileWriter, jsonDataObject):
    for outputNameKey in jsonDataObject.output:
        if jsonDataObject.output[outputNameKey][HelperVariables.TYPE_TAGNAME] == "executable":
            fileWriter.writeExecutableOutput(outputNameKey, jsonDataObject.output[outputNameKey][HelperVariables.SOURCE_FILES_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.EXE_OUTPUT_DIR_TAGNAME])
        elif jsonDataObject.output[outputNameKey][HelperVariables.TYPE_TAGNAME] == "static_lib":
            fileWriter.writeLibraryOutput(outputNameKey, True, jsonDataObject.output[outputNameKey][HelperVariables.SOURCE_FILES_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.LIB_OUTPUT_DIR_TAGNAME])
        elif jsonDataObject.output[outputNameKey][HelperVariables.TYPE_TAGNAME] == "shared_lib":
            # Can assume the output type is "shared_lib" at this point
            fileWriter.writeLibraryOutput(outputNameKey, False, jsonDataObject.output[outputNameKey][HelperVariables.SOURCE_FILES_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME], jsonDataObject.output[outputNameKey][HelperVariables.LIB_OUTPUT_DIR_TAGNAME])
        # else:
            # Raise some sort of 'invalid output type given' error. This code should never be reached due to type checking in the data class, but you never know.

def writeProjectImportedLibs(fileWriter, jsonDataObject):
    # Write imported_libs
    for importedLibName in jsonDataObject.imported_libs:
        fileWriter.writeImportedLib(importedLibName, jsonDataObject.imported_libs[importedLibName][HelperVariables.TYPE_TAGNAME] == "static", jsonDataObject.imported_libs[importedLibName][HelperVariables.LIB_FILES_TAGNAME], jsonDataObject.imported_libs[importedLibName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], jsonDataObject.imported_libs[importedLibName][HelperVariables.HEADER_FILES_TAGNAME])

def writeProjectLinks(fileWriter, jsonDataObject):
    # Write linked_libs
    for outputName in jsonDataObject.link_libs:
        # This if statement might be unnecessary, since if no elements are
        # contained, shouldn't the number of keys be 0?
        if not len(jsonDataObject.link_libs[outputName]) == 0:
            fileWriter.writeLinkedLibs(outputName, jsonDataObject.link_libs[outputName], jsonDataObject.imported_libs)

# Write C++ standards
def writeProjectCppStandards(fileWriter, jsonDataObject):
    fileWriter.writeCppStandards(jsonDataObject.allowed_cpp_standards, jsonDataObject.default_cpp_standard)

# Write C standards
def writeProjectCStandards(fileWriter, jsonDataObject):
    fileWriter.writeCStandards(jsonDataObject.allowed_c_standards, jsonDataObject.default_c_standard)

# Write project build targets
def writeProjectBuildTargets(fileWriter, jsonDataObject):
    targetKeys = list(jsonDataObject.targets)

    if jsonDataObject.default_target != "":
        fileWriter.writeDefaultBuildTarget(jsonDataObject.default_target)
    else:
        fileWriter.writeDefaultBuildTarget(targetKeys[0])

    fileWriter.writeBuildTargetList(targetKeys)
    for buildTargetName in targetKeys:
        fileWriter.writeBuildTarget(buildTargetName, jsonDataObject.targets[buildTargetName][HelperVariables.C_FLAGS_TAGNAME], jsonDataObject.targets[buildTargetName][HelperVariables.CPP_FLAGS_TAGNAME])

def writeCMakeFiles(rootDir):
    try:
        try:
            jsonDataObject = Data(rootDir)
        except FileNotFoundError as e:
            print("In initialization of Data object: ")
            raise e
        except JSONDecodeError as e:
            print("Invalid JSON provided in initialization of Data object...")
            raise e
        fileWriter = CMakeBuilder(rootDir + "/CMakeLists.txt")

        writeProjectVersion(fileWriter, jsonDataObject)
        writeProjectName(fileWriter, jsonDataObject)
        writeProjectOutputs(fileWriter, jsonDataObject)
        writeProjectImportedLibs(fileWriter, jsonDataObject)
        writeProjectLinks(fileWriter, jsonDataObject)
        writeProjectCStandards(fileWriter, jsonDataObject)
        writeProjectCppStandards(fileWriter, jsonDataObject)
        writeProjectBuildTargets(fileWriter, jsonDataObject)

    except KeyError as e:
        print("ERROR: Problem with JSON file. See below:\n")
        print(str(e))
        raise e
    except TypeError as e:
        print("(TYPE) ERROR:", str(e))
        raise e
