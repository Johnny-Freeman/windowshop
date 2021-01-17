import time, json, os, inspect, random
from datetime import datetime, timedelta

# non standard libs
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# Settings
tasklog_location = None

# Hidden settings
_default_tasklog = "/tasklog.dat"

# =======================================
# Directory Handling
# =======================================
def _create_dir(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)

def get_tasklog_filename():
	frame = inspect.stack()[-1]
	module = inspect.getmodule(frame[0])

	## WIP , need to truncate directory! without filename
	root_file = ""
	if not tasklog_location:
		root_file = os.path.dirname(os.path.abspath(module.__file__)) + _default_tasklog
	else:
		root_file = tasklog_location

	root_dir = os.path.dirname(root_file)
	_create_dir(root_dir)
	
	return root_file
	
def save_tasklog(filename, j_string):
	ofile = open(filename, "w+")
	ofile.write(j_string)
	ofile.close()

def read_tasklog(filename):
	try:
		ofile = open(filename, "r")
	except:
		return None
	
	j_string = ofile.read()
	ofile.close()
	return j_string

# =======================================
# Task Object Handling (Needs to be in it's own file)
# =======================================
class Tasknote():
	def __init__(self):
		self.description = ""
		self.count_procrastination = 0
		self.date_start = ""
		self.priority = 0
		self.epoch_timestamp = 0
	
	def set_description(self, description, priority):
		self.description = description
		self.priority = priority
		self.epoch_timestamp = int(time.time())
		self.date_start = datetime.now().strftime("%Y-%m-%d")
		
	def edit(self, description=None, priority=None):
		if description:
			self.description = description
		if priority:
			self.priority = priority
		
	def procrastinate(self):
		self.count_procrastination +=1
	
	def calc_days(self):
		diff_epoch = int(time.time()) - self.epoch_timestamp
		if diff_epoch < 0:
			return 0
		else:
			return diff_epoch // 86400 #(3600*24)
	
	def _export(self):
		_dict = {
			"description"	: self.description,
			"count_procrastination" : self.count_procrastination,
			"date_start"	: self.date_start,
			"priority"		: self.priority,
			"epoch_timestamp"	: self.epoch_timestamp,
		}
		
		return json.dumps(_dict)
	
	def _import(self, j_string):
		_dict = json.loads(j_string)
		self.description = _dict["description"]
		self.count_procrastination = int(_dict["count_procrastination"])
		self.date_start = _dict["date_start"]
		self.priority = int(_dict["priority"])
		self.epoch_timestamp = int(_dict["epoch_timestamp"])

class Task_Session():
	def __init__(self):
		self.list_tasknotes = []
		
	def add_task(self, description, priority):
		new_task = Tasknote()
		new_task.set_description(description, priority)
		self.list_tasknotes.append(new_task)
		
	def edit_task(self, id, *args, **kwargs):
		self.list_tasknotes[id].edit(*args, **kwargs)
		return self.get_task(id)

	def algo_get_task(self):
		return random.randint(0,len(self.list_tasknotes)-1)

	def get_task(self, id=None):
		if len(self.list_tasknotes) < 1:
			print("Warning: No more tasks! Add a Task!")
			return None
		
		if id == None:
			id = self.algo_get_task()
		
		return {
			"id"	: id,
			"task"	: self.list_tasknotes[id],
		}
	
	def procrastinate_task(self, id):
		self.list_tasknotes[id].procrastinate()
		
	def drop_task(self, id):
		del self.list_tasknotes[id]

	def _export(self):
		str_el_list = []
		for el in self.list_tasknotes:
			str_el_list.append(el._export())
		
		return json.dumps(str_el_list)
	
	def _import(self, j_string):
		if not j_string:
			return # do nothing, start from scratch
		
		str_el_list = json.loads(j_string)
		for el in str_el_list:
			# init tasks
			new_task = Tasknote()
			new_task._import(el)
			self.list_tasknotes.append(new_task)
			
	def length(self):
		return len(self.list_tasknotes)

