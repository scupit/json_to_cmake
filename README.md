# Cmake from Json - IN PROGRESS -

## What is it?
In short, this project is a python script which generates a CMakeLists.txt file from a user-written cmake_data.json file. Its goal is to somewhat automate the process of writing a CmakeLists file, and make visualizing what goes on in the file easier. Currently a work in progress, but functioning with limited functionality.

## Why did I make this?
I want to use Cmake for my projects, but I seriously want to avoid having to write CMakeLists.txt files by hand. Especially since I enjoy making a bunch of little C and C++ projects for practice, continuously writing CMakeLists files seemed like too much of a pain. I wanted a more intuitive (for me) system which would make it easier to visualize how a project is being built, while still allowing for semi-complex cross-platform projects. Using minimal writing to specify a complex structure was also a goal.

## Requirements to run
* Python 3

## How to run
Call `main.py path/to/project/directory` from the command line. 
Note that for this to work properly, the project directory must contain a *cmake_data.json* file.

## Currently Supported Functionality

### Output Types
Output items are all defined in the single `"output"` *(required)* attribute object. At least one output item must be defined.

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
Defines an executable output type. Should be defined as an attribute object inside `"output"`.

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
Defines a static library output type. Should be defined as an attribute object inside `"output"`.

##### Available Options
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
Defines a shared library output type. Should be defined as an attribute object inside `"output"`.

##### Available Options
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
I suppose these would be considered dependencies. Therefore each imported library will need to be compiled separately on different platforms as usual. These will be defined in the `"imported_libs"` *(required)* attribute object. This object may be empty.

**Example:**
``` json
"imported_libs": {
  "imported_lib_1": { ... },
  "imported_lib_2": { ... }
}
```

I like to think of libraries (or groups of library files) as 'packages'. Therefore imported libraries are defined in a package-like format, where the object name (per imported library 'package' as defined in *imported_libs*) represents the package name, and the associated *lib_files* represent the library files defined by each package. This makes specifying linking in cmake_date.json much more intuitive and easily changeable, as only the package name needs to be used. More on that later.

#### Static imported libraries
Imported 'library' of static type. Should be defined as an attribute of `"imported_libs"`.

##### Available Options
* `type`*(required)*: String used to defined this imported library as static type.
* `root_dir` *(required)*: Root file path for the `"lib_files"` attribute. This is the directory which contains all static library files associated with this 'package'. Only one root_dir can be specified.
* `lib_files` *(required)*: An array of file names to use from the root_dir directory. Multiple can be specified, but make sure they are all static library files. **Do not** include the 'lib' prefix or file extensions. This will be done automatically, and will make cross-platform inclusion simpler.
* `r_header_dirs` *(required)*: An array of root directories for which header files (.h, .hpp, .hxx, etc.) will be searched. All header files located in the directories (and their subdirectories) specified here will be included in the sources of any output items that include this package.
* `r_include_dirs` *(required)*: An array of root directories (expands to their subdirectories as well) which the compiler will use as 'root' directories for file inclusion. For example, instead of including *include/otherfolder/NoiceFile.hpp*, adding "include" r_include_dirs will allow you to just include "NoiceFile.hpp". Handy feature, but could cause confusion in larger projects. This attribute will likely be replaced by something non-recursive in the future.

**Example:**
``` json
"user_defined_static_package_name": {
  "type": "static",
  "root_dir": "dep/lib_example/lib",
  "lib_files": [
    "myStaticLibraryFileName1",
    "myStaticLibraryFileName2"
  ],
  "r_header_dirs": [
    "dep/lib_example/include"
  ],
  "r_include_dirs": [
    "dep/lib_example/include"
  ]
}
```

#### Shared imported libraries
Imported 'library' of shared type. Should be defined as an attribute of `"imported_libs"`.


##### Available Options
* `type`*(required)*: String used to defined this imported library as shared type.
* `root_dir` *(required)*: Root file path for the `"lib_files"` attribute. This is the directory which contains all shared library files associated with this 'package'. Only one root_dir can be specified.
* `lib_files` *(required)*: An array of file names to use from the root_dir directory. Multiple can be specified, but make sure they are all shared library files. **Do not** include the 'lib' prefix or file extensions. This will be done automatically, and will make cross-platform inclusion simpler.
* `r_header_dirs` *(required)*: An array of root directories for which header files (.h, .hpp, .hxx, etc.) will be searched. All header files located in the directories (and their subdirectories) specified here will be included in the sources of any output items that include this package.
* `r_include_dirs` *(required)*: An array of root directories (expands to their subdirectories as well) which the compiler will use as 'root' directories for file inclusion. For example, instead of including *include/otherfolder/NoiceFile.hpp*, adding "include" r_include_dirs will allow you to just include "NoiceFile.hpp". Handy feature, but could cause confusion in larger projects. This attribute will likely be replaced by something non-recursive in the future.

