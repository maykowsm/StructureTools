import FreeCAD, FreeCADGui, Part, math, os
from PySide2 import QtWidgets

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
pathFont = os.path.join(os.path.dirname(__file__), "resources/fonts/ARIAL.TTF")
# pathFont = os.path.join(os.path.dirname(__file__), "ARIAL.TTF")

def show_error_message(msg):
	msg_box = QtWidgets.QMessageBox()
	msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Ícone de erro
	msg_box.setWindowTitle("Erro")
	msg_box.setText(msg)
	msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
	msg_box.exec_()

class Diagram:
	def __init__(self, obj, calc):
		obj.Proxy = self
		obj.addProperty("App::PropertyLink", "ObjectBase", "Diagram", "elementos para a analise").ObjectBase = calc
		obj.addProperty("App::PropertyInteger", "FontHeight", "Diagram", "Tamanho da fonte no diagrama").FontHeight = 100
		obj.addProperty("App::PropertyInteger", "Precision", "Diagram", "precisão de casas decimais").Precision = 2

		obj.addProperty("App::PropertyBool", "MomentZ", "DiagramMoment", "Ver diagrama de momento em Z").MomentZ = False
		obj.addProperty("App::PropertyBool", "MomentY", "DiagramMoment", "Ver diagrama de momento em Y").MomentY = False
		obj.addProperty("App::PropertyFloat", "ScaleMoment", "DiagramMoment", "Escala dos diagramas de momento").ScaleMoment = 1


		obj.addProperty("App::PropertyBool", "ShearZ", "DiagramShear", "Ver diagrama de cortante em Z").ShearZ = False
		obj.addProperty("App::PropertyBool", "ShearY", "DiagramShear", "Ver diagrama de cortante em Y").ShearY = False
		obj.addProperty("App::PropertyFloat", "ScaleShear", "DiagramShear", "Escala dos diagramas de cortante").ScaleShear = 1
		
		obj.addProperty("App::PropertyBool", "Torque", "DiagramTorque", "Ver diagrama de torque").Torque = False
		obj.addProperty("App::PropertyFloat", "ScaleTorque", "DiagramTorque", "Escala do diagrama de torque").ScaleTorque = 1

		obj.addProperty("App::PropertyBool", "AxialForce", "DiagramAxial", "Ver diagrama de força normal").AxialForce = False
		obj.addProperty("App::PropertyFloat", "ScaleAxial", "DiagramAxial", "Escala do diagrama de força normal").ScaleAxial = 1
	

	# Gera uma matriz baseado em umdos parâmetros do calc
	def getMatrix(self, param):
		matriz = []
		for linha in param:
			lista = [float(value) for value in linha.split(',')]
			matriz.append(lista)
		
		return matriz


	#  Mapeia os nós da estrutura
	def mapNodes(self, elements):	
		# Varre todos os elementos de linha e adiciona seus vertices à tabela de nodes
		listNodes = []
		for element in elements:
			for edge in element.Shape.Edges:
				for vertex in edge.Vertexes:
					node = [round(vertex.Point.x, 2), round(vertex.Point.y, 2), round(vertex.Point.z, 2)]
					if not node in listNodes:
						listNodes.append(node)

		return listNodes


	# Mapeia os membros da estrutura
	def mapMembers(self, elements, listNodes):
		listMembers = {}
		for element in elements:
			for i, edge in enumerate(element.Shape.Edges):
				listIndexVertex = []
				for vertex in edge.Vertexes:
					node = [round(vertex.Point.x, 2), round(vertex.Point.y, 2), round(vertex.Point.z, 2)]
					index = listNodes.index(node)
					listIndexVertex.append(index)
				# valida se o primeiro nó é mais auto do que o segundo nó, se sim inverte os nós do membro (necessário para manter os diagramas voltados para a posição correta)
				n1 = listIndexVertex[0]
				n2 = listIndexVertex[1]
				if listNodes[n1][2] > listNodes[n2][2]:
					aux = n1
					n1 = n2
					n2 = aux
				listMembers[element.Name + '_' + str(i)] = {
					'nodes': [str(n1), str(n2)],
					'RotationSection': element.RotationSection.getValueAs('rad')
				}
		
		return listMembers
	
	# separa as ordenadas em grupos de valores positivos e negativos
	def separatesOrdinates(self, values):
		loops = []
		loop = [values[0]]
		for i in range(1, len(values)):
			if values[i] * values[i-1] < 0 and abs(values[i]) > 1e-2: #valida  se o valor passa pelo eixo das abssisas comparado com o valor anterior
				loops.append(loop)
				loop = [values[i]]
			else:
				loop.append(values[i])
		
		loops.append(loop)
		
		return loops


	# Função que cria os pares de coordenadas e já cria os valores que cruzam o eixo das absissas
	def generateCoordinates(self, ordinates, dist):
		cont = 0
		loops = []
		loop = []
		for i in range(len(ordinates)):
			for j in range(len(ordinates[i])):
				
				if j == 0 and abs(ordinates[i][j]) > 1e-2 and len(loop) == 0: #Valida se o primeiro valor do loop é maior do que 0
					loop.append([0,0])  

				coordinate = [cont * dist, ordinates[i][j]]
				loop.append(coordinate)
				cont += 1
			
			loops.append(loop)
			loop = []
			if i == len(ordinates) - 1: #valida se foi o ultimo loop a ser processado
				if abs(loops[-1][-1][1]) > 1e-2: #Valida se o valor do ultimo loop é diferente de 0
					loops[-1].append([(cont - 1) * dist,0])
			
			else:
				# calcula o ponto de intersecção com o eixo das abcissas
				o = loops[-1][-1][0]
				a = abs(loops[-1][-1][1])
				b = abs(ordinates[i+1][0])
				x = (a * dist) / (a + b)
				loops[-1].append([o + x, 0]) #Acrecenta o ponto de intersecção no ultimo loop
				loop.append([o + x, 0]) # Acrescenta o ponto de intersecção no inicio do proximo loop
		
		return loops
	

	# Gera as faces
	def generateFaces(self, loops):
		faces = []
		for loop in loops:
			
			loop.append(loop[0])
			loop = [FreeCAD.Vector(value[0], 0, value[1]) for value in loop]

			edges = [Part.LineSegment(loop[i], loop[i+1]).toShape() for i in range(len(loop)-1)]
			wire = Part.Wire(edges)
			face = Part.Face(wire)
			# Valida a face
			if face.Area > 0:
				faces.append(face)
		
		return faces
	
	# Faz a rotação do  diagrama na direção passada como argumento e o posiciona
	def rotate(self, element, dirStart, dirEnd, position = FreeCAD.Vector(0,0,0.1)):
		try:
			dirStart.normalize()
			dirEnd.normalize()

			if dirStart == dirEnd:
				return element.translate(position)       
			
			rotacao = FreeCAD.Rotation(dirStart, dirEnd)
			elementoRotacionado = element.transformGeometry(FreeCAD.Placement(position,rotacao).toMatrix())
			return elementoRotacionado
		except:
			print('Erro ao rotacionar diagrama.')
			return element
	
	# Gero os valores nos diagramas
	def makeText(self, values, listMatrix, dist, fontHeight, precision):
		listWire = []
		for i, value in enumerate(values):
			offset = 0
			valueString = abs(listMatrix[i])
			string = f"{valueString:.{precision}e}"
			x = dist * i
			y = value + offset if value > 0 else value - offset

			text = Part.makeWireString(string, pathFont, fontHeight)
			for wires in text:
				for wire in wires:
					wire = wire.rotated(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 90)
					wire = wire.translate(FreeCAD.Vector(x, 0, y))
					listWire += [wire]
		
		return listWire


	# Gera o diagrama da matriz passada como argumento
	def makeDiagram(self, matrix,nodes, members, orderMembers, nPoints, rotacao, escale, fontHeight, precision):
		
		# e = 1e-11
		listDiagram = []
		for i, nameMember in enumerate(orderMembers):
			p1 = nodes[int(members[nameMember]['nodes'][0])]
			p2 = nodes[int(members[nameMember]['nodes'][1])]
			length = ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)**0.5
			dist = length / (nPoints -1) #Distancia entre os pontos no eixo X
			values = [value * escale for value in matrix[i]]

			ordinates = self.separatesOrdinates(values)
			coordinates = self.generateCoordinates(ordinates, dist)
			faces = self.generateFaces(coordinates)
			texts = self.makeText(values, matrix[i], dist, fontHeight, precision)
			
			# Posiciona o diagrama
			dx = p2[0] - p1[0]
			dy = p2[1] - p1[1]
			dz = p2[2] - p1[2]
			element = Part.makeCompound(faces)
			element = Part.makeCompound([element] + texts)

			print(members[nameMember]['RotationSection'])
			rot = FreeCAD.Rotation(FreeCAD.Vector(1,0,0), rotacao)
			element.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), rot)
			element = self.rotate(element, FreeCAD.Vector(1,0,0), FreeCAD.Vector(abs(dx), abs(dy), abs(dz)))

			if dx < 0 :
				element = element.mirror(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
			
			if dy < 0 :
				element = element.mirror(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0))

			
			element = element.translate(FreeCAD.Vector(p1[0], p1[1], p1[2]))
			
			listDiagram.append(element)
			# Part.show(element)
			# Part.show(Part.makeCompound(faces))
			# for face in faces:
			#     Part.show(Part.makeCompound(faces))
		
		return listDiagram



	def execute(self, obj):
		elements = list(filter(lambda element: 'Line' in element.Name or 'Wire' in element.Name,  obj.ObjectBase.ListElements))
		nodes = self.mapNodes(elements)
		members = self.mapMembers(elements, nodes)
		orderMembers = obj.ObjectBase.NameMembers

		listDiagram = []
		if obj.MomentZ:
			listDiagram += self.makeDiagram(self.getMatrix(obj.ObjectBase.MomentZ),nodes, members, orderMembers, obj.ObjectBase.NumPointsMoment, 0, obj.ScaleMoment, obj.FontHeight, obj.Precision)
		
		if obj.MomentY:
			listDiagram += self.makeDiagram(self.getMatrix(obj.ObjectBase.MomentY),nodes, members, orderMembers, obj.ObjectBase.NumPointsMoment, 90, obj.ScaleMoment, obj.FontHeight, obj.Precision)
		
		if obj.ShearY:
			listDiagram += self.makeDiagram(self.getMatrix(obj.ObjectBase.ShearY),nodes, members, orderMembers, obj.ObjectBase.NumPointsShear, 0, obj.ScaleShear, obj.FontHeight, obj.Precision)

		if obj.ShearZ:
			listDiagram += self.makeDiagram(self.getMatrix(obj.ObjectBase.ShearZ),nodes, members, orderMembers, obj.ObjectBase.NumPointsShear, 90, obj.ScaleShear, obj.FontHeight, obj.Precision)
		
		if obj.Torque:
			listDiagram += self.makeDiagram(self.getMatrix(obj.ObjectBase.Torque),nodes, members, orderMembers, obj.ObjectBase.NumPointsTorque, 0, obj.ScaleTorque, obj.FontHeight, obj.Precision)
		
		if obj.AxialForce:
			listDiagram += self.makeDiagram(self.getMatrix(obj.ObjectBase.AxialForce),nodes, members, orderMembers, obj.ObjectBase.NumPointsAxial, 0, obj.ScaleAxial, obj.FontHeight, obj.Precision)
		
		if not listDiagram:
			shape = Part.Shape()
		else:	
			print(listDiagram)
			shape = Part.makeCompound(listDiagram)

		print(shape)
		obj.Shape = shape

		# Estilização
		obj.ViewObject.LineWidth = 1
		obj.ViewObject.PointSize = 1
		obj.ViewObject.LineColor = (255,0,0)
		obj.ViewObject.PointColor = (255,0,0)
		obj.ViewObject.ShapeAppearance = (FreeCAD.Material(DiffuseColor=(1.00,0.00,0.00),AmbientColor=(0.33,0.33,0.33),SpecularColor=(0.53,0.53,0.53),EmissiveColor=(0.00,0.00,0.00),Shininess=(0.90),Transparency=(0.00),))
		obj.ViewObject.Transparency = 70


	def onChanged(self,obj,Parameter):
		if Parameter == 'edgeLength':
			self.execute(obj)


