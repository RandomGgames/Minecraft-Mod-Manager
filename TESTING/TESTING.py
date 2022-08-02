print("\033[0;41m TESTING \033[0m")
exit()

import yaml
import json
import os

class colors:
	NORMAL = ''
	GRAY = '\033[90m'
	RED = '\033[91m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	BLUE = '\033[94m'
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	INDENTED = '\033[90a'
	INDENTEDARROWS = '\033[90b'
	DROPPED = '\033[90e'
	BOLD = '\033[1m'
	ITALIC = '\x1B[3m'
	INVERTED = '\033[7m'
	UNDERLINE = '\033[4m'
	RESET = '\033[0m'

def log(text):
	print(f"{text}\033[0m")
	#📝 WRITE TO LOG FILES

def loadInstances():
	log(f"{colors.BOLD}{colors.BLUE}LOADING INSTANCES...")
	try:
		with open("RMMUDInstances.yaml", "r") as f:
			instances = yaml.safe_load(f)
			f.close()
	except Exception as e:
		log(f"	{colors.BOLD}{colors.RED}[WARN] Could not load instances file. {repr(e)}")
		exit()
		return

	enabled_instances = {}
	if instances and len(instances) >= 1:
		for instance_name, instance in instances.items():
			keys = ["Loader", "Enabled", "Version", "Client Directory", "Server Directory", "Client and Server Mods", "Client Mods", "Server Mods"]
			if not all(key in instance.keys() for key in keys):
				missing_keys = [key for key in keys if key not in instance]
				if len(missing_keys) == 1:
					log(f"	{colors.BOLD}{colors.RED}[WARN] Cannot load instance \"{instance_name}\". It is missing the key: {missing_keys[0]}")
				else:
					log(f"	{colors.BOLD}{colors.RED}[WARN] Cannot load instance \"{instance_name}\". It is missing the keys: {', '.join(missing_keys)}")
			else:
				if instance["Enabled"]:

					instance["Loader"] = str(instance["Loader"] or "").title()
					instance["Enabled"] = bool(instance["Enabled"])
					instance["Version"] = str(instance["Version"] or "")
					instance["Client Directory"] = str(instance["Client Directory"] or "")
					instance["Server Directory"] = str(instance["Server Directory"] or "")

					replacers = {"$AppData": os.getenv("APPDATA"), "$Documents": os.getenv("USERPROFILE")}
					keys = ["Client Directory", "Server Directory"]
					
					for key in keys:
						for replace, replacer in replacers.items():
							instance[key] = instance[key].replace(replace, replacer)

					if not isinstance(instance["Client and Server Mods"], list):
						instance["Client and Server Mods"] = str(instance["Client and Server Mods"] or "")
						instance["Client and Server Mods"] = [instance["Client and Server Mods"]]
					instance["Client and Server Mods"] = list(str(i) for i in instance["Client and Server Mods"] if i != None and i != "")

					if not isinstance(instance["Client Mods"], list):
						instance["Client Mods"] = str(instance["Client Mods"] or "")
						instance["Client Mods"] = [instance["Client Mods"]]
					instance["Client Mods"] = list(str(i) for i in instance["Client Mods"] if i != None and i != "")

					if not isinstance(instance["Server Mods"], list):
						instance["Server Mods"] = str(instance["Server Mods"] or "")
						instance["Server Mods"] = [instance["Server Mods"]]
					instance["Server Mods"] = list(str(i) for i in instance["Server Mods"] if i != None and i != "")

					log(f"	{colors.CYAN}Loaded instance \"{instance_name}\".")
					enabled_instances[instance_name] = instance

	if len(enabled_instances) == 1:
		log(f"	{colors.GREEN}Done loading {len(enabled_instances)} instance.")
	else:
		log(f"	{colors.GREEN}Done loading {len(enabled_instances)} instances.")
	return enabled_instances

def loadConfig():
	log(f"{colors.BOLD}{colors.BLUE}LOADING CONFIG...")
	try:
		with open("RMMUDConfig.yaml", "r") as f:
			config = yaml.safe_load(f)
			f.close()
		keys = ["Download Mods Location", "Check for RMMUD Updates", "CurseForge API Key"]
		if not all(key in config.keys() for key in keys):
			missing_keys = [key for key in keys if key not in config]
			if len(missing_keys) == 1:
				log(f"	{colors.BOLD}{colors.RED}[WARN] Cannot load config due to missing key: {missing_keys[0]}")
			else:
				log(f"	{colors.BOLD}{colors.RED}[WARN] Cannot load config due to missing keys: {', '.join(missing_keys)}")
			exit()
			return

		downloads_location = str(config["Download Mods Location"] or "")
		enable_rmmud_updates = bool(config["Check for RMMUD Updates"])
		curseforge_api_key = str(config["CurseForge API Key"] or "")

		log(f"	{colors.GREEN}Done reading config.")
		return {"download_mods_location": downloads_location, "check_for_updates": enable_rmmud_updates, "headers": {"Accept": "application/json", "x-api-key": curseforge_api_key}}

	except Exception as e:
		log(f"	{colors.BOLD}{colors.RED}[WARN] Could not load config. {repr(e)}")
		exit()
		return

def modsList(instances):
	log(f"{colors.BOLD}{colors.BLUE}LOADING MODS...")
	mods = {}
	total_loaded_mods = 0
	for instance_name, instance in instances.items():
		log(f"	{colors.CYAN}Loading mods from instance \"{instance_name}\"")
		version = str(instance["Version"])
		loader = str(instance["Loader"])
		if version not in mods:
			mods[version] = {}
		if loader not in mods[version]:
			mods[version][loader] = {"client_mods": {}, "server_mods": {}}
		
		for mod_type in [instance["Client and Server Mods"], instance["Client Mods"], instance["Server Mods"]]:
			print(f"{mod_type = }")
		#for client_and_server_mod in instance["Client and Server Mods"]:
		#	if client_and_server_mod not in mods[version][loader]["client_mods"]:
		#		mods[version][loader]["client_mods"][client_and_server_mod] = [instance["Client Directory"]]
		#	else:
		#		if instance["Client Directory"] not in mods[version][loader]["client_mods"][client_and_server_mod]:
		#			mods[version][loader]["client_mods"][client_and_server_mod].append(instance["Client Directory"])
		#	if client_and_server_mod not in mods[version][loader]["server_mods"]:
		#		mods[version][loader]["server_mods"][client_and_server_mod] = [instance["Server Directory"]]
		#	else:
		#		if instance["Server Directory"] not in mods[version][loader]["server_mods"][client_and_server_mod]:
		#			mods[version][loader]["server_mods"][client_and_server_mod].append(instance["Server Directory"])
		#	total_loaded_mods += 1
		#
		#for client_mod in instance["Client Mods"]:
		#	if client_mod not in mods[version][loader]["client_mods"]:
		#		mods[version][loader]["client_mods"][client_mod] = [instance["Client Directory"]]
		#	else:
		#		if instance["Client Directory"] not in mods[version][loader]["client_mods"][client_mod]:
		#			mods[version][loader]["client_mods"][client_mod].append(instance["Client Directory"])
		#	total_loaded_mods += 1
		#
		#for server_mod in instance["Server Mods"]:
		#	if server_mod not in mods[version][loader]["server_mods"]:
		#		mods[version][loader]["server_mods"][server_mod] = [instance["Server Directory"]]
		#	else:
		#		if instance["Server Directory"] not in mods[version][loader]["server_mods"][server_mod]:
		#			mods[version][loader]["server_mods"][server_mod].append(instance["Server Directory"])
		#	total_loaded_mods += 1

	if total_loaded_mods == 1:
		log(f"	{colors.GREEN}Loaded {total_loaded_mods} mod!")
	else:
		log(f"	{colors.GREEN}Loaded {total_loaded_mods} mods!")
	return mods

def main():
	config = loadConfig()
	#log(json.dumps(config, indent = "\t"))
	#log(config)

	instances = loadInstances()
	#log(json.dumps(instances, indent = "\t"))
	#log(instances)

	mods = modsList(instances)
	#log(json.dumps(mods, indent = "\t"))
	log(mods)

if __name__ == "__main__":
	main()
