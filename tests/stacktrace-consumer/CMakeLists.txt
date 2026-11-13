cmake_minimum_required(VERSION 3.25)
project(stacktrace_consumer LANGUAGES CXX)
find_package(Boost CONFIG REQUIRED COMPONENTS stacktrace_basic)
add_executable(stacktrace_consumer main.cpp)
target_compile_features(stacktrace_consumer PRIVATE cxx_std_23)
target_compile_definitions(stacktrace_consumer PRIVATE BOOST_STACKTRACE_LINK)
# The dump library must arrive transitively through this component alone.
target_link_libraries(stacktrace_consumer PRIVATE Boost::stacktrace_basic)
