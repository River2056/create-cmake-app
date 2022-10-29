import os
import sys
import argparse
import textwrap
import subprocess

from pathlib import Path


def write_to_output(path, content):
    with open(path, "wt", encoding="utf-8") as output:
        output.write(textwrap.dedent(content))


def create_nested_file(path, content):
    path.touch()
    print(f"{str(path)} created")
    write_to_output(path, content)
    print(f"Done creating {path}")


def test():
    pass


def main():
    parser = argparse.ArgumentParser(
        description="cmake template cli tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            navigate to destination and run:
            python main.py -n <your-project-name> (REQUIRED)

            script will generate project directory and necessary nested template files
                               """
        ),
    )
    parser.add_argument("-n", "--name", help="project name")

    args = parser.parse_args()

    if not args.name:
        print("Please provide project directory name!")
        sys.exit(1)

    project_name = args.name
    cwd = Path(os.getcwd())
    # create project directory
    print(f"creating project directory: {project_name}...")
    os.mkdir(cwd.joinpath(project_name))

    project_dir_path = Path(cwd.joinpath(project_name))
    cmake_dir_path = Path(project_dir_path.joinpath("cmake"))
    app_dir_path = Path(project_dir_path.joinpath("app"))
    src_dir_path = Path(project_dir_path.joinpath("src"))
    external_dir_path = Path(project_dir_path.joinpath("external"))

    # creating directories
    cmake_dir_path.mkdir()
    print(f"{str(cmake_dir_path)} created")
    app_dir_path.mkdir()
    print(f"{str(app_dir_path)} created")
    src_dir_path.mkdir()
    print(f"{str(src_dir_path)} created")
    external_dir_path.mkdir()
    print(f"{str(external_dir_path)} created")

    # root Makefile
    create_nested_file(
        Path(project_dir_path.joinpath("Makefile")),
        """
            exe_name := task

            all: run

            clean:
            \trm -rf ./build
            \tmkdir build

            build: clean
            \tcmake -S . -B ./build
            \tcmake --build ./build

            run: build
            \t./build/app/Debug/$(exe_name).exe

            pre_generate: clean
            \tcmake -S . -B ./build -GNinja
            \tcmake --build ./build
            \tmv ./build/compile_commands.json .
            
            generate: pre_generate
            \trm -rf ./build
            \tmkdir build
        """,
    )

    # root CMakeLists.txt
    create_nested_file(
        Path(project_dir_path).joinpath("CMakeLists.txt"),
        """
            cmake_minimum_required(VERSION 3.16)

            project(task)

            set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
            set(CMAKE_CXX_STANDARD 17)
            set(CMAKE_CXX_STANDARD_REQUIRED ON)
            set(CMAKE_CXX_EXTENSIONS OFF) 

            set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake/")
            include(AddGitSubmodule)

            add_subdirectory(src)
            add_subdirectory(app)
        """,
    )

    # AddGitSubmodule.cmake
    create_nested_file(
        Path(cmake_dir_path).joinpath("AddGitSubmodule.cmake"),
        """
            function(add_git_submodule dir)
            \tfind_package(Git REQUIRED)

            \tif (NOT EXISTS ${dir}/CMakeLists.txt)
            \t\texecute_process(COMMAND ${GIT_EXECUTABLE}
            \t\t\tsubmodule update --init --recursive -- ${dir}
            \t\t\tWORKING_DIRECTORY ${PROJECT_SOURCE_DIR})
            \tendif()

            \tadd_subdirectory(${dir})
            endfunction() 
        """,
    )

    # app/main.cpp
    create_nested_file(
        Path(app_dir_path).joinpath("main.cpp"),
        """
            #include <iostream>

            int main() {
                std::cout << "hello from cmake template cli!" << '\\n';
                return 0;
            }
        """,
    )

    # app/CMakeLists.txt
    create_nested_file(
        Path(app_dir_path).joinpath("CMakeLists.txt"),
        """
            set(EXECUTABLE_SOURCES 
                "main.cpp")

            add_executable(${PROJECT_NAME} ${EXECUTABLE_SOURCES})
        """,
    )

    # src/CMakeLists.txt
    # empty CMakeLists.txt, add custom later
    Path(src_dir_path).joinpath("CMakeLists.txt").touch()
    print("Done creating src/CMakeLists.txt")

    # .gitignore
    create_nested_file(
        Path(project_dir_path).joinpath(".gitignore"),
        """
            .ccls-cache/
            external/
            build/
            compile_commands.json
        """,
    )

    # git init
    os.chdir(project_dir_path)
    result = subprocess.run(["git", "init"], stdout=subprocess.PIPE)
    print(result)

    print("Done generating cmake template project!")


if __name__ == "__main__":
    main()
