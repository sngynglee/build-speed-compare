import os
import subprocess
import time

# Directory to store the generated C files
output_dir = "generated_files"
os.makedirs(output_dir, exist_ok=True)

# Template for the C files (without main function)
c_file_template = """
#include <stdio.h>
#include <stdlib.h>

#define SIZE 20000

void compute_{0}() {{
    int **arr = (int **)malloc(SIZE * sizeof(int *));
    for (int i = 0; i < SIZE; i++) {{
        arr[i] = (int *)malloc(SIZE * sizeof(int));
    }}

    for (int i = 0; i < SIZE; i++) {{
        for (int j = 0; j < SIZE; j++) {{
            arr[i][j] = i * j;
        }}
    }}

    for (int i = 0; i < SIZE; i++) {{
        free(arr[i]);
    }}
    free(arr);
}}
"""

# Template for the header file
header_file_template = """
#ifndef COMPUTE_FUNCTIONS_H
#define COMPUTE_FUNCTIONS_H

{0}

#endif // COMPUTE_FUNCTIONS_H
"""

# Template for the main C file
main_file_template = """
#include <stdio.h>
#include "compute_functions.h"

int main() {{
    for (int i = 0; i < 3000; i++) {{
        switch(i) {{
            {0}
        }}
    }}
    return 0;
}}
"""

# Generate 3000 C files
for i in range(3000):
    c_file_content = c_file_template.format(i)
    with open(os.path.join(output_dir, f"file_{i}.c"), "w") as f:
        f.write(c_file_content)

# Generate the header file
compute_declarations = "\n".join([f"void compute_{i}();" for i in range(3000)])
header_content = header_file_template.format(compute_declarations)
with open(os.path.join(output_dir, "compute_functions.h"), "w") as f:
    f.write(header_content)

# Generate the main C file
compute_calls = "\n".join([f"case {i}: compute_{i}(); break;" for i in range(3000)])
main_content = main_file_template.format(compute_calls)
with open(os.path.join(output_dir, "main.c"), "w") as f:
    f.write(main_content)

# Generate the meson.build file
c_sources = ",\n".join([f"  'generated_files/{file}'" for file in os.listdir(output_dir) if file.endswith('.c')])

meson_build_template = """
project('test_project', 'c')

# Define the source files
c_sources = files(
{0}
)

# Create the final executable
exe = executable('my_test_executable', c_sources,
  c_args: ['-O2', '-Wall', '-Wextra'],
  cpp_args: ['-O2', '-Wall', '-Wextra']
)

test('basic', exe)
"""

meson_build_content = meson_build_template.format(c_sources)
with open("meson.build", "w") as f:
    f.write(meson_build_content)

# Generate the CMakeLists.txt file
c_sources = "\n".join([f"  generated_files/{file}" for file in os.listdir(output_dir) if file.endswith('.c')])

cmake_template = """
cmake_minimum_required(VERSION 3.10)
project(test_project C)
set(CMAKE_VERBOSE_MAKEFILE OFF)

# Define the source files
set(SOURCE_FILES
{0}
)

# Create the final executable
add_executable(my_test_executable ${{SOURCE_FILES}})
target_compile_options(my_test_executable PRIVATE -O2 -Wall -Wextra)
"""

cmake_content = cmake_template.format(c_sources)
with open("CMakeLists.txt", "w") as f:
    f.write(cmake_content)

# Function to measure build time
def measure_build_time(command, build_dir):
    start_time = time.time()
    subprocess.run(command, shell=True, cwd=build_dir)
    end_time = time.time()
    return end_time - start_time

# Setup and build with Ninja
subprocess.run("meson setup builddir_ninja", shell=True)
ninja_build_time = measure_build_time("ninja", "builddir_ninja")

# Setup and build with Make using CMake
os.makedirs("builddir_make", exist_ok=True)
subprocess.run('cmake -S . -B builddir_make -G "Unix Makefiles" -DCMAKE_C_COMPILER=gcc', shell=True)
make_build_time = measure_build_time("make -s -j8", "builddir_make")

# Print build times
print(f"Ninja build time: {ninja_build_time:.2f} seconds")
print(f"Make build time: {make_build_time:.2f} seconds")