# =======================================
# Menu Object handling (needs to be in it's own menu_objects.py file)
# =======================================
"""
Every Object in PYQT is a "widget", however they have "parent" owners
 	modal "children" widgets block access to parent widgets until they are closed
 	modeless "children" widgets are non-blocking, and act as if they have no parent
PYQT has two main methods of assigning parents to child widgets
 	Inheritance
 		Parents assigned at *initiation*
 		*self is passed in as part of parent widget's class methods
 		ex1:
 			class QDialog()
 				def __init__(self):
 					layout = QVBoxLayout(self)
 					layout.addWidget(....)
 					..
 					return
 		ex2:
			class QDialog()
 				def __init__(self):
 					buttons = QDialogButtonBox(self)
 					buttons.accepted....
 					..
 					return
 			
 	Composition
		Parents assigned *after* instantiation
		or self.set..., self.add... for within parent
		Easier AND cleaner to implement event driven interfaces as child widgets are treated more as independent instances than dependent class objects
		less common > setModal(*T/F), setWindowModality(*parent) from outside parent # https://doc.qt.io/qtforpython/PySide6/QtWidgets/QDialog.html
		ex1:
			class QDialog()
 				def __init__(self):
 					new_layout = QVBoxLayout() # << note self not included
					new_layout.addWidget(....)
					..
					self.setLayout(new_layout)
					return
		ex2:
			class QDialog()
 				def __init__(self):
 					new_buttons = QDialogButtonBox() # << note self not included
 					new_buttons.accepted....
 					..
					self.addWidget(new_buttons)
 					return
"""

class QT_Custom_Dialog(QDialog):
	# https://stackoverflow.com/questions/18196799/how-can-i-show-a-pyqt-modal-dialog-and-get-data-out-of-its-controls-once-its-clo << inheritance from QDialog method
	# https://www.learnpyqt.com/tutorials/dialogs/
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs) # super(CustomDialog, self).__init__(*args, **kwargs), I prefer just super() due to neatness
		layout = QVBoxLayout(self)
		
		# Text inputs
		# https://doc.qt.io/qtforpython/PySide6/QtWidgets/QDialog.html
		# https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
		self.text_input_1 = QLineEdit()
		self.text_input_1.setText("OYOYOYOYY")
		layout.addWidget(self.text_input_1)
		
		# OK and Cancel buttons
		# "To close the dialog and return the appropriate value, you must connect a default button"
		default_buttons = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
			Qt.Horizontal) #, self) << I don't like *self referencing method to parent, I prefer composition
		default_buttons.accepted.connect(self.accept)
		default_buttons.rejected.connect(self.reject)
		# default_buttons.setDefault(self.accept)
		layout.addWidget(default_buttons)
		
		# Port layout to self
		self.setLayout(layout) # << composition method 
	
	def result(self):
		# this may not be the best method to do this, look into QInputDialog's source code to see how they do it!
		result = super().result()
		if result == True:
			return self.text_input_1.text(), True
		else:
			return None, False
		
	@staticmethod
	def get_input(parent=None):
		# static method to execute Qdialog in-line in main code block
		dialog = QT_Custom_Dialog(parent) #if parent is none, it becomes modeless, as modal blocks parent interaction
		dialog.exec_()
		return dialog.result()
		
