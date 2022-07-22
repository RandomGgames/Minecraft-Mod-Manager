import yaml
import json

def load_instances():
	with open("RMMUDInstances.yaml", "r") as f:
		instances = yaml.safe_load(f)
		f.close()
	for instance_name, instance in instances.items():
		print(f"{instance_name = }")
		print(json.dumps(instance, indent = "\t"))
		print()
		
		#print(f"{instance} Enabled: {instances[instance]['Enabled']}")
		#print(type(instances[instance]["Enabled"]))
		#if instances[instance]["Enabled"]:
		#	print(instances[instance])

def main():
	with open("RMMUDConfig.yaml", "r") as f: config = yaml.safe_load(f)
	download_mods_location = config["Download Mods Location"]
	check_for_updates = config["Check for RMMUD Updates"]
	headers = {"Accept": "application/json", "x-api-key": config["CurseForge API Key"]}

	mods = load_instances()

if __name__ == "__main__":
	main()
