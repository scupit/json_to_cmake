from json.decoder import JSONDecodeError
from data import Data
from file_write import CMakeBuilder

import HelperFunctions
import HelperVariables

# Write CMake project version
def writeProjectVersion(fileWriter, jsonDataObject):
    # fileWriter.writeVersion(jsonDataObject.cmake_tag_version)
    fileWriter.writeVersion("3.12")

# Write project name
def writeProjectName(fileWriter, jsonDataObject):
    fileWriter.writeProjectName(jsonDataObject.project_name)

# Write project output items
def writeProjectOutputs(fileWriter, jsonDataObject):
    for outputNameKey in jsonDataObject.output:
        outputItem = jsonDataObject.output[outputNameKey]
        if outputItem[HelperVariables.TYPE_TAGNAME] == HelperVariables.OUTPUT_TYPES["EXE"]:
            fileWriter.writeExecutableOutput(outputNameKey, outputItem[HelperVariables.SOURCE_FILES_TAGNAME], outputItem[HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], outputItem[HelperVariables.EXE_OUTPUT_DIR_TAGNAME])
        elif outputItem[HelperVariables.TYPE_TAGNAME] == HelperVariables.OUTPUT_TYPES["STATIC_LIB"]:
            fileWriter.writeLibraryOutput(outputNameKey, True, outputItem[HelperVariables.SOURCE_FILES_TAGNAME], outputItem[HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], outputItem[HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME], outputItem[HelperVariables.LIB_OUTPUT_DIR_TAGNAME])
        elif outputItem[HelperVariables.TYPE_TAGNAME] == HelperVariables.OUTPUT_TYPES["SHARED_LIB"]:
            # Can assume the output type is "shared_lib" at this point
            fileWriter.writeLibraryOutput(outputNameKey, False, outputItem[HelperVariables.SOURCE_FILES_TAGNAME], outputItem[HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], outputItem[HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME], outputItem[HelperVariables.LIB_OUTPUT_DIR_TAGNAME])
        # else:
            # Raise some sort of 'invalid output type given' error. This code should never be reached due to type checking in the data class, but you never know.

# Write imported_libs
def writeProjectImportedLibs(fileWriter, jsonDataObject):
    for importedLibName in jsonDataObject.imported_libs:
        fileWriter.writeImportedLib(importedLibName, jsonDataObject.imported_libs[importedLibName][HelperVariables.LIB_FILES_TAGNAME], jsonDataObject.imported_libs[importedLibName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME], jsonDataObject.imported_libs[importedLibName][HelperVariables.HEADER_FILES_TAGNAME])

# Write linked_libs
def writeProjectLinks(fileWriter, jsonDataObject):
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

        fileWriter.writeWaterMark()
        writeProjectVersion(fileWriter, jsonDataObject)
        writeProjectName(fileWriter, jsonDataObject)
        writeProjectImportedLibs(fileWriter, jsonDataObject)
        writeProjectOutputs(fileWriter, jsonDataObject)
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
