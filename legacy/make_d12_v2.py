import os

#base folder where this script lives
base_folder = os.path.dirname(os.path.abspath(__file__)) # is where the base folder lives, dirname is a function is os package, this sets the directory to the absolute path
input_folder = os.path.join(base_folder, "inputs")       # where dopant basis files are stored, takes the base folder and looks for the input folder
templates_folder = os.path.join(base_folder, "templates") # where input templates are stored, looks in the base folder and looks for template folder

#spinlock values, use a dictionary mapping an atomic number to a spinlock value
spinlock_map = {
    '21': '2',  # Sc
    '22': '1',  # Ti
    '23': '2',  # V
    '24': '3',  # Cr
    '25': '4',  # Mn
    '26': '3',  # Fe
    '27': '2',  # Co
    '28': '1',  # Ni
    '29': '2',  # Cu
    '30': '1',  # Zn
    '4' : '1',  # Be
    '20': '1',  # Ca
    '48': '1',  # Cd
    '12': '1',  # Mg
    '232': '1',  # Ge
    '250': '1', # Sn with PSE
    '238': '1', # Sr with PSE
    '247': '2', # Ag with PSE
    '246': '2', # Pd with PSE
    '278': '1', # Pt with PSE
    '6': '1',   # C
    '3': '2',   # Li
    '14': '1', # Si
    '282': '1' #Pb
}

#detect templates (skip any with 'prop' or 'band' in the name so script doesnt read wrong template.
template_files = {}  #directionary to store template identifier -> full path
for file in os.listdir(templates_folder): #for loop used to go through each file in the template folder, must use os.listdir to name a folder
    filename_lower = file.lower()  #makes all lowercase, file name is converted to full lowercase and saved in variable filename_lower
    if file.startswith("template_") and file.endswith(".txt") \
       and "prop" not in filename_lower \
       and "band" not in filename_lower:  #skip band template
        # \ is a line continuation character, this conditional statement confirms that the filename starts with template and ends with .txt, deosnt inc prop AND band
        site_label = file.replace("template_", "").replace(".txt", "") #remove prefix/suffix to get simplified site label, .replace() creates a new string at every occurrence, here temp and txt is replaced with nothing, removing those words
        template_files[site_label] = os.path.join(templates_folder, file) #site label is read from the template, with template and .txt removed, is directionary key assignment, key = site label and after is assingment, joining the path of new template name and the file in the for loop, gives the full path to that file
        #the full path is stored in the dictionary template_files, with key (which is site label with prefix and suffix removed)
#print detected templates for debugging
print("Using templates:", list(template_files.keys()))

# automatically detect dopants (all .txt files in inputs folder)
dopant_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")] #list comprehension, loops through all entries, calling them f in the input folder, keep the ones ending in .txt

def modify_input(template_lines, basis_file_path):
    """
    Takes a template and a dopant input file and produces a d12 input file.
    Returns:
        new_lines: list of lines for the d12 file
        dopant_z: atomic number of dopant (string)
        element_symbol: element symbol from the dopant file
    """
    new_lines = []  #collects modified lines of a template

    #open dopant basis file
    with open(basis_file_path, "r") as bf: #open dopant file as read ('r')
        bf_lines = bf.readlines()  #read all lines

    element_symbol = bf_lines[0].strip()  #first line = element symbol, [] indexes the list, bf_lines is a list of strings, each line from the file
    dopant_z = bf_lines[1].strip()        #second line = atomic number as string
    basis_lines = bf_lines[2:]            #rest of file = basis set, strip removes whitespaces, [2:] means line 3rd line onwards

    #get spinlock value, return None if not found
    if dopant_z not in spinlock_map:
        return None #for the whole function

    spinlock_value = spinlock_map[dopant_z] #retrive spinlock value from dictionary, dopant_z is the key, spinlock_map[dopant_z] looks up the value associated with that key

    #replace placeholders in template
    for line in template_lines: #loops over all lines in the template
        if "<DOPANT_ATOMIC_NUMBER>" in line:
            new_lines.append(line.replace("<DOPANT_ATOMIC_NUMBER>", dopant_z))
        elif "<BASIS_SET_BLOCK>" in line:
            new_lines.extend(basis_lines)
        elif "<SPIN_LOCK>" in line:
            new_lines.append(line.replace("<SPIN_LOCK>", spinlock_value))
        else:
            new_lines.append(line)
    #append adds one item (so 1 line as we read line by line), extend takes every element of the iterable and adds them one by one to the list, is a list of strings

    return new_lines, dopant_z, element_symbol #exits the function

#loop over all dopant files
for dopant_file in dopant_files:
    basis_path = os.path.join(input_folder, dopant_file) #gives the full path to the basis files

    #read element symbol (first line of dopant file)
    with open(basis_path, "r") as bf: #opens basis folder as read
        element_symbol = bf.readline().strip() #remove whitespaces

    #loop over all templates
    for site_label, template_file in template_files.items(): #for loop for a dictionary, template_files is the dictionary; site_label, template_file unpacks each key-value pair into 2 variables, site_label is dictionary key, template_file gets the value, loops over each template in the dictionary (key, value) -> each key-value pair
        site_folder = os.path.join(base_folder, element_symbol, site_label) #site folder is joining the base folder, element symbol and the site label, full path to site label in each elemental folder
        os.makedirs(site_folder, exist_ok=True)  # create subfolder for each template with exist_ok = True

        #read template lines
        with open(template_file, "r") as f: #f assgins file object to variable f
            template_lines = f.readlines() #use f to read the files contents, reads each line, each line becomes an element in a list

        # generate new input with replacements
        result = modify_input(template_lines, basis_path) #calling function
        if result is None:
            print(f"Skipped (no spinlock value found) -> {element_symbol}") #if spinlock unassinged, dont write anything for that element, file is ignored, print to user
            break #means we ignore this dopant stuff if there is no spinlock value, is a control statement used to exit the loop

        new_input, dopant_z, _ = result #used when we ignore a value, is j a variable name, is for element symbol, but it is not needed anymore

        #new_input is modified template line, dopant_z is atomic number of the dopant, _ is element symbol, refer to modify_input function

        #prepare output file path
        output_file = os.path.join(site_folder, f"{element_symbol}_{site_label}.d12") #outpile file is given a path, joins the site_folder, f string for element symbol, site label and .d12 extension

        #write file if it doesn't already exist
        if not os.path.exists(output_file): #if it does not exist
            with open(output_file, "w") as f: #with _ as f is a context manager, closes file when it is done, actually writes the file 'w'
                f.writelines(new_input) #new input is a list of strings, writelines() writes each string in the list to the file in order, new file is writen, dopant_z is only used to name the folder
            print(f"Generated input -> {output_file}") #if written print
        else: #if it does exist, as per the if statement:
            print(f"Skipped (already exists) -> {output_file}") #if not written print