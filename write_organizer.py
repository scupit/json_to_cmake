from json.decoder import JSONDecodeError
from data import Data
from file_write import CMakeBuilder

# TODO: Add support for writing these files recursively based on the output items.
# Currently only a single CMakeLists.txt file is written in the root directory. This
# could work, but will make reading it very difficult. The current solution will
# most likely not be viable if new library dirs are added

def writeCMakeFiles(rootDir):

    try:
        try:
            dataObj = Data(rootDir)
        except FileNotFoundError as e:
            print("In initialization of Data object: ")
            raise e
        except JSONDecodeError as e:
            print("Invalid JSON provided in initialization of Data object...")
            raise e
        writer = CMakeBuilder(rootDir + "/CMakeLists.txt")

        writer.writeVersion(dataObj.cmake_tag_version)
        writer.writeProjectName(dataObj.project_name)

        outputKeys = dataObj.output.keys()

        for outputNameKey in outputKeys:
            if dataObj.output[outputNameKey]["type"] == "executable":
                writer.writeExecutableOutput(outputNameKey, dataObj.output[outputNameKey]["source_files"], dataObj.output[outputNameKey]["include_directories"], dataObj.output[outputNameKey]["executable_output_dir"])
            elif dataObj.output[outputNameKey]["type"] == "static_lib":
                writer.writeLibraryOutput(outputNameKey, True, dataObj.output[outputNameKey]["source_files"], dataObj.output[outputNameKey]["include_directories"], dataObj.output[outputNameKey]["archive_output_dir"], dataObj.output[outputNameKey]["library_output_dir"])
            else:
                # Can assume the output type is "shared_lib" at this point
                writer.writeLibraryOutput(outputNameKey, False, dataObj.output[outputNameKey]["source_files"], dataObj.output[outputNameKey]["include_directories"], dataObj.output[outputNameKey]["archive_output_dir"], dataObj.output[outputNameKey]["library_output_dir"])

        linkLibsKeys = dataObj.link_libs.keys()
        for outputName in linkLibsKeys:
            # This if statement might be unnecessary, since if no elements are
            # contained, shouldn't the number of keys be 0?
            if not len(dataObj.link_libs[outputName]) == 0:
                writer.writeLinkedLibs(outputName, dataObj.link_libs[outputName])

        writer.writeCppStandards(dataObj.allowed_cpp_standards, dataObj.default_cpp_standard)
        writer.writeCStandards(dataObj.allowed_c_standards, dataObj.default_c_standard)

        targetKeys = dataObj.targets.keys()

        if dataObj.default_target != "":
            writer.writeDefaultBuildTarget(dataObj.default_target)
        else:
            writer.writeDefaultBuildTarget(targetKeys[0])

        writer.writeBuildTargetList(targetKeys)

        for buildTargetName in targetKeys:
            writer.writeBuildTarget(buildTargetName, dataObj.targets[buildTargetName]["c_flags"], dataObj.targets[buildTargetName]["c_flags"])

        # writer.close()
    except KeyError as e:
        print("ERROR: Problem with JSON file. See below:\n")
        print(str(e))
        raise e
    except TypeError as e:
        print("(TYPE) ERROR:", str(e))
        raise e
