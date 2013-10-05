import sublime, sublime_plugin
import os, re

class GotemplateCommand(sublime_plugin.WindowCommand):
	curProject = None
	curSource = None
	curPath = None

	tree = []

	def run(self):

		self.curProject = None
		self.curSource = None
		self.curPath = None
		del self.tree[:]

		folders = self.window.folders()
		self.tree.append("Please Select Project...")
		for folder in folders:
			self.tree.append(folder)
		self.openQuickPanel(self.tree, self.onSelected, None)

	def onSelected(self, index):
		if index == -1 : return
		if index == 0 :
			self.openQuickPanel(self.tree, self.onSelected, None)
			return
		if self.curProject == None :
			self.curProject = self.tree[index]
		
		self.curSource = self.sourceOfProject(self.curProject, None)
		if self.curSource :
			self.curPath = self.curProject + "/" + self.curSource
			self.sourceIsSet()
		else:
			self.window.show_input_panel("Please set the Source of the [" + self.curProject + "]:", "", self.sourcePathInput, None, None)

	def sourcePathInput(self, path) :
		self.sourceOfProject(self.curProject, path)

	def sourceIsSet(self, path = "") :
		del self.tree[:]
		self.tree.append("Create Class With Package...")
		if path != "" :
			self.curPath = self.curPath + "/" + path
		subs = os.listdir(self.curPath)
		dirs = []
		for p in subs :
			if os.path.isdir(os.path.join(self.curPath, p)) == True:
				dirs.append(p)
		if len(dirs) == 0 :
			self.window.show_input_panel("Type in the class name [" + self.curProject + "]:", "", self.genClass, None, None)
			return
		self.tree.extend(dirs)
		self.openQuickPanel(self.tree, self.onSelectPackage, None)

	def onSelectPackage(self, index) :
		if index == 0 :
			self.window.show_input_panel("Type in the class include Package [" + self.curProject + "]:", "", self.genClass, None, None)
		elif index != -1 :
			self.sourceIsSet(self.tree[index])

	def genClass(self, name):
		path = ""
		n = ""
		pack = ""
		if "#" in name :
			arr = name.split("#")
			path = re.sub("\.", "/", arr[0])
			if os.path.exists(self.curPath + "/" + path) == False :
				os.makedirs(self.curPath + "/" + path)
			packPath = arr[0].split(".")
			packPathLen = len(packPath)
			n = arr[1]
			pack = packPath[packPathLen - 1]
		else :
			arr = self.curPath.split("/")
			arrLen = len(arr)
			pack = arr[arrLen - 1]
			path = ""
			n = name

		print(pack, path, n)
		fileName = self.curPath + "/" + path + "/" + n + ".go"
		if os.path.isfile(fileName) == False :
			f = open(fileName, "w")
			f.write("package " + pack)
			f.write("\n\nimport(\n\t\"\"\n)\n\n")
			f.close()
			self.window.open_file(fileName)
		else :
			sublime.message_dialog(n + ".go" + " is exists!")
			

	def sourceOfProject(self, project, new_source) :
		projectData = self.window.project_data()
		if "folders" in projectData:
			folders = projectData["folders"]
			for folder in folders :
				if folder["path"] == project :
					if "source" in folder :
						return folder["source"]
					else :
						if new_source != None :
							new_source = self.removeAllBlank(new_source)
							if new_source != "" :
								folder["source"] = new_source
								self.curSource = new_source
								self.curPath = self.curProject + "/" + self.curSource
								if os.path.exists(self.curPath) == False :
									os.mkdir(self.curPath)
								self.window.set_project_data(projectData)
						else :
							return None

	def removeAllBlank(self, str) :
		pattern = re.compile("\s+", re.I)
		return re.sub(pattern, '', str)

	def openQuickPanel(self, data, callback, highlighted):
		sublime.set_timeout(lambda: self.window.show_quick_panel(data, callback, sublime.MONOSPACE_FONT, 0, highlighted), 1)