# StructureTools

![ ] (https://s3.amazonaws.com/assets.apoia.se/campaigns/65f2042ce6eb334f82dcee15%7C67b62e77030f0b5f94f858a2/user-campaign-about-cover%7Capoiasecapa-20250219_21163104.png)
This is a workbench for FreeCAD that implements a set of tools for modeling and analyzing structural stresses, similar to analysis software such as SAP2000, Cype3D, SkyCiv, EdiLus, among many others.
The goal is to provide engineers and engineering students with a powerful and easy-to-use open source tool. Fully integrated with the existing tools in FreeCAD.
Note: The tools developed are limited to modeling, calculation and analysis of stresses in structural elements. The focus is not on developing tools for dimensioning these elements. The dimensioning will be handled by another workbench that I am developing in parallel to this one.

## Installing

At the moment, the StructureTools workbench can only be installed manually. I am working on getting the workbench into the FreeCAD repository.

To manually install the workbench, follow these steps:

1 – Click on the “Code” button and then on Download ZIP.

2 – Unzip the ZIP file to your computer.

3 – Rename the extracted folder to “StructureTools.”

4 – Copy the renamed folder to the Mod folder inside your FreeCAD default installation folder.

For more details on manual installation, watch the video:
https://www.youtube.com/watch?v=HeYGVXhw31A


## Tools

The StructureTools workbench is still under development and is constantly changing with the addition of new tools, improvements and bug fixes, I will try to keep this list updated whenever possible.

**Define Member** - modeling of bar elements, the graphical modeling of a bar element can be done using the Draft tool through the line tool and later converting it into a member of the structure. With the definition of the member of the structure done, it is possible to assign to this member several parameters such as Section, Material, and whether it is a truss member.

**Support** - modeling of the supports of the structure capable of fixing the individual rotation and translation of the X, Y and Z axes.

**Section** - defines the section of the members of the structure, capable of capturing the geometric parameters of the area of ​​any face.

**Material** - Defines the physical properties of the material of the structural elements.

**Distributed Load **- defines an external linear load distributed on a member of the structure, capable of modeling uniformly distributed loads, triangular and trapezoidal loads, definition in the global axis.

**Nodal Load** – defines an external force acting on a node of the structure, defined on the global axis.

**Calc Structure** – a tool that creates a calculation object with all the results of the efforts of the structural elements, bending moment, shear, axial force, torque and displacements. It is possible to change the units of the results, number of points calculated for each element, automatic calculation of own weight.

**Diagram** – generates the effort diagrams based on the Calc object. With this tool, it is possible to graphically view the diagram of the efforts of the same on the axis of the element itself. The tool has parameters for scale, color, text size, all to facilitate the visualization and interpretation of the results. It is possible to draw the diagram of individual elements or of the entire structure.

You can see more about the tools in these videos:

* StructureTools - Alpha Version - Workbench Tools and Workflow: https://www.youtube.com/watch?v=AicdjiOc61k
* StructureTools - Alpha Version - Calculation of forces of simply supported beams: https://www.youtube.com/watch?v=Ig0SyqJao0Q

## Development
You can follow the development of the project here: https://github.com/users/maykowsm/projects/1/views/1
I'm trying to write proper documentation for the FreeCAD Wiki, if you want to help me, you'll be welcome.

Please consider supporting the project so I can dedicate more time to it: [Patreon] (https://patreon.com/StructureTools), [ApoiaSe] ( https://apoia.se/structuretools )

## Dependencies

['numpy','scipy','prettytable','PyniteFEA']




## Maintainer

Maykow Menezes
eng.maykowmenezes@gmail.com
