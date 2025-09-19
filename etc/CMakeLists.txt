cmake_minimum_required(VERSION 3.12)
project(MiniTerminalDashboard)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Incluir FTXUI desde subcarpeta
include_directories(${CMAKE_SOURCE_DIR}/ftxui/include)

# Crear ejecutable
add_executable(dashboard dashboard.cpp)

# Enlazar pthread (FTXUI usa solo headers, no librerías externas)
target_link_libraries(dashboard PRIVATE pthread)