class QT_Add_Task_Dialog(QDialog):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.layout = QVBoxLayout(self)
		
		self.lookup = {}
		
		# Text inputs
		# https://doc.qt.io/qtforpython/PySide6/QtWidgets/QDialog.html
		# https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
		self.add_label("lbl_description","Description:")
		
		input_description = QLineEdit()
		input_description.setText("Input Description Here...")
		self.lookup["input_description"] = input_description
		self.layout.addWidget(input_description)
		
		self.add_label("lbl_priority","Priority:")
		
		input_priority = QLineEdit()
		input_priority.setText("#")
		self.lookup["input_priority"] = input_priority
		self.layout.addWidget(input_priority)
		
		# OK and Cancel buttons
		default_buttons = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
			Qt.Horizontal)
		default_buttons.accepted.connect(self.accept)
		default_buttons.rejected.connect(self.reject)
		self.layout.addWidget(default_buttons)
		
		# Port layout to self
		self.setLayout(self.layout)
		
	def add_label(self, name, input_string):
		label = QLabel(input_string)
		
		self.lookup[name] = label
		self.layout.addWidget(label)
		
	def add_button(self, name, btn_text, target_function):
		button = QPushButton(btn_text)
		button.clicked.connect(target_function)
		
		self.lookup[name] = button
		self.layout.addWidget(button)
	
	def result(self):
		# this may not be the best method to do this, look into QInputDialog's source code to see how they do it!
		result = super().result()
		if result == True:
			return self.lookup["input_description"].text(),int(self.lookup["input_priority"].text()), True
		else:
			return None, None, False
		
	@staticmethod
	def get_input(parent=None, *args, **kwargs):
		# static method to execute Qdialog in-line in main code block
		dialog = QT_Add_Task_Dialog(parent, *args, **kwargs) #if parent is none, it becomes modeless, as modal blocks parent interaction
		dialog.exec_()
		return dialog.result()

class QT_Edit_Task_Dialog(QDialog):
	def __init__(self, description, priority, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.layout = QVBoxLayout(self)
		
		self.lookup = {}
		
		# Text inputs
		# https://doc.qt.io/qtforpython/PySide6/QtWidgets/QDialog.html
		# https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
		self.add_label("lbl_description","Description:")
		
		input_description = QLineEdit()
		input_description.setText(description)
		self.lookup["input_description"] = input_description
		self.layout.addWidget(input_description)
		
		self.add_label("lbl_priority","Priority:")
		
		input_priority = QLineEdit()
		input_priority.setText(str(priority))
		self.lookup["input_priority"] = input_priority
		self.layout.addWidget(input_priority)
		
		# OK and Cancel buttons
		default_buttons = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
			Qt.Horizontal)
		default_buttons.accepted.connect(self.accept)
		default_buttons.rejected.connect(self.reject)
		self.layout.addWidget(default_buttons)
		
		# Port layout to self
		self.setLayout(self.layout)
		
	def add_label(self, name, input_string):
		label = QLabel(input_string)
		
		self.lookup[name] = label
		self.layout.addWidget(label)
		
	def add_button(self, name, btn_text, target_function):
		button = QPushButton(btn_text)
		button.clicked.connect(target_function)
		
		self.lookup[name] = button
		self.layout.addWidget(button)
	
	def result(self):
		# this may not be the best method to do this, look into QInputDialog's source code to see how they do it!
		result = super().result()
		if result == True:
			return self.lookup["input_description"].text(),int(self.lookup["input_priority"].text()), True
		else:
			return None, None, False
		
	@staticmethod
	def get_input(parent=None, *args, **kwargs):
		# static method to execute Qdialog in-line in main code block
		dialog = QT_Edit_Task_Dialog(parent, *args, **kwargs) #if parent is none, it becomes modeless, as modal blocks parent interaction
		dialog.exec_()
		return dialog.result()

