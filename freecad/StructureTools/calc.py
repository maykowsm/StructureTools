import FreeCAD, App, FreeCADGui, Part, os, math
from PySide2 import QtWidgets
import subprocess

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

try:
	from Pynite import FEModel3D
except:
	print('Instalando dependencias')
	subprocess.check_call(["pip", "install", "PyniteFEA"])

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

class Calc:
	def __init__(self, obj, elements):
		obj.Proxy = self
		obj.addProperty("App::PropertyLinkList", "ListElements", "Calc", "elementos para a analise").ListElements = elements
		obj.addProperty("App::PropertyInteger", "Precision", "Calc", "Presizão dos gráficos").Precision = 10

		obj.addProperty("App::PropertyStringList", "NameMembers", "Calc", "name of structure members")
		obj.addProperty("App::PropertyVectorList", "Nodes", "Calc", "nós")

		obj.addProperty("App::PropertyStringList", "MomentY", "ResultMoment", "momento em Y local")
		obj.addProperty("App::PropertyStringList", "MomentZ", "ResultMoment", "momento em Z local")
		obj.addProperty("App::PropertyFloatList", "MinMomentY", "ResultMoment", "momento minimo em Y")
		obj.addProperty("App::PropertyFloatList", "MinMomentZ", "ResultMoment", "momento minimo em Z")
		obj.addProperty("App::PropertyFloatList", "MaxMomentY", "ResultMoment", "momento maximo em Y")
		obj.addProperty("App::PropertyFloatList", "MaxMomentZ", "ResultMoment", "momento maximo em Z")

		obj.addProperty("App::PropertyStringList", "AxialForce", "ResultAxial", "força axial")
		
		obj.addProperty("App::PropertyStringList", "Torque", "ResultTorque", "torque no elemento")
		obj.addProperty("App::PropertyFloatList", "MinTorque", "ResultTorque", "torque minimo")
		obj.addProperty("App::PropertyFloatList", "MaxTorque", "ResultTorque", "torque maximo")
		
		obj.addProperty("App::PropertyStringList", "ShearY", "ResultShear", "cortante")
		obj.addProperty("App::PropertyFloatList", "MinShearY", "ResultShear", "cortante minimo")
		obj.addProperty("App::PropertyFloatList", "MaxShearY", "ResultShear", "cortante maximo")
		obj.addProperty("App::PropertyStringList", "ShearZ", "ResultShear", "cortante")
		obj.addProperty("App::PropertyFloatList", "MinShearZ", "ResultShear", "cortante minimo")
		obj.addProperty("App::PropertyFloatList", "MaxShearZ", "ResultShear", "cortante maximo")

		obj.addProperty("App::PropertyStringList", "DeflectionY", "ResultDeflection", "Deslocamento em y")
		obj.addProperty("App::PropertyFloatList", "MinDeflectionY", "ResultDeflection", "Deslocamento minimo em y")
		obj.addProperty("App::PropertyFloatList", "MaxDeflectionY", "ResultDeflection", "Deslocamento máximo em Y")
		obj.addProperty("App::PropertyStringList", "DeflectionZ", "ResultDeflection", "Deslocamento em Z")
		obj.addProperty("App::PropertyFloatList", "MinDeflectionZ", "ResultDeflection", "Deslocamento minimo em Z")
		obj.addProperty("App::PropertyFloatList", "MaxDeflectionZ", "ResultDeflection", "Deslocamento máximo em Z")


	#  Mapeia os nós da estrutura, (inverte o eixo y e z para adequação as coordenadas do sover)
	def mapNodes(self, elements):	
		# Varre todos os elementos de linha e adiciona seus vertices à tabela de nodes
		listNodes = []
		for element in elements:
			for edge in element.Shape.Edges:
				for vertex in edge.Vertexes:
					node = [round(vertex.Point.x, 2), round(vertex.Point.z, 2), round(vertex.Point.y, 2)]
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
					node = [round(vertex.Point.x, 2), round(vertex.Point.z, 2), round(vertex.Point.y, 2)]
					index = listNodes.index(node)
					listIndexVertex.append(index)

				listMembers[element.Name + '_' + str(i)] = {
					'nodes': [str(listIndexVertex[0]), str(listIndexVertex[1])],
					'material': element.MaterialMember.Name,
					'section': element.SectionMember.Name}
		
		return listMembers

	# Cria os nós no modelo do solver
	def setNodes(self, model, nodes_map):
		for i, node in enumerate(nodes_map):
			model.add_node(str(i), node[0], node[1], node[2])
		
		return model

	# Cria os membros no modelo do solver
	def setMembers(self, model, members_map):
		for memberName in list(members_map):
			model.add_member(memberName, members_map[memberName]['nodes'][0] , members_map[memberName]['nodes'][1], members_map[memberName]['material'], members_map[memberName]['section'])

		return model

	# Cria os carregamentos
	def setLoads(self, model, loads):
		pass
		for load in loads:

			match load.GlobalDirection:
				case '+X':
					axis = 'FX'
					direction = 1

				case '-X':
					axis = 'FX'
					direction = -1

				case '+Y':
					axis = 'FZ'
					direction = 1

				case '-Y':
					axis = 'FZ'
					direction = -1

				case '+Z':
					axis = 'FY'
					direction = 1

				case '-Z':
					axis = 'FY'
					direction = -1

			# Valida se o carregamento é distribuido
			if 'Edge' in load.ObjectBase[0][1][0]:
				subname = int(load.ObjectBase[0][1][0].split('Edge')[1]) - 1
				name = load.ObjectBase[0][0].Name + '_' + str(subname)
				model.add_member_dist_load(name, axis, float(load.InitialLoading) * direction, float(load.FinalLoading) * direction)

			# Valida se o carregamento é nodal
			elif 'Vertex' in load.ObjectBase[0][1][0]:
				subname = int(load.ObjectBase[0][1][0].split('Vertex')[1]) - 1
				name = str(subname)
				model.add_node_load(name, axis, float(load.NodalLoading) * direction)
			

					
		return model

	# Cria os suportes
	def setSuports(self, model, suports, nodes_map):
		for suport in suports:
			suportvertex = list(suport.ObjectBase[0][0].Shape.Vertexes[int(suport.ObjectBase[0][1][0].split('Vertex')[1])-1].Point)
			for i, node in enumerate(nodes_map):
				if round(suportvertex[0],2) == round(node[0],2) and round(suportvertex[1],2) == round(node[2],2) and round(suportvertex[2],2) == round(node[1],2):					
					name = str(i)
					model.def_support(name, suport.FixTranslationX, suport.FixTranslationZ, suport.FixTranslationY, suport.FixRotationX, suport.FixRotationZ, suport.FixRotationY)
					break
		
		return model

	def setMaterialAndSections(self, model, lines):
		materiais = []
		sections = []
		for line in lines:
			material = line.MaterialMember
			section = line.SectionMember

			if not material.Name in materiais:
				density = material.Density
				modulusElasticity = material.ModulusElasticity
				poissonRatio = material.PoissonRatio
				G = modulusElasticity / (2 * (1 + poissonRatio))
				model.add_material(material.Name, modulusElasticity, G, poissonRatio, density)
				materiais.append(material.Name)

			if not section.Name in sections:
				ang = line.RotationSection.getValueAs('rad')
				Iy = ((section.MomentInertiaZ + section.MomentInertiaY) / 2 ) - ((section.MomentInertiaZ - section.MomentInertiaY) / 2 )*math.cos(2*ang) + section.ProductInertiaYZ*math.sin(2*ang)
				Iz = ((section.MomentInertiaZ + section.MomentInertiaY) / 2 ) + ((section.MomentInertiaZ - section.MomentInertiaY) / 2 )*math.cos(2*ang) - section.ProductInertiaYZ*math.sin(2*ang)
				J  = section.MomentInertiaPolar
				A  = section.AreaSection.Value

				print([Iy, Iz, J, A])
				model.add_section(section.Name, A, Iy, Iz, J)
				sections.append(section.Name)
		
		return model

	
	def execute(self, obj):
		model = FEModel3D()
		# Filtra os diferentes tipos de elementos
		lines = list(filter(lambda element: 'Line' in element.Name or 'Wire' in element.Name, obj.ListElements))
		loads = list(filter(lambda element: 'Load' in element.Name, obj.ListElements))
		suports = list(filter(lambda element: 'Suport' in element.Name, obj.ListElements))

		nodes_map = self.mapNodes(lines)
		members_map = self.mapMembers(lines, nodes_map)

		model = self.setMaterialAndSections(model, lines)
		model = self.setNodes(model, nodes_map)
		model = self.setMembers(model, members_map)
		model = self.setLoads(model, loads)
		model = self.setSuports(model, suports, nodes_map)

		model.analyze()

		# Gera os resultados
		momentz = []
		momenty = []
		mimMomenty = []
		mimMomentz = []
		maxMomenty = []
		maxMomentz = []
		axial = []
		torque = []
		minTorque = []
		maxTorque = []
		sheary = []
		shearz = []
		minSheary = []
		maxSheary = []
		minShearz = []
		maxShearz = []
		deflectiony = []
		minDeflectiony = []
		maxDeflectiony = []
		deflectionz = []
		minDeflectionz = []
		maxDeflectionz = []

		for name in model.members.keys():			
			momenty.append(','.join( str(value) for value in model.members[name].moment_array('My', obj.Precision)[1]))
			momentz.append(','.join( str(value) for value in model.members[name].moment_array('Mz', obj.Precision)[1]))

			sheary.append(','.join( str(value) for value in model.members[name].shear_array('Fy', obj.Precision)[1]))
			shearz.append(','.join( str(value) for value in model.members[name].shear_array('Fz', obj.Precision)[1]))

			axial.append(','.join( str(value) for value in model.members[name].axial_array(obj.Precision)[1]))
			
			torque.append(','.join( str(value) for value in model.members[name].torque_array(obj.Precision)[1]))

			deflectiony.append(','.join( str(value) for value in model.members[name].deflection_array('dy', obj.Precision)[1]))
			deflectionz.append(','.join( str(value) for value in model.members[name].deflection_array('dz', obj.Precision)[1]))

			mimMomenty.append(model.members[name].min_moment('My'))
			mimMomentz.append(model.members[name].min_moment('Mz'))
			maxMomenty.append(model.members[name].max_moment('My'))
			maxMomentz.append(model.members[name].max_moment('Mz'))

			minSheary.append(model.members[name].min_shear('Fy'))
			minShearz.append(model.members[name].min_shear('Fz'))
			maxSheary.append(model.members[name].max_shear('Fy'))
			maxShearz.append(model.members[name].max_shear('Fz'))

			minTorque.append(model.members[name].min_torque())
			maxTorque.append(model.members[name].max_torque())

			minDeflectiony.append(model.members[name].min_deflection('dy'))
			minDeflectionz.append(model.members[name].min_deflection('dz'))
			maxDeflectiony.append(model.members[name].max_deflection('dy'))
			maxDeflectionz.append(model.members[name].max_deflection('dz'))
			
			

		obj.NameMembers = model.members.keys()
		obj.Nodes = [FreeCAD.Vector(node[0], node[2], node[1]) for node in nodes_map]
		obj.MomentZ = momentz
		obj.MomentY = momenty
		obj.MinMomentY = mimMomenty
		obj.MinMomentZ = mimMomentz
		obj.MaxMomentY = maxMomenty
		obj.MaxMomentZ = maxMomentz
		obj.AxialForce = axial
		obj.Torque = torque
		obj.MinTorque = minTorque
		obj.MaxTorque = maxTorque
		obj.MinShearY = minSheary
		obj.MinShearZ = minShearz
		obj.MaxShearY = maxSheary
		obj.MaxShearZ = maxShearz
		obj.ShearY = sheary
		obj.ShearZ = shearz
		obj.DeflectionY = deflectiony
		obj.DeflectionZ = deflectionz
		obj.MinDeflectionY = minDeflectiony
		obj.MinDeflectionZ = minDeflectionz
		obj.MaxDeflectionY = maxDeflectiony
		obj.MaxDeflectionZ = maxDeflectionz
		
	   


	def onChanged(self,obj,Parameter):
		pass
	