class ViewProviderDiagram:
	def __init__(self, obj):
		obj.Proxy = self

	def getIcon(self):
		return """/* XPM */
static char * moment_xpm[] = {
"32 32 51 1",
" 	c None",
".	c #0D0000",
"+	c #000000",
"@	c #0E0000",
"#	c #390000",
"$	c #060000",
"%	c #410000",
"&	c #F60000",
"*	c #090000",
"=	c #100000",
"-	c #460000",
";	c #F80000",
">	c #FF0000",
",	c #530000",
"'	c #FB0000",
")	c #5F0000",
"!	c #FD0000",
"~	c #660000",
"{	c #FE0000",
"]	c #720000",
"^	c #7D0000",
"/	c #8C0000",
"(	c #990000",
"_	c #9E0000",
":	c #AB0000",
"<	c #0B0000",
"[	c #B00000",
"}	c #070000",
"|	c #4A0000",
"1	c #880000",
"2	c #040000",
"3	c #4B0000",
"4	c #B50000",
"5	c #0C0000",
"6	c #B10000",
"7	c #A60000",
"8	c #940000",
"9	c #850000",
"0	c #840000",
"a	c #6D0000",
"b	c #0F0000",
"c	c #670000",
"d	c #FC0000",
"e	c #5A0000",
"f	c #110000",
"g	c #FA0000",
"h	c #4D0000",
"i	c #470000",
"j	c #050000",
"k	c #3B0000",
"l	c #010000",
"                                ",
"                              .+",
"                             @#$",
"                            .%&*",
"                           =-;>*",
"                          =,'>>*",
"                         @)!>>>*",
"                        =~{>>>>*",
"                       @]>>>>>>*",
"                      .^>>>>>>>*",
"                     @/>>>>>>>>*",
"                    .(>>>>>>>>>*",
"                   @_>>>>>>>>>>*",
"                  @:>>>>>>>>>>>*",
"                 <[>>>>>>>>>>>>*",
"                }|11111111111112",
"211111111111113}                ",
"$>>>>>>>>>>>>45                 ",
"$>>>>>>>>>>>6.                  ",
"$>>>>>>>>>>7@                   ",
"$>>>>>>>>>(5                    ",
"$>>>>>>>>8@                     ",
"$>>>>>>>9.                      ",
"$>>>>>>0@                       ",
"$>>>>{ab                        ",
"$>>>{cb                         ",
"$>>def                          ",
"$>gh=                           ",
"$;i@                            ",
"jkf                             ",
"l.                              ",
"+                               "};
		"""



class CommandDiagram():

	def GetResources(self):
		return {"Pixmap"  : os.path.join(ICONPATH, "icons/diagram.svg"), # the name of a svg file available in the resources
				"Accel"   : "Shift+D", # a default shortcut (optional)
				"MenuText": "Diagram",
				"ToolTip" : "Gera os diagramas dos esforços"}
	
	def Activated(self):
		objectBase = FreeCADGui.Selection.getSelection()[0]
		if 'Calc' in objectBase.Name:

			doc = FreeCAD.ActiveDocument
			obj = doc.addObject("Part::FeaturePython", "Diagram")
			Diagram(obj, objectBase)
			ViewProviderDiagram(obj.ViewObject) 

		else:
			show_error_message('Deve ser selecionado um objeto calc para traçar o diagrama')
			print('Deve ser selecionado um objeto calc para traçar o diagrama')
	
	def IsActive(self):
		return True


FreeCADGui.addCommand("diagram", CommandDiagram())
