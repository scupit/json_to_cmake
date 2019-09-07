# CMake variable suffixes
INCLUDE_DIRS_SUFFIX = "_INCLUDE_DIRS"
HEADER_FILES_SUFFIX = "_HEADER_FILES"

# CMake operation system specifiers
WINDOWS_OS_NAME = "WIN32"
MAC_OS_NAME = "APPLE"
LINUX_OS_NAME = "UNIX AND NOT APPLE"
UNIX_OS_NAME = "UNIX"

# cmake_data.json tag strings
# --------------------------------------------------

# CMake Project info tags
CMAKE_MIN_VERSION_TAGNAME = "min_cmake_version"
PROJECT_NAME_TAGNAME = "project_name"

# Output item info tags
OUTPUT_TAGNAME = "output"
TYPE_TAGNAME = "type"
SOURCE_FILES_TAGNAME = "source_files"
BASE_FILE_TAGNAME = "base_file"

# Recursive directory definition tags
R_HEADER_DIRS_TAGNAME = "r_header_dirs"
R_INCLUDE_DIRS_TAGNAME = "r_include_dirs"
R_SOURCE_DIRS_TAGNAME = "r_source_dirs"

# cmake_data.json individual inclusion tags
IND_HEADER_DIRS_TAGNAME = "header_dirs"
IND_INCLUDE_DIRS_TAGNAME = "include_dirs"
IND_SOURCE_DIRS_TAGNAME = "source_dirs"

# Include directories tag
INCLUDE_DIRECTORIES_TAGNAME = "include_directories"

# Output directory tags
EXE_OUTPUT_DIR_TAGNAME = "executable_output_dir"
ARCHIVE_OUTPUT_DIR_TAGNAME = "archive_output_dir"
LIB_OUTPUT_DIR_TAGNAME = "library_output_dir"

# Imported libraries info tags
IMPORTED_LIBS_TAGNAME = "imported_libs"
ROOT_DIR_TAGNAME = "root_dir"
LIB_FILES_TAGNAME = "lib_files"
HEADER_FILES_TAGNAME = "header_files"

# Linked libraries tag
LINK_LIBS_TAGNAME = "link_libs"

# Language standards tags
ALLOWED_C_STANDARDS_TAGNAME = "allowed_c_standards"
ALLOWED_CPP_STANDARDS_TAGNAME = "allowed_cpp_standards"
DEFAULT_C_STANDARD_TAGNAME = "default_c_standard"
DEFAULT_CPP_STANDARD_TAGNAME = "default_cpp_standard"

# Build targets tags
TARGETS_TAGNAME = "targets"
CPP_FLAGS_TAGNAME = "cpp_flags"
C_FLAGS_TAGNAME = "c_flags"
DEFAULT_TARGET_TAGNAME = "default_target"
# --------------------------------------------------

OUTPUT_TYPES = {
  "EXE": "executable",
  "STATIC_LIB": "static_lib",
  "SHARED_LIB": "shared_lib"
}