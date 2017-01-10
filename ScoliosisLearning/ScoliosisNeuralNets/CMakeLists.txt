cmake_minimum_required(VERSION 2.8.9)

project(ScoliosisNeuralNets)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ScoliosisNeuralNets")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Ben Church")
set(EXTENSION_DESCRIPTION "Tools to use neural networks for scoliosis quantification from ultrasound landmarks")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ScoliosisNeuralNets.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ScoliosisNeuralNets/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CenterAndNormalizeLandmarks)
add_subdirectory(DegradeTransverseProcesses)
add_subdirectory(ExtendSpine)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
