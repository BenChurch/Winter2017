cmake_minimum_required(VERSION 2.8.9)

project(FuzzyHelicopterPilot)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/FuzzyHelicopterPilot")
set(EXTENSION_CATEGORY "Fuzzy Logic")
set(EXTENSION_CONTRIBUTORS "Ben Church (Queen's University)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/FuzzyHelicopterPilot.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/FuzzyHelicopterPilot/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(HelicopterBuilder)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
