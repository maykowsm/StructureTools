set(Namespace_SRCS
        freecad/StructureTools/init_gui.py
        freecad/StructureTools/__init__.py
        freecad/StructureTools/my_numpy_function.py
        freecad/StructureTools/version.py
        freecad/StructureTools/resources/cool.svg
        freecad/StructureTools/resources/translations/StructureTools_es-ES.qm
        freecad/StructureTools/resources/translations/StructureTools_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/StructureTools" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
