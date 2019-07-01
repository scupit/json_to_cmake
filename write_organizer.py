import data
import file_write

# TODO: Add support for writing these files recursively based on the output items.
# Currently only a single CMakeLists.txt file is written in the root directory. This
# could work, but will make reading it very difficult. The current solution will
# most likely not be viable if new library dirs are added

def writeCMakeFiles(rootDir):

    try:
        dataObj = Data(rootDir)
        writer = CMakeBuilder(rootDir + "/CMakeLists.txt")

        writer.writeVersion(dataObj.cmake_tag_version)
        writer.writeProjectName(dataObj.project_name)

        outputKeys = dataObj.output.keys()

        for outputNameKey in outputKeys:
            if dataObj.output[outputNameKey]["type"] == "executable":
                writer.writeExecutableOutput(key, dataObj.output[outputNameKey]["source_files"], dataObj.output[outputNameKey]["include_directories"], dataObj.output[outputNameKey]["executable_output_dir"])
            elif dataObj.output[outputNameKey]["type"] == "static_lib":
                writer.writeLibraryOutput(key, True, dataObj.output[outputNameKey]["source_files"], dataObj.output[outputNameKey]["include_directories"], dataObj.output[outputNameKey]["archive_output_dir"], dataObj.output[outputNameKey]["library_output_dir"])
            else:
                # Can assume the output type is "shared_lib" at this point
                writer.writeLibraryOutput(key, False, dataObj.output[outputNameKey]["source_files"], dataObj.output[outputNameKey]["include_directories"], dataObj.output[outputNameKey]["archive_output_dir"], dataObj.output[outputNameKey]["library_output_dir"])

        writer.writeCppStandards(dataObj.allowed_cpp_standards, dataObj.default_cpp_standard)
        writer.writeCStandards(dataObj.allowed_c_standards, dataObj.default_c_standard)

        targetKeys = dataObj.targets.keys()

        for buildTargetName in targetKeys:
            writer.writeBuildTarget(buildTargetName, dataObj.targets[buildTargetName]["c_flags"], dataObj.targets[buildTargetName]["c_flags"])

        writer.close()
    except KeyError as e:
        print("ERROR: Problem with JSON file. See below:\n")
        print(str(e))
    except TypeError as e:
        print("ERROR:", str(e))
