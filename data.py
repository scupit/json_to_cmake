import io
import json
from pathlib import Path
import glob

import HelperFunctions
import HelperVariables

jsonFileName = "cmake_data.json"
defCppStandard = "11"
defCStandard = "99"

allowedImportedLibTypeNames = [
    "shared",
    HelperVariables.OUTPUT_TYPES["SHARED_LIB"],
    "static",
    HelperVariables.OUTPUT_TYPES["STATIC_LIB"]
]

cppSourceFileTypes = [
    "cpp",
    "c++",
    "cxx"
]

cppHeaderFileTypes = [
    "hpp",
    "h++",
    "hxx",
    "h"
]

cHeaderFileTypes = [
    "h"
]

cSourceFileTypes = [
    "c"
]

allSourceTypes = set(cppSourceFileTypes + cSourceFileTypes)
allHeaderTypes = set(cppHeaderFileTypes + cHeaderFileTypes)
allFileTypes = set(cppSourceFileTypes + cppHeaderFileTypes + cHeaderFileTypes + cSourceFileTypes)

def fixWindowsPath(pathString):
    return pathString.replace('\\', '/')

def fixFilePaths(basePath, arrayOfPathStrings):
    if str(basePath) != ".":
        # Remove the basePath argument data from each returned pathString
        # TODO: Refactor this lambda. 'item.find' should not have to be called twice.
        return set(map(lambda item : fixWindowsPath(item[ (item.find(str(basePath)) + len(str(basePath)) + 1) if item.find(str(basePath)) >= 0 else 0:]), arrayOfPathStrings))
    return set(map(lambda item : fixWindowsPath(item), arrayOfPathStrings))

# Recursively get all files whose extensions match any of the ones in the 'fileExtensionTypes' array
def getFilesRecursively(basePath, otherPathStrings, fileExtensionTypes):
    fileList = []
    for pathString in otherPathStrings:
        for sourceType in fileExtensionTypes:
            # TODO: Make this more efficient using a combined regex. (The regex should combine all source types, as this currently traverses the directories recursively FOR EACH FILE TYPE. That will get badly very quick for large-scale projects)
            fileList += glob.glob( str( basePath/pathString/("**/*." + sourceType) ), recursive=True )
    return set(fixFilePaths(basePath, fileList))

# Get all directories in a folder
def getDirsRecursively(basePath, otherPathStrings):
    dirList = []
    for pathString in otherPathStrings:
        dirList += glob.glob( str( basePath/pathString ) + '/**/', recursive=True)
    return set(fixFilePaths(basePath, dirList))

# Returns true if the tag is found, else raises a KeyError.
# Optional parentTag is the tag of the object that should contain the missing tag.
# if possible and applicable it should be included for the sake of error message clarity.
# "why" is an optional explanation of why the tag should be added
def _hasTag(pJSON, tag, parentTag = "", why=""):
    if tag in pJSON:
        return True
    else:
        errorMessage = "Tag \"" + tag + "\" missing in " + jsonFileName + ". "

        if parentTag == "":
            errorMessage += "Please add it to the file."
        else:
            errorMessage += "Please add it inside its parent tag \"" + parentTag + "\"."

        if why != "":
            errorMessage += "\n" + why
        raise KeyError(errorMessage)