class QT_IDE():
	# ------------------------------------
	# State Management
	# ------------------------------------
	def __init__(self):
		# https://www.tutorialspoint.com/pyqt/pyqt_major_classes.htm
		
		# init Qappication
		self.app = QApplication([]) # application just sets the environment of windowed application (top lvl)
		
		# Easy find naming system (hash table)
		self.lookup = {}
		
		# Box Layout
		self.layout = QVBoxLayout() # Type of QWidget(*parent)Layout controls display flow/placement (template)
		self.window = QWidget()
		self.window.setLayout(self.layout)	# Sets window to template provided by QVBoxLayout
	
	def start_display(self):
		# Displays page
		self.window.show()
		self.app.exec_() 
	
	# ------------------------------------
	# Layout
	# ------------------------------------
	def add_label(self, name, input_string):
		label = QLabel(input_string)
		
		self.lookup[name] = label
		self.layout.addWidget(label)
		
	def add_button(self, name, btn_text, target_function):
		button = QPushButton(btn_text)
		button.clicked.connect(target_function)
		
		self.lookup[name] = button
		self.layout.addWidget(button)
	
	# ------------------------------------
	# Dialog inputs
	# ------------------------------------
	def get_text_input(self):
		# https://www.tutorialspoint.com/pyqt/pyqt_qinputdialog_widget.htm
		# pre configured
		text, ok = QInputDialog.getText(self.window, 'Text Input Dialog', 'Enter your name:') # << pass in parent window, in this case it's a type QWidget window
		return text, ok
		
	def get_text_dialog(self):
		# https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
		# Two line method
		# open_dialog = QT_Custom_Dialog()
		# output = open_dialog.exec_()
		
		# Single line static method (wrapped in QT_Custom_Dialog)
		output = QT_Custom_Dialog.get_input(self.window) # << can also leave blank for modeless (but then it WONT block parent window)
		return output
		# input(output) << DONT USE INPUTS inside dialogs, QDialog seeks parent!

# =======================================
# Menu (should be in main.py)
# =======================================
class Nanny_App():
	def __init__(self):
		# ----------------------------------
		# Get tasknote
		# ----------------------------------
		self.tasklog_filename = get_tasklog_filename()
		j_string = read_tasklog(self.tasklog_filename)
		
		self.tasklog = Task_Session()
		self.tasklog._import(j_string)
		
		self.tasknote = None
		
		# ----------------------------------
		# Menu initiation / layout
		# ----------------------------------
		self.window = QT_IDE()
		
		# Labels
		self.window.add_label("lbl_totaltasks_title", "Total Tasks:")
		self.window.add_label("lbl_totaltasks_text", "NaN")
		
		self.window.add_label("lbl_description_title", "Task Description:")
		self.window.add_label("lbl_description_text", "NaN")
		
		self.window.add_label("lbl_priority_title", "Priority:")
		self.window.add_label("lbl_priority_text", "NaN")
		
		self.window.add_label("lbl_date_title", "Posted:")
		self.window.add_label("lbl_date_text", "NaN")
		
		self.window.add_label("lbl_days_title", "Days:")
		self.window.add_label("lbl_days_text", "NaN")
		
		self.window.add_label("lbl_procrastination_counter_title", "Procrastination Counter:")
		self.window.add_label("lbl_procrastination_counter_text", "NaN")
		
		# Buttons
		self.window.add_button("btn_next_task", "Next", self.next_task)
		self.window.add_button("btn_remv_task", "Remove", self.remove_task)
		self.window.add_button("btn_edit_task", "Edit", self.edit_task)
		self.window.add_button("btn_add_task", "Add New", self.add_task)
		self.window.add_button("btn_procrastinate", "Procrastinate", self.procrastinate)
		
		# ----------------------------------
		# Display first tasknote after initiation
		# ----------------------------------
		self.next_task()
		self.update_display()
	
	
	def update_display(self):
		# total number of tasks
		total_tasks = self.tasklog.length()
		self.window.lookup["lbl_totaltasks_text"].setText(str(total_tasks))
		
		if not self.tasknote:
			# nothing to update if no tasks available
			return
		
		id = self.tasknote["id"]
		# reload tasknote
		self.tasknote = self.tasklog.get_task(id)
		
		description = self.tasknote["task"].description
		count_procrastination = self.tasknote["task"].count_procrastination
		priority = self.tasknote["task"].priority
		date_start = self.tasknote["task"].date_start
		days_posted = self.tasknote["task"].calc_days()
		
		self.window.lookup["lbl_description_text"].setText(description)
		self.window.lookup["lbl_priority_text"].setText(str(priority))
		self.window.lookup["lbl_date_text"].setText(date_start)
		self.window.lookup["lbl_days_text"].setText(str(days_posted))
		self.window.lookup["lbl_procrastination_counter_text"].setText(str(count_procrastination))
	
	def save_tasklog(self):
		j_string = self.tasklog._export()
		save_tasklog(self.tasklog_filename, j_string)
		
	def procrastinate(self):
		if self.tasknote == None:
			print("Can't procrastinate non-Task")
			return
		
		id = self.tasknote["id"]
		self.tasklog.procrastinate_task(id)
		self.save_tasklog()
		self.update_display()
		
	def add_task(self):
		new_description, new_priority, ok = QT_Add_Task_Dialog.get_input(self.window.window)
		if ok:
			self.tasklog.add_task(new_description, new_priority)
			self.save_tasklog()
			self.update_display()
		
		else:
			print("boo, no new task!")
			pass
		
	def edit_task(self):
		if self.tasknote == None:
			print("Can't edit non-Task")
			return
		
		id = self.tasknote["id"]
		description = self.tasknote["task"].description
		priority = self.tasknote["task"].priority
		
		new_description, new_priority, ok = QT_Edit_Task_Dialog.get_input(self.window.window, description, priority)
		if ok:
			self.tasklog.edit_task(id, new_description, new_priority)
			self.save_tasklog()
			self.update_display()
		else:
			print("boo, no edits")
			pass
			
	def remove_task(self):
		if self.tasknote == None:
			print("Can't remove non-Task")
			return
		
		id = self.tasknote["id"]
		self.tasklog.drop_task(id)
		self.save_tasklog()
		self.next_task()
		
	def next_task(self):
		# if you hit next btn, you just procastinated!
		self.procrastinate()
	
		self.tasknote = self.tasklog.get_task()
		if self.tasknote == None:
			self.window.lookup["lbl_totaltasks_text"].setText(str(0))
			self.window.lookup["lbl_description_text"].setText("NaN")
			self.window.lookup["lbl_priority_text"].setText("NaN")
			self.window.lookup["lbl_date_text"].setText("NaN")
			self.window.lookup["lbl_days_text"].setText("NaN")
			self.window.lookup["lbl_procrastination_counter_text"].setText("NaN")
			
		else:
			self.update_display()
	
	def show(self):
		self.window.start_display()

