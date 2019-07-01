import io
import json
from pathlib import Path
import glob

# TODO: Require each 'output' item to have a root_dir tag attribute. This will make
# recursively writing CMakeLists.txt files much easier

jsonFileName = "cmake_data.json"
defCppStandard = "11"
defCStandard = "99"

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

def getFilesRecursively(basePath, otherPathStrings, fileExtensionTypes):
    fileList = []
    for pathString in otherPathStrings:
        for sourceType in fileExtensionTypes:
            # TODO: Make this more efficient using a combined regex. (The regex should combine all source types, as this currently traverses the directories recursively FOR EACH FILE TYPE. That will get badly very quick for large-scale projects)
            fileList += glob.glob( str( basePath/pathString/("**/*." + sourceType) ), recursive=True )
    return set(fileList)

def getDirsRecursively(basePath, otherPathStrings):
    dirList = []
    for pathString in otherPathStrings:
        print("String: ", str( basePath/pathString ) + '/**/')
        dirList += glob.glob( str( basePath/pathString ) + '/**/', recursive=True)
    return set(dirList)


# Returns true if the tag is found, else raises a KeyError.
# Optional parentTag is the tag of the object that should contain the missing tag.
# if possible and applicable it should be included for the sake of error message clarity.
# "why" is an optional explanation of why the tag should be added
def _hasTag(pJSON, tag, parentTag = "", why=""):
    if tag in pJSON:
        return true
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
        p = Path(rootDir)
        parsedJSON = None

        if type(p) is str:
            parsedJSON = json.load(io.open(str((p/jsonFileName).resolve())))
        else:
            raise TypeError("Passed a non-string value into the Data(str) constructor")

        keys = parsedJSON.keys()

        # Check for min_cmake_version
        if _hasTag(parsedJSON, "min_cmake_version"):
            self.cmake_tag_version = parsedJSON["min_cmake_version"]

        # Check for project_name
        if _hasTag(parsedJSON, "project_name"):
            self.project_name = parsedJSON["project_name"]

        # Check for default_cpp_standard
        if "default_cpp_standard" in parsedJSON:
            self.default_cpp_standard = parsedJSON["default_cpp_standard"]
        else:
            self.default_cpp_standard = ""

        # Check for default_c_standard
        if "default_c_standard" in parsedJSON:
            self.default_c_standard = parsedJSON["default_c_standard"]
        else:
            self.default_c_standard = ""

        # Check for allowed_cpp_standards
        if _hasTag(parsedJSON, "allowed_cpp_standards"):
            self.allowed_cpp_standards = parsedJSON["allowed_cpp_standards"]

        if _hasTag(parsedJSON, "targets", why="Are you building a release binary? Or maybe a debug one? Add the 'targets' tag and add a build type to it."):
            self.targets = {}

            targetTags = parsedJSON["targets"].tags()

            for targetTag in targetTags:
                # Initialize the target
                self.targets[targetTag] = {}

                # Check target cpp_flags
                if _hasTag(parsedJSON["targets"][targetTag], "cpp_flags", parentTag="targetTag", why="C++ compiler flags must be defined (as an array). If for some reason you aren't using any compiler flags, still define this tag as an empty array."):
                    self.targets[targetTag]["cpp_flags"] = parsedJSON["targets"][targetTag]["cpp_flags"]

                # Check target c_flags
                if _hasTag(parserJSON["targets"][targetTag], "c_flags", parentTag="targetTag", why="C compiler flags must be defined (as an array). If for some reason you aren't using any compiler flags, still define this tag as an emtpy string."):
                    self.targets[targetTag]["c_flags"] = parsedJSON["targets"][targetTag]["c_flags"]

            # TODO: Add support for more compilers. (Here, might need to manipulate the
            # given flags or require different flag lists altogether if the flags are
            # different across (for) other compilers

        # Check for output
        if _hasTag(parsedJSON, "output"):
            # output = empty dict, for use later. (Makes changing values easier)
            self.output = {}

            # Since output exists, we can now iterate through its items
            outputItemKeys = parsedJSON["output"].keys()

            # Make sure there are actually items in output, otherwise nothing will
            # be compiled and output
            if len(outputItemKeys) < 1:
                # Use the _hasTag function to throw an error since no tags were found (for consistency and mesaage clarity)
                _hasTag(parsedJSON["output"], "any tag name", parentTag="output", why="An item must be added to the output tag, otherwise nothing will be compiled and/or built")

            for keyName in outputItemKeys:
                self.output[keyname] = {}
                outputItem = parsedJSON["output"][keyname]

                # Check output item for type
                if _hasTag(outputItem, "type", parentTag=keyname, why="Without a type, we do not know what to compile your code into. Options: \"executable\", \"static_lib\", \"shared_lib\""):
                    self.output[keyname]["type"] = outputItem["type"]

                # Define the source_files array for this output item
                self.output[keyname]["source_files"] = []

                # Check for base_file (this tag is optional)
                if "base_file" in outputItem:
                    self.output[keyname]["source_files"].append(outputItem["base_file"])

                # Check for r_source_dirs
                if _hasTag(outputItem, "r_source_dirs", parentTag=keyname, why="These are the base directories to be recursively searched for source files. If you are only compiling the (optional) base file, still include this tag with an empty array."):
                    self.output[keyname]["source_files"] += getFilesRecursively(p, outputItem["r_source_dirs"], allSourceTypes)

                # Check for r_include_dirs
                if _hasTag(outputItem, "r_include_dirs", parentTag=keyname, why="Without include directories and header files, the header files will not be compiler not included"):
                    self.output[keyname]["source_files"] += getFilesRecursively(p, outputItem["r_include_dirs"], allHeaderTypes)

                    # Initialize the include_directories array in this output item as well
                    self.output[keyname]["include_directories"] = list(getDirsRecursively(p, outputItem["r_include_dirs"]))

                if self.output[keyname]["type"].lower() == "executable":
                    # Only executable_output_dir is required
                    if _hasTag(outputItem, "executable_output_dir", parentTag=tagname, why="Specifies the directory into which the executable will be build. (Don't use a beginning /)"):
                        self.output[keyname]["executable_output_dir"] = outputItem["executable_output_dir"]
                else:
                    # Assumed to be a library, so both archive_output_dir and library_output_dir are required

                    # Check for archive_output_dir
                    if _hasTag(outputItem, "archive_output_dir", parentTag=tagname, why="Specifies the directory into which the library 'archive' files will be built. (Don't use a beginning /)"):
                        self.output[keyname]["archive_output_dir"] = outputItem["archive_output_dir"]

                    # Check for library_output_dir
                    if _hasTag(outputItem, "library_output_dir", parentTag=tagname, why="Specifies the directory into which the library files will be built. (Don't use a beginning /)"):
                        self.output[keyname]["library_output_dir"] = outputItem["library_output_dir"]

                # TODO: Add support for linking libraries into these output libraries/executables
                # using the tags "link_shared_libs", "link_static_libs".
                # both compiled and IMPORTed libraries should be supported


