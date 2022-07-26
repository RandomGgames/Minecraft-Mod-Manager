from http import client
import yaml
import json

def loadInstances():
	print("LOADING INSTANCES...")
	try:
		with open("RMMUDInstances.yaml", "r") as f:
			instances = yaml.safe_load(f)
			f.close()
	except Exception as e:
		print(f"	[WARN] Could not load instances file. {repr(e)}")
		exit()
		return

	enabled_instances = {}
	for instance_name, instance in instances.items():
		keys = ["Loader", "Enabled", "Version", "Client Directory", "Server Directory", "Client and Server Mods", "Client Mods", "Server Mods"]
		if not all(key in instance.keys() for key in keys):
			missing_keys = [key for key in keys if key not in instance]
			if len(missing_keys) == 1:
				print(f"	[WARN] Cannot load instance \"{instance_name}\". It is missing the key: {missing_keys[0]}")
			else:
				print(f"	[WARN] Cannot load instance \"{instance_name}\". It is missing the keys: {', '.join(missing_keys)}")
		else:
			if instance["Enabled"]:

				instance["Loader"] = str(instance["Loader"] or "")
				instance["Enabled"] = bool(instance["Enabled"])
				instance["Version"] = str(instance["Version"] or "")
				instance["Client Directory"] = str(instance["Client Directory"] or "")
				instance["Server Directory"] = str(instance["Server Directory"] or "")
				
				if isinstance(instance["Client and Server Mods"], str):
					instance["Client and Server Mods"] = [str(instance["Client and Server Mods"])]
				

				
				print(f"	{instance['Client and Server Mods'] = }")
				#instance["Client and Server Mods"] = [] if instance["Client and Server Mods"] is None else list(instance["Client and Server Mods"])
				#instance["Client and Server Mods"] = [str(i) for i in instance["Client and Server Mods"] if i]
				
				print(f"	Loaded instance \"{instance_name}\".")
				enabled_instances[instance_name] = instance
	
	if len(enabled_instances) == 1:
		print(f"	Done loading {len(enabled_instances)} instance.")
	else:
		print(f"	Done loading {len(enabled_instances)} instances.")
	return enabled_instances

def loadConfig():
	print("LOADING CONFIG...")
	try:
		with open("RMMUDConfig.yaml", "r") as f:
			config = yaml.safe_load(f)
			f.close()
		keys = ["Download Mods Location", "Check for RMMUD Updates", "CurseForge API Key"]
		if not all(key in config.keys() for key in keys):
			missing_keys = [key for key in keys if key not in config]
			if len(missing_keys) == 1:
				print(f"	[WARN] Cannot load config due to missing key: {missing_keys[0]}")
			else:
				print(f"	[WARN] Cannot load config due to missing keys: {', '.join(missing_keys)}")
			exit()
			return
		
		downloads_location = str(config["Download Mods Location"] or "")
		enable_rmmud_updates = bool(config["Check for RMMUD Updates"])
		curseforge_api_key = str(config["CurseForge API Key"] or "")
		
		print(f"	Done reading config.")
		return {"download_mods_location": downloads_location, "check_for_updates": enable_rmmud_updates, "headers": {"Accept": "application/json", "x-api-key": curseforge_api_key}}

	except Exception as e:
		print(f"	[WARN] Could not load config. {repr(e)}")
		exit()
		return

def main():
	#config = loadConfig()
	#print(config)

	instances = loadInstances()
	#print(instances)

if __name__ == "__main__":
	main()