def main_app():
	menu = Nanny_App()
	menu.show()

# ========================================
# Debug functions
# ========================================
class IDE_Test():
	def __init__(self):
		self.window = QT_IDE()
		self.window.add_label("label_1", "This is Label 1")
		self.window.add_label("label_2", "This is Label 2")
		
		self.window.add_button("btn_1", "Click Here to change Label 1", self.change_label1)
		self.window.add_button("btn_2", "Click Here to change Label 2", self.change_label2)
		
	# ------------------------------------
	# Interactivity
	# ------------------------------------
	def change_label1(self):
		output = self.window.get_text_dialog()
		self.window.lookup["label_1"].setText(str(output))
	
	def change_label2(self):
		text, ok = self.window.get_text_input()
		
		if ok:
			self.window.lookup["label_2"].setText(text)
	
	def show(self):
		self.window.start_display()

def main_IDE_debug():
	menu = IDE_Test()
	menu.show()

def main_task_debug():
	new_task1 = Tasknote()
	new_task1.set_description("this is a fresh task", 7)
	j_string1 = new_task1._export()
	print(j_string1)
	
	new_task2 = Tasknote()
	new_task2._import(j_string1)
	j_string2 = new_task2._export()
	print(j_string2)
	print(new_task2.calc_days())
	
	new_sess = Task_Session()
	new_sess.add_task("this is a fresh subtask", 2)
	new_sess.add_task("this is a fresh subtask", 5)
	
	
	
	new_sess = Task_Session()
	new_sess.add_task("this is a fresh subtask", 6)
	new_sess.add_task("this is a fresh subtask", 7)
	j_string_session = new_sess._export()
	
	new_sess2 = Task_Session()
	new_sess2._import(j_string_session)
	print(new_sess2._export())
	
if __name__ == "__main__":
	main_app()
	print('program exit')
	