class ViewProviderCalc:
	def __init__(self, obj):
		obj.Proxy = self
	

	def getIcon(self):
		return """
/* XPM */
static char * calc_xpm[] = {
"32 32 282 2",
"  	c None",
". 	c #030C1D",
"+ 	c #05112D",
"@ 	c #051129",
"# 	c #061129",
"$ 	c #071229",
"% 	c #08142C",
"& 	c #0A152E",
"* 	c #0B162E",
"= 	c #0A1426",
"- 	c #0C1527",
"; 	c #0F192E",
"> 	c #101A2E",
", 	c #111B2E",
"' 	c #121C2E",
") 	c #111827",
"! 	c #121826",
"~ 	c #151E2E",
"{ 	c #171E2E",
"] 	c #181E2C",
"^ 	c #171E29",
"/ 	c #181E29",
"( 	c #191F29",
"_ 	c #1D212D",
": 	c #13161D",
"< 	c #030C1C",
"[ 	c #1044AB",
"} 	c #1966FF",
"| 	c #1B67FF",
"1 	c #226CFF",
"2 	c #2870FF",
"3 	c #2F75FF",
"4 	c #3679FF",
"5 	c #3C7EFF",
"6 	c #4382FF",
"7 	c #4A86FF",
"8 	c #508BFF",
"9 	c #578FFF",
"0 	c #5E94FF",
"a 	c #6498FF",
"b 	c #6B9CFF",
"c 	c #72A1FF",
"d 	c #78A5FF",
"e 	c #7FAAFF",
"f 	c #86AEFF",
"g 	c #8CB3FF",
"h 	c #93B7FF",
"i 	c #9ABBFF",
"j 	c #6B80AA",
"k 	c #12161D",
"l 	c #040D1F",
"m 	c #206BFF",
"n 	c #266FFF",
"o 	c #2D73FF",
"p 	c #3478FF",
"q 	c #3A7CFF",
"r 	c #4181FF",
"s 	c #4885FF",
"t 	c #4E89FF",
"u 	c #558EFF",
"v 	c #5C92FF",
"w 	c #6297FF",
"x 	c #699BFF",
"y 	c #70A0FF",
"z 	c #76A4FF",
"A 	c #7DA8FF",
"B 	c #84ADFF",
"C 	c #8AB1FF",
"D 	c #91B6FF",
"E 	c #98BAFF",
"F 	c #13181F",
"G 	c #1964FA",
"H 	c #0F409E",
"I 	c #0C2E72",
"J 	c #0B2C6E",
"K 	c #0D2D6E",
"L 	c #0F2F6E",
"M 	c #12316E",
"N 	c #15336E",
"O 	c #19356E",
"P 	c #1B366D",
"Q 	c #1E386D",
"R 	c #213B6E",
"S 	c #243D6E",
"T 	c #263F6E",
"U 	c #2A406E",
"V 	c #2D426E",
"W 	c #2F446E",
"X 	c #344972",
"Y 	c #4D69A0",
"Z 	c #7FA9FA",
"` 	c #88B0FF",
" .	c #8FB4FF",
"..	c #13161F",
"+.	c #0C2F76",
"@.	c #02060E",
"#.	c #060A0E",
"$.	c #384E77",
"%.	c #80AAFF",
"&.	c #86AFFF",
"*.	c #12161F",
"=.	c #04122C",
"-.	c #141C2C",
";.	c #77A5FF",
">.	c #7EA9FF",
",.	c #10151F",
"'.	c #041128",
").	c #111929",
"!.	c #6E9FFF",
"~.	c #75A3FF",
"{.	c #0F141F",
"].	c #04122B",
"^.	c #111A2C",
"/.	c #6699FF",
"(.	c #6D9DFF",
"_.	c #0E141F",
":.	c #0C2D71",
"<.	c #274073",
"[.	c #5D93FF",
"}.	c #0D131F",
"|.	c #1964FB",
"1.	c #0E3A92",
"2.	c #0A2B6B",
"3.	c #0A2A69",
"4.	c #0A2762",
"5.	c #092459",
"6.	c #0B2559",
"7.	c #0D2759",
"8.	c #0F2859",
"9.	c #112959",
"0.	c #142B59",
"a.	c #172C59",
"b.	c #254585",
"c.	c #4D87FB",
"d.	c #5B92FF",
"e.	c #0C131F",
"f.	c #1D69FF",
"g.	c #246DFF",
"h.	c #2B72FF",
"i.	c #3176FF",
"j.	c #387BFF",
"k.	c #3F7FFF",
"l.	c #4583FF",
"m.	c #4C88FF",
"n.	c #538CFF",
"o.	c #0B121F",
"p.	c #1B68FF",
"q.	c #2970FF",
"r.	c #3D7EFF",
"s.	c #4A87FF",
"t.	c #09101F",
"u.	c #0D327E",
"v.	c #030E25",
"w.	c #1453D0",
"x.	c #276FFF",
"y.	c #2D74FF",
"z.	c #3B7CFF",
"A.	c #05112C",
"B.	c #0D3482",
"C.	c #1E69FF",
"D.	c #256EFF",
"E.	c #3277FF",
"F.	c #397BFF",
"G.	c #080F1F",
"H.	c #1864F9",
"I.	c #165BE3",
"J.	c #030E22",
"K.	c #092457",
"L.	c #1860F1",
"M.	c #175EEB",
"N.	c #1658DD",
"O.	c #175FEE",
"P.	c #1B64F4",
"Q.	c #236CFF",
"R.	c #2971FF",
"S.	c #3075FF",
"T.	c #070F1F",
"U.	c #0B2E74",
"V.	c #040C20",
"W.	c #030C1E",
"X.	c #020916",
"Y.	c #03091A",
"Z.	c #030D21",
"`.	c #030D1F",
" +	c #1451CA",
".+	c #1556D8",
"++	c #020A1A",
"@+	c #030B1E",
"#+	c #216BFF",
"$+	c #2770FF",
"%+	c #060E1F",
"&+	c #092254",
"*+	c #030D1E",
"=+	c #020816",
"-+	c #040B1A",
";+	c #030A18",
">+	c #1249B6",
",+	c #1249B9",
"'+	c #030918",
")+	c #040D22",
"!+	c #040B1E",
"~+	c #020812",
"{+	c #030C1F",
"]+	c #081F4E",
"^+	c #1F6AFF",
"/+	c #050D1F",
"(+	c #1450C8",
"_+	c #124BBB",
":+	c #071D48",
"<+	c #134DC0",
"[+	c #165AE0",
"}+	c #1554D3",
"|+	c #134EC3",
"1+	c #1863F7",
"2+	c #031027",
"3+	c #0B2E72",
"4+	c #020918",
"5+	c #124ABA",
"6+	c #0F3990",
"7+	c #061739",
"8+	c #1557D9",
"9+	c #0F3C93",
"0+	c #04132F",
"a+	c #1454D1",
"b+	c #0C317B",
"c+	c #030D20",
"d+	c #1659DF",
"e+	c #0B2A69",
"f+	c #1554D2",
"g+	c #031026",
"h+	c #0A2C6C",
"i+	c #030A1A",
"j+	c #0C2F75",
"k+	c #051027",
"l+	c #04132E",
"m+	c #1658DC",
"n+	c #071A42",
"o+	c #134DC1",
"p+	c #02060F",
"q+	c #124ABB",
"r+	c #071E49",
"s+	c #0F3E9B",
"t+	c #030E21",
"u+	c #082152",
"v+	c #010712",
"w+	c #1147B0",
"x+	c #1556D6",
"y+	c #1148B5",
"z+	c #0E3A8F",
"A+	c #030B1A",
"B+	c #010813",
"C+	c #020C1C",
"D+	c #1555D5",
"E+	c #040D20",
"F+	c #020B1B",
"G+	c #041431",
"H+	c #061637",
"I+	c #1861F3",
"J+	c #030F24",
"K+	c #1144AA",
"L+	c #040C1E",
"M+	c #06183D",
"N+	c #134FC5",
"O+	c #1041A1",
"P+	c #144FC6",
"Q+	c #0E3685",
"R+	c #1862F4",
"S+	c #1860F0",
"T+	c #124CBC",
"U+	c #1861F2",
"V+	c #092255",
"W+	c #1966FE",
"X+	c #1044AA",
"Y+	c #030B1D",
"Z+	c #031029",
"`+	c #04122D",
" @	c #04122E",
".@	c #040F28",
"+@	c #030E24",
"@@	c #030F26",
"#@	c #03112A",
"$@	c #031028",
"        . + @ # $ % & * = - ; > , ' ) ! ~ { ] ^ / ( _ :         ",
"      < [ } } | 1 2 3 4 5 6 7 8 9 0 a b c d e f g h i j k       ",
"      l } } } } } m n o p q r s t u v w x y z A B C D E F       ",
"      l } } G H I J K L M N O P Q R S T U V W X Y Z `  ...      ",
"      l } } +.@.                                #.$.%.&.*.      ",
"      l } } =.                                    -.;.>.,.      ",
"      l } } '.                                    ).!.~.{.      ",
"      l } } ].                                    ^./.(._.      ",
"      l } } :.                                    <.[.a }.      ",
"      l } } |.1.2.3.3.3.3.4.5.5.5.5.6.7.8.9.0.a.b.c.u d.e.      ",
"      l } } } } } } } } } } } } } } } f.g.h.i.j.k.l.m.n.o.      ",
"      l } } } } } } } } } } } } } } } } p.1 q.3 4 r.6 s.t.      ",
"      l } } } } } u.v.w.} } } } } } } } } } m x.y.p z.r t.      ",
"      l } } } } } A.  B.} } } } } } } } } } } C.D.h.E.F.G.      ",
"      l } } } H.I.J.  K.L.} } } } } M.N.N.N.I.O.P.Q.R.S.T.      ",
"      l } } U.V.W.X.  Y.Z.`. +} } .+++W.W.W.W.W.@+J #+$+%+      ",
"      l } } &+*+=+      -+;+>+} } ,+'+)+!+~+~+~+{+]+} ^+/+      ",
"      l } } H.(+_+{+  :+<+[+} } } } }+_+_+_+_+_+|+1+} } l       ",
"      l } } } } } 2+  3+} } } } } } } } } } } } } } } } l       ",
"      l } } } } } 5.4+5+} } } } } } } } } } } } } } } } l       ",
"      l } } } } } } 1+} } } } } } } } } } } } } } } } } l       ",
"      l } } } } } } } } } } } } } } } } } } } } } } } } l       ",
"      l } } } 6+7+8+} 9+0+a+} } } } b+c+6+} d+e+f+} } } l       ",
"      l } } } g+  . h+i+  j+} } } } k+  l+m+J.  n+} } } l       ",
"      l } } } o+i+  p+  '.M.} } } } q+r+s+t+  ++o+} } } l       ",
"      l } } } } u+    v+w+} } } } } } x+J.  ++y+} } } } l       ",
"      l } } } z+A+  B+  C+D+} } } } }+E+  F+1.G+H+I+} } l       ",
"      l } } } J+  G+K+L+  B.} } } } M+  L+N+O+  @+ +} } l       ",
"      l } } } P+Q+R+} N.B.S+} } } } T+n+f+} U+V+e+W+} } l       ",
"      l } } } } } } } } } } } } } } } } } } } } } } } } l       ",
"      . [ } } } } } } } } } } } } } } } } } } } } } } X+.       ",
"        Y++ Z+Z+Z+`+ @ @.@+@ @ @ @ @v.@@ @ @ @#@Z+Z+$@.         "};
		"""


class CommandCalc():

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/calc.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+C", # a default shortcut (optional)
                "MenuText": "Calc estructure",
                "ToolTip" : "Calcula a estrutura"}
    
    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("Part::FeaturePython", "Calc")

        objSuport = Calc(obj, selection)
        ViewProviderCalc(obj.ViewObject)           

        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("calc", CommandCalc())
