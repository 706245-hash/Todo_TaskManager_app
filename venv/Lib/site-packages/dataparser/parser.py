import os
import logging
import json

#TODO Set logger    
logging.basicConfig(
  level = logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,"
)
LOGGER = logging.getLogger()


#Path verification
'''def gen_path(file_name):
    if file_name == '':
        raise EnvironmentError("No path were specified")
    else:
        file_name = "text"
        strip = file_name.split("/")
        directory = file_name.replace(strip[-1], "")
        if not os._exists(file_name):
            os.mkdir(directory)'''

def _path_correction(path):
    if path.__contains__("\\"):
        return path.replace("\\", "/")
    else:
        return path

def write_file(file_name: str, data: dict):
    #gen_path(file_name)
    file_name = _path_correction(file_name)
    #Get dict
    if not type(data) == dict:
        raise TypeError("Argument: \"data\" must be dictionary type.\nwrite_file(\"file_name\", \"overwrite\" = True, \"data\" = { }")
    elif data.__len__ == 0:
        raise ValueError("\"data\" must not be empty, for erasing data use clear() instead")
    else:
        if os._exists(file_name):
            os.remove(file_name)
        jstream = open(file_name, "w+")
        json.dump(data, jstream)

        jstream.close()

        #Logger
        log = file_name.split("/")
        LOGGER.info(f"{log[-1]} successfully created")

def read_file(file_name: str):
    jstream = open(file_name, "r")
    dt = jstream.read()
    jstream.close()
    
    data = json.loads(dt)

    return data

#file_name = Name of the file, data = tuple to filter, returns a tuple
def get_data(file_name: str, data: tuple, as_dict = False):
    DATA = read_file(file_name)
    if as_dict:
        if data.count == 0:
            return DATA
        else:
            dData = dict()
            keys = tuple(DATA.keys())
            values = tuple(DATA.values())

            for x in keys:
                dData[x] = values[keys.index(x)]
            
            return dData
    else:
        if data.count == 0:
            return tuple(DATA.values())
        else:
            lData = list()
            for x in data:
                lData.append(DATA[x])
            return tuple(lData)

def update_file(file_name: str, data: dict):
    file_name = _path_correction(file_name)
    if file_name == "":
        raise ValueError("\"file_name\" must not be empty")
    elif data.__len__() == 0:
        raise ValueError("\"data\" must contain data to update")
    else:
        try:
            DATA = read_file(file_name)
        except:
            LOGGER.warning(f"No {file_name} were found, a new file will be created")
            DATA = dict()
        finally:
            keys = tuple(data.keys())
            for x in keys:
                DATA[x] = data[x]
            write_file(file_name, DATA)

            #Logging
            log = file_name.split("/")
            LOGGER.info(f"{log[-1]} updated successfully")

def delete_data(file_name: str):
    file_name = _path_correction(file_name)
    if file_name == "":
        raise ValueError("\"file_name\" must not be empty")
    else:
        os.remove(file_name)
        log = file_name.split("/")
        LOGGER.info(f"{log[-1]} was removed")

def delete_many(*file_names: str):
    for x in file_names:
        if not type(x) == str:
            LOGGER.error(f"{x} is not a string")
        else:
            delete_data(x)