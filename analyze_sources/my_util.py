import os

def get_csvs(path):
	return __get_files_wk([], path, ".csv")

def __get_files_wk(file_list, path, extension):
	if extension.find(".") == -1:
		extension = "." + extension

	f_names = os.listdir(path)
	for f_name in f_names:
		cur_f_path = os.path.join(path, f_name)
		if os.path.isdir(cur_f_path):
			file_list = __get_files_wk(file_list, cur_f_path, extension)
		else:
			if f_name.find(extension) > 0:
				file_list.append(os.path.join(path, f_name))

	return file_list