class Data():
    def __init__(self, rootDir):

        if type(rootDir) is str:
            rootDirPathObject = Path(rootDir)
            parsedJSON = json.load(io.open(str((rootDirPathObject/jsonFileName).resolve())))
        else:
            raise TypeError("Passed a non-string value into the Data(str) constructor. Item: ")

        self.setMinCmakeVersion(parsedJSON)
        self.setProjectName(parsedJSON)
        self.setDefaultCppStandard(parsedJSON)
        self.setDefaultCStandard(parsedJSON)
        self.setAllowedCppStandards(parsedJSON)
        self.setAllowedCStandards(parsedJSON)

        self.setTargets(parsedJSON)
        self.setTargetDefault(parsedJSON)

        self.setOutput(parsedJSON, rootDirPathObject)
        self.setImportedLibs(parsedJSON, rootDirPathObject)
        self.setLinks(parsedJSON)

    # Check for min_cmake_version
    def setMinCmakeVersion(self, parsedJSON):
        if _hasTag(parsedJSON, HelperVariables.CMAKE_MIN_VERSION_TAGNAME):
            self.cmake_tag_version = parsedJSON[HelperVariables.CMAKE_MIN_VERSION_TAGNAME]

    # Check for project_name
    def setProjectName(self, parsedJSON):
        if _hasTag(parsedJSON, HelperVariables.PROJECT_NAME_TAGNAME):
            self.project_name = parsedJSON[HelperVariables.PROJECT_NAME_TAGNAME]

    # Check for default_cpp_standard
    def setDefaultCppStandard(self, parsedJSON):
        if HelperVariables.DEFAULT_CPP_STANDARD_TAGNAME in parsedJSON:
            self.default_cpp_standard = parsedJSON[HelperVariables.DEFAULT_CPP_STANDARD_TAGNAME]
        else:
            self.default_cpp_standard = ""

    # Check for default_c_standard
    def setDefaultCStandard(self, parsedJSON):
        if HelperVariables.DEFAULT_C_STANDARD_TAGNAME in parsedJSON:
            self.default_c_standard = parsedJSON[HelperVariables.DEFAULT_C_STANDARD_TAGNAME]
        else:
            self.default_c_standard = ""

    # Check for allowed_cpp_standards
    def setAllowedCppStandards(self, parsedJSON):
        if _hasTag(parsedJSON, HelperVariables.ALLOWED_CPP_STANDARDS_TAGNAME):
            self.allowed_cpp_standards = parsedJSON[HelperVariables.ALLOWED_CPP_STANDARDS_TAGNAME]

    # Check for allowed_c_standards
    def setAllowedCStandards(self, parsedJSON):
        if _hasTag(parsedJSON, HelperVariables.ALLOWED_C_STANDARDS_TAGNAME):
            self.allowed_c_standards = parsedJSON[HelperVariables.ALLOWED_C_STANDARDS_TAGNAME]

    # Check for output HelperVariables.TARGETS_TAGNAME such as 'debug' and 'release'
    def setTargets(self, parsedJSON):
        if _hasTag(parsedJSON, HelperVariables.TARGETS_TAGNAME, why="Are you building a release binary? Or maybe a debug one? Add the 'targets' tag and add a build type to it."):
            self.targets = {}

            targetTags = parsedJSON[HelperVariables.TARGETS_TAGNAME].keys()

            for targetTag in targetTags:
                # Initialize the target
                self.targets[targetTag] = {}

                # Check target cpp_flags
                if _hasTag(parsedJSON[HelperVariables.TARGETS_TAGNAME][targetTag], HelperVariables.CPP_FLAGS_TAGNAME, parentTag=targetTag, why="C++ compiler flags must be defined (as an array). If for some reason you aren't using any compiler flags, still define this tag as an empty array."):
                    self.targets[targetTag][HelperVariables.CPP_FLAGS_TAGNAME] = parsedJSON[HelperVariables.TARGETS_TAGNAME][targetTag][HelperVariables.CPP_FLAGS_TAGNAME]

                # Check target c_flags
                if _hasTag(parsedJSON[HelperVariables.TARGETS_TAGNAME][targetTag], HelperVariables.C_FLAGS_TAGNAME, parentTag=targetTag, why="C compiler flags must be defined (as an array). If for some reason you aren't using any compiler flags, still define this tag as an emtpy string."):
                    self.targets[targetTag][HelperVariables.C_FLAGS_TAGNAME] = parsedJSON[HelperVariables.TARGETS_TAGNAME][targetTag][HelperVariables.C_FLAGS_TAGNAME]

            # TODO: Add support for more compilers. (Here, might need to manipulate the
            # given flags or require different flag lists altogether if the flags are
            # different across (for) other compilers

    # Check for optional default_target
    def setTargetDefault(self, parsedJSON):
        if HelperVariables.DEFAULT_TARGET_TAGNAME in parsedJSON:
            self.default_target = parsedJSON[HelperVariables.DEFAULT_TARGET_TAGNAME]
        else:
            self.default_target = ""

    # Check for output items
    def setOutput(self, parsedJSON, rootDirPathObject):
        if _hasTag(parsedJSON, HelperVariables.OUTPUT_TAGNAME):
            # output = empty dict, for use later. (Makes changing values easier)
            self.output = {}

            # Since output exists, we can now iterate through its items
            outputItemKeys = parsedJSON[HelperVariables.OUTPUT_TAGNAME].keys()

            # Make sure there are actually items in output, otherwise nothing will
            # be compiled and output
            if len(outputItemKeys) < 1:
                # Use the _hasTag function to throw an error since no tags were found (for consistency and mesaage clarity)
                _hasTag(parsedJSON[HelperVariables.OUTPUT_TAGNAME], "any tag name", parentTag=HelperVariables.OUTPUT_TAGNAME, why="An item must be added to the output tag, otherwise nothing will be compiled and/or built")

            for keyName in outputItemKeys:
                self.output[keyName] = {}
                outputItem = parsedJSON[HelperVariables.OUTPUT_TAGNAME][keyName]

                # Check output item for type
                if _hasTag(outputItem, HelperVariables.TYPE_TAGNAME, parentTag=keyName, why="Without a type, we do not know what to compile your code into. Options: \"executable\", \"static_lib\", \"shared_lib\""):
                    self.output[keyName][HelperVariables.TYPE_TAGNAME] = outputItem[HelperVariables.TYPE_TAGNAME]

                # Define the source_files array for this outputitem
                self.output[keyName][HelperVariables.SOURCE_FILES_TAGNAME] = []

                # Check for base_file (this tag is optional)
                if HelperVariables.BASE_FILE_TAGNAME in outputItem:
                    self.output[keyName][HelperVariables.SOURCE_FILES_TAGNAME].append(outputItem[HelperVariables.BASE_FILE_TAGNAME])

                # Check for r_source_dirs
                if _hasTag(outputItem, HelperVariables.R_SOURCE_DIRS_TAGNAME, parentTag=keyName, why="These are the base directories to be recursively searched for source files. If you are only compiling the (optional) base file, still include this tag with an empty array."):
                    self.output[keyName][HelperVariables.SOURCE_FILES_TAGNAME] += getFilesRecursively(rootDirPathObject, outputItem[HelperVariables.R_SOURCE_DIRS_TAGNAME], allSourceTypes)

                # Check for r_header_dirs
                if _hasTag(outputItem, HelperVariables.R_HEADER_DIRS_TAGNAME, parentTag=keyName, why="Without header files, your files will not be able to include other files, and your program may not compile."):
                    self.output[keyName][HelperVariables.SOURCE_FILES_TAGNAME] += getFilesRecursively(rootDirPathObject, outputItem[HelperVariables.R_HEADER_DIRS_TAGNAME], allHeaderTypes)

                if _hasTag(outputItem, HelperVariables.R_INCLUDE_DIRS_TAGNAME, parentTag=keyName, why="Without passing the include directories of your header files to the compiler, there is a good chance they may not be included."):
                    # Initialize the include_directories array in this output item as well
                    self.output[keyName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME] = list(getDirsRecursively(rootDirPathObject, outputItem[HelperVariables.R_INCLUDE_DIRS_TAGNAME]))

                    if HelperVariables.IND_INCLUDE_DIRS_TAGNAME in outputItem:
                        self.output[keyName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME] += map(lambda relPathString : str(rootDirPathObject/relPathString), outputItem[HelperVariables.IND_INCLUDE_DIRS_TAGNAME])
                        # Make sure no duplicates were added
                        self.output[keyName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME] = list(dict.fromkeys(self.output[keyName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME]))

                if self.output[keyName][HelperVariables.TYPE_TAGNAME].lower() == HelperVariables.OUTPUT_TYPES["EXE"]:
                    # Only executable_output_dir is required
                    if _hasTag(outputItem, HelperVariables.EXE_OUTPUT_DIR_TAGNAME, parentTag=keyName, why="Specifies the directory into which the executable will be build. (Don't use a beginning /)"):
                        self.output[keyName][HelperVariables.EXE_OUTPUT_DIR_TAGNAME] = outputItem[HelperVariables.EXE_OUTPUT_DIR_TAGNAME]
                else:
                    # Assumed to be a library, so both archive_output_dir and library_output_dir are required
                    # Check for archive_output_dir
                    if _hasTag(outputItem, HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME, parentTag=keyName, why="Specifies the directory into which the library 'archive' files will be built. (Don't use a beginning /)"):
                        self.output[keyName][HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME] = outputItem[HelperVariables.ARCHIVE_OUTPUT_DIR_TAGNAME]

                    # Check for library_output_dir
                    if _hasTag(outputItem, HelperVariables.LIB_OUTPUT_DIR_TAGNAME, parentTag=keyName, why="Specifies the directory into which the library files will be built. (Don't use a beginning /)"):
                        self.output[keyName][HelperVariables.LIB_OUTPUT_DIR_TAGNAME] = outputItem[HelperVariables.LIB_OUTPUT_DIR_TAGNAME]

    # Check for imported_libs
    def setImportedLibs(self, parsedJSON, rootDirPathObject):
        self.imported_libs = {}
        if HelperVariables.IMPORTED_LIBS_TAGNAME in parsedJSON:
            importedLibItem = parsedJSON[HelperVariables.IMPORTED_LIBS_TAGNAME]

            libNameKeys = importedLibItem
            for libName in libNameKeys:
                self.imported_libs[libName] = {}

                if _hasTag(importedLibItem[libName], HelperVariables.TYPE_TAGNAME, parentTag=libName, why="An imported lib type must be specified, otherwise the compiler may try to link it as an incorrect type by default."):
                    if not importedLibItem[libName][HelperVariables.TYPE_TAGNAME] in allowedImportedLibTypeNames:
                        raise KeyError("Invalid imported lib type defined in \"" + libName + "\"")
                    # Set the imported lib type
                    self.imported_libs[libName][HelperVariables.TYPE_TAGNAME] = importedLibItem[libName][HelperVariables.TYPE_TAGNAME]

                if _hasTag(importedLibItem[libName], HelperVariables.ROOT_DIR_TAGNAME, parentTag=libName, why="A root directory should be defined so that library files can easily be found."):
                    # Initialize the base path object for these files
                    fileBasePath = Path(importedLibItem[libName][HelperVariables.ROOT_DIR_TAGNAME])

                    if _hasTag(importedLibItem[libName], HelperVariables.LIB_FILES_TAGNAME, parentTag=libName, why="Imported library file names must be given, otherwise no libraries will be imported. Please add at least one lib name to import."):
                        self.imported_libs[libName][HelperVariables.LIB_FILES_TAGNAME] = []
                        for libFileName in importedLibItem[libName][HelperVariables.LIB_FILES_TAGNAME]:
                            self.imported_libs[libName][HelperVariables.LIB_FILES_TAGNAME].append(str(fileBasePath/libFileName))
                        # Fix file paths so they can be correctly prepended with '${PROJECT_SOURCE_DIR}'
                        self.imported_libs[libName][HelperVariables.LIB_FILES_TAGNAME] = list(fixFilePaths(rootDirPathObject, self.imported_libs[libName][HelperVariables.LIB_FILES_TAGNAME]))

                if _hasTag(importedLibItem[libName], HelperVariables.R_INCLUDE_DIRS_TAGNAME, parentTag=libName, why="An array of directories to recursively search for header files should be given here, so that header files needed on library import can be found. If for some reason you do not to import any header files for this project, please define this as an empty array."):
                    self.imported_libs[libName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME] = list(getDirsRecursively(rootDirPathObject, importedLibItem[libName][HelperVariables.R_INCLUDE_DIRS_TAGNAME]))
                    self.imported_libs[libName][HelperVariables.HEADER_FILES_TAGNAME] = list(getFilesRecursively(rootDirPathObject, importedLibItem[libName][HelperVariables.R_HEADER_DIRS_TAGNAME], allHeaderTypes))

    def setLinks(self, parsedJSON):
        # Check for link_libs
        self.link_libs = {}
        if HelperVariables.LINK_LIBS_TAGNAME in parsedJSON:

            outputNameKeys = parsedJSON[HelperVariables.LINK_LIBS_TAGNAME].keys()
            for outputName in outputNameKeys:
                if not outputName in parsedJSON[HelperVariables.OUTPUT_TAGNAME]:
                    raise KeyError("\"" + outputName + "\" tag in \"link_libs\" not found in \"output\". Make sure your names match.")
                for libName in parsedJSON[HelperVariables.LINK_LIBS_TAGNAME][outputName]:
                    if not libName in parsedJSON[HelperVariables.OUTPUT_TAGNAME] and not libName in parsedJSON[HelperVariables.IMPORTED_LIBS_TAGNAME]:
                        raise KeyError("\"" + outputName + "\" tag in \"link_libs\" not found in \"output\" nor \"imported_libs\". Make sure your names match.")
                    # Since adding 'include directories' to an imported library makes no sense, add them to each output item that imports them.
                    elif libName in parsedJSON[HelperVariables.IMPORTED_LIBS_TAGNAME] and len(parsedJSON[HelperVariables.IMPORTED_LIBS_TAGNAME][libName][HelperVariables.R_INCLUDE_DIRS_TAGNAME]) > 0:
                        self.output[outputName][HelperVariables.INCLUDE_DIRECTORIES_TAGNAME].append( HelperFunctions.inBraces(libName + HelperVariables.INCLUDE_DIRS_SUFFIX) )
                        self.output[outputName][HelperVariables.SOURCE_FILES_TAGNAME].append( HelperFunctions.inBraces(libName + HelperVariables.HEADER_FILES_SUFFIX) )

            self.link_libs = parsedJSON[HelperVariables.LINK_LIBS_TAGNAME]