**Example:**
``` json
"user_defined_shared_package_name": {
  "type": "shared",
  "root_dir": "dep/lib_example/lib",
  "lib_files": [
    "mySharedLibraryFileName1",
    "mySharedLibraryFileName2"
  ],
  "r_header_dirs": [
    "dep/lib_example/include"
  ],
  "r_include_dirs": [
    "dep/lib_example/include"
  ]
}
```

### Linking
Both imported and program-generated libraries can be linked to output executables. Multiple libraries can be linked, and can be a mix of static/shared and imported/program-generated. Linking structure should be defined in the `"link_libs"` *(required)* attribute object. Output libraries should not link to themselves, as usual.

**Example:**
``` json
"link_libs": {
  "executable_output_1": [
    "user_defined_shared_package_name"
  ],
  "static_output_2": [
    "user_defined_shared_package_name",
    "user_defined_static_package_name"
  ]
}
```

#### The Linking Structure
Each attrubute defined in `link_libs` should have a name that exactly matches the name given to an output item defined in `output`. The attribute should be an array of 'package' names. Each name should exactly match either a library output item defined in *output*, or an imported 'package' defined in *imported_libs*.

#### Linking behind the scenes
When a library package is linked to an output item, all header files resolved from the library's *r_header_dirs* are added to the output item's source files in CMakeLists.txt. Then if the library is an imported lib, each lib_file is added to the output's list of libraries to link. Otherwise the output library target is added to the output item's list of libraries to link.

### Language Standards
Both C and C++ language standards can be defined and limited. Multiple can be specified for selection in the CMake GUI. Note that currently only main versions are supported (such as C++ 11, 14, 17, etc. and C 90, 99, 11, etc.)

#### Specifying C standards
Allowed C standards are specified in the `"allowed_c_standards"` *(required)* attribute array. Each array item should be a string representing the C version.

Each item in the *allowed_c_standards* array will be stored in CMake cache, and can be selected using a dropdown in the CMake GUI.

**Example:**
``` json
"allowed_c_standards": [
  "99",
  "11"
]
```

A default standard can also be specified in `"default_c_standard"` *(optional)*, however this is not required.

**Example:**
``` json
"default_c_standard": "99"
```

#### Specifying C++ standards
Allowed C++ standards are specified in the `"allowed_cpp_standards"` *(required)* attribute array. Each array item should be a string representing the C++ version.

Each item in the *allowed_c_standards* array will be stored in CMake cache, and can be selected using a dropdown in the CMake GUI.

**Example:**
``` json
"allowed_cpp_standards": [
  "11",
  "14",
  "17
]
```

A default standard can also be specified in `"default_cpp_standard"` *(optional)*, however this is not required.

**Example:**
``` json
"default_cpp_standard": "11"
```

### CMake version
You must define the minimum required CMake version. The version should be at least CMake 3.x. This attribute is required, however it is not too important unless you are going to customize the generated file yourself using new CMake features. 

Cmake version should be defined in the `"min_cmake_version"` attribute like so:
**Example:**
``` json
"min_cmake_version": "3.12"
```

### Project Name
The name of the CMake project. Should be defined in the `"project_name"` attribute.

**Example:**
``` json
"project_name": "MySuperAwesomeProject"
```

### Output Targets
Multiple output targets (such as *Debug* and *Release*) can be specified. These targets will be defined in the `"targets"` *(required)* attribute object. Language-specific compiler flags can also be defined. Compiler-specific flags for each target is a planned feature.

**Example:**
``` json
"targets": {
  "debug": { ... },
  "release": { ... },
  "some_other_configuration": { ... }
}
```

#### Specifying a possible output target
Each output target will be defined inside the `targets` object. Its attribute name represens its selectable name in the CMake GUI dropdown.

##### Available Options
* `c_flags` *(required)*: An array of flags to be passed to the C compiler. All flags will be passed to all compilers, and the dash is mandatory. (Compiler specific flags are a planned feature)
* `cpp_flags` *(required)*: An array of flags to be passed to the C++ compiler. All flags will be passed to all compilers, and the dash is mandatory. (Compiler specific flags are a planned feature)

**Example:**
``` json
"output_target_name": {
  "c_flags": [
    "-O2",
    "-DNDEBUG"
  ],
  "cpp_flags": [
    "-O3",
    "-DNDEBUG"
  ]
}
```

A default output target can also be specified using `"default_target"` *(optional)*. While this is not required, it is recommended since it allows the CMake GUI to load and cache the default compiler flag lists on initial config. This should be specified in the root object.

**Example:**
``` json
"default_target": "debug"
```

## Planned features
- [ ] Compiler-specific flags per target
- [ ] Platform-specific imports!!
- [ ] Specification of single include folders

## Finished planned features
:(

## Other Plans
* Refactoring!! I Really need to make this code more organized now that I know what needs to happen.