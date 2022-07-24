from marshmallow import missing
import yaml
import json

def loadInstances():
	print("Loading Instances...")
	try:
		with open("RMMUDInstances.yaml", "r") as f:
			instances = yaml.safe_load(f)
			f.close()
	except Exception as e:
		print(f"[WARN] Could not load instances file. {repr(e)}")
		return


	enabled_instances = {}
	for instance_name, instance in instances.items():
		keys = ["Loader", "Enabled", "Version", "Client Directory", "Server Directory", "Client and Server Mods", "Client Mods", "Server Mods"]
		if not all(key in instance.keys() for key in keys):
			missing_keys = [key for key in keys if key not in instance]
			if len(missing_keys) == 1:
				print(f"[WARN] Cannot load instance \"{instance_name}\". It is missing the key: {missing_keys[0]}")
			else:
				print(f"[WARN] Cannot load instance \"{instance_name}\". It is missing the keys: {', '.join(missing_keys)}")
		else:
			print("Found all keys")

			if isinstance(instance["Loader"], str):
				print("Enabled is a string")

			if instance["Enabled"]:
				enabled_instances[instance_name] = instance
	
	return enabled_instances

def loadConfig():
	print("Loading Config...")
	with open("RMMUDConfig.yaml", "r") as f:
		config = yaml.safe_load(f)
	return {"download_mods_location": config["Download Mods Location"], "check_for_updates": config["Check for RMMUD Updates"], "headers": {"Accept": "application/json", "x-api-key": config["CurseForge API Key"]}}

def main():
	print(loadConfig())
	instances = loadInstances()
	print(json.dumps(instances, indent = "\t"))

if __name__ == "__main__":
	main()
