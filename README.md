# Cmake from Json - IN PROGRESS -

## What is it?
In short, this project is a python script which generates a CMakeLists.txt file from a user-written cmake_data.json file. Its goal is to somewhat automate the process of writing a CmakeLists file, and make visualizing what goes on in the file easier. Currently a work in progress, but functioning with limited functionality.

## Currently Supported Functionality

### Output Types
Output items are all defined in the single `"output"` attribute object.
**Example:**
``` json
"output": {
  "static_output_1": { ... },
  "executable_output_1": { ... },
  "executable_output_2": { ... },
  etc.
}
```

#### Executable
Defines an executable output type. 

##### Avaiable Options
* `type` *(required)*: Specify that this output should be of executable type.
* `base_file` *(semi-optional)*: Explicitly specifies the main file of the executable. If base_file is not specified, then the main file *must exist* in one of the directories (resolved recursively) specified in *r_source_dirs*.
* `executable_output_dir` *(required)*: Specify the location of this executable output *in the build directory*. Note that the specified directory name will be prefixed with the output target name ('Debug', 'Release', etc.).
* `r_source_dirs` *(required)*: An array of root directories for which source files (.c, .cpp, .cxx, etc.) will be searched. All source files located in the directories (and their subdirectories) specified here will be compiled into the executable.
* `r_header_dirs` *(required)*: An array of root directories for which header files (.h, .hpp, .hxx, etc.) will be searched.  All header files located in the directories (and their subdirectories) specified here will be compiled into the executable.
* `r_include_dirs` *(required)*: An array of root directories (expands to their subdirectories as well) which the compiler will use as 'root' directories for file inclusion. For example, instead of including *include/otherfolder/NoiceFile.hpp*, adding "include" r_include_dirs will allow you to just include "NoiceFile.hpp". Handy feature, but could cause confusion in larger projects. This attribute will likely be replaced by something non-recursive in the future.

**Example:**
``` json
"executable_output_example_name": {
  "type": "executable",
  "base_file": "main.cpp",
  "executable_output_dir": "bin",
  "r_source_dirs": [
    "src"
  ],
  "r_header_dirs": [
    "include/example"
  ],
  "r_include_dirs": [
    "include/example"
  ]
}
```

#### Static Library
Defines a static library output type.

##### Avaiable Options
* `type` *(required)*: Specify that this output should be of static_lib type.
* `archive_output_dir` *(required)*: Specify the location of the archive file output *in the build directory*. Note that the specified directory name will be prefixed with the output target name ('Debug', 'Release', etc.).
* `r_source_dirs` *(required)*: An array of root directories for which source files (.c, .cpp, .cxx, etc.) will be searched. All source files located in the directories (and their subdirectories) specified here will be compiled into the library.
* `r_header_dirs` *(required)*: An array of root directories for which header files (.h, .hpp, .hxx, etc.) will be searched.  All header files located in the directories (and their subdirectories) specified here will be compiled into the library.
* `r_include_dirs` *(required)*: An array of root directories (expands to their subdirectories as well) which the compiler will use as 'root' directories for file inclusion. For example, instead of including *include/otherfolder/NoiceFile.hpp*, adding "include" r_include_dirs will allow you to just include "NoiceFile.hpp". Handy feature, but could cause confusion in larger projects. This attribute will likely be replaced by something non-recursive in the future.

**Example:**
``` json
"static_lib_output_example_name": {
  "type": "static_lib",
  "archive_output_dir": "lib",
  "library_output_dir": "lib",
  "r_source_dirs": [
    "another_folder/src"
  ],
  "r_header_dirs": [
    "another_folder/include"
  ],
  "r_include_dirs": [
    "another_folder/include"
  ]
}
```

#### Shared Library
Defines a shared library output type

##### Avaiable Options
* `type` *(required)*: Specify that this output should be of shared_lib type.
* `archive_output_dir` *(required)*: Specify the location of the archive file output *in the build directory*. Note that the specified directory name will be prefixed with the output target name ('Debug', 'Release', etc.).
* `r_source_dirs` *(required)*: An array of root directories for which source files (.c, .cpp, .cxx, etc.) will be searched. All source files located in the directories (and their subdirectories) specified here will be compiled into the library.
* `r_header_dirs` *(required)*: An array of root directories for which header files (.h, .hpp, .hxx, etc.) will be searched.  All header files located in the directories (and their subdirectories) specified here will be compiled into the library.
* `r_include_dirs` *(required)*: An array of root directories (expands to their subdirectories as well) which the compiler will use as 'root' directories for file inclusion. For example, instead of including *include/otherfolder/NoiceFile.hpp*, adding "include" r_include_dirs will allow you to just include "NoiceFile.hpp". Handy feature, but could cause confusion in larger projects. This attribute will likely be replaced by something non-recursive in the future.

**Example:**
``` json
"shared_lib_output_example_name": {
  "type": "shared_lib",
  "archive_output_dir": "lib",
  "library_output_dir": "lib",
  "r_source_dirs": [
    "yet_another_folder/src"
  ],
  "r_header_dirs": [
    "yet_another_folder/include"
  ],
  "r_include_dirs": [
    "yet_another_folder/include"
  ]
}
```

### Imported (already compiled) libraries
I suppose these would be considered dependencies. Therefore each imported library will need to be compiled separately on different platforms as usual.
* Static imported libraries
* Shared imported libraries

### Linking
Both imported and program-generated libraries can be linked to output executables. Multiple libraries can be linked, and can be a mix of static/shared and imported/program-generated

### Language Standards
Both C and C++ language standards can be defined and limited. Multiple can be specified for selection in the CMake GUI.
