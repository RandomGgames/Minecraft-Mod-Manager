from datetime import datetime
from zipfile import ZipFile
import json
import os
import requests
import shutil
import time
import yaml
run_time = datetime.now().strftime("%Y-%m-%d")

VERSION = "3.6WIP" #DO NOT CHANGE THIS YOURSELF!

class style:
	BLUE = "\033[94m"
	CYAN = "\033[96m"
	GRAY = "\033[90m"
	GREEN = "\033[92m"
	PURPLE = "\033[95m"
	RED = "\033[91m"
	YELLOW = "\033[33m"
	UNDERLINED = "\033[4m"
	ITALIC = "\x1B[3m"
	BOLD = "\033[1m"
	RESET = "\033[0m"

def debug(text):
	print(f"{style.ITALIC}{style.GRAY}{text}{style.RESET}")

class log:
	def header(text):
		print(f"{style.BOLD}{style.CYAN}{text}{style.RESET}")

	def info(text):
		print(f"{style.BLUE}{text}{style.RESET}")

	def completed(text):
		print(f"{style.GREEN}{text}{style.RESET}")

	def special(text):
		print(f"{style.PURPLE}{text}{style.RESET}")

	def warn(text):
		print(f"{style.YELLOW}{text}{style.RESET}")

	def err(text):
		print(f"{style.RED}{text}{style.RESET}")

	def exit(text):
		log.err(text)
		log.toFile(text)
		input("PRESS ANY KEY TO EXIT.")
		exit()

	def toFile(text):
		if not os.path.exists("RMMUDLogs"): os.makedirs("RMMUDLogs")
		with open(f"RMMUDLogs/{run_time}.log", "a", encoding = "UTF-8") as file: file.write(f"{str(text)}\n")
		with open(f"RMMUDLogs/latest.log", "a", encoding = "UTF-8") as file: file.write(f"{str(text)}\n")

class github:
	def checkForGithubUpdate(enabled):
		log.header("CHECKING FOR SCRIPT UPDATES:")
		try:
			github_latest_version = requests.get("https://api.github.com/repos/RandomGgames/RMMUD/releases/latest").json()
			#debug(f"github_latest_version = {json.dumps(github_latest_version)}")
			github_version = str(github_latest_version['tag_name'])
		except Exception as e:
			if github_latest_version["message"][:23]  == "API rate limit exceeded":
				reset_time = round((requests.get("https://api.github.com/rate_limit").json()["resources"]["core"]["reset"] - datetime.now().timestamp()) / 60, 1)
				log.warn(f"	[WARN] Could not retreive latest GitHub release version due to exceeding API limit. It wil reset in {reset_time} minutes. Canceling auto-update.")
			else:
				log.warn(f"	[WARN] Could not retreive latest GitHub release version. Canceling auto-update. {repr(e)}")
			return

		if VERSION  == github_version:
			log.info(f"	You have the latest release!")
		elif len(VERSION) > 3 and VERSION[:3] <= github_version:
			log.warn(f"	Your updater is out of date ({VERSION} vs {github_version}). Updating now!")
			github.downloadLatestGithubRelease(github_latest_version)
		elif len(VERSION) > 3 and not VERSION[:3] <= github_version:
			log.special(f"	Working on a new release ay? Good luck!")
		elif VERSION < github_version:
			log.warn(f"	Your updater is out of date ({VERSION} vs {github_version}). Updating now!")
			github.downloadLatestGithubRelease(github_latest_version)
		elif VERSION > github_version:
			log.special(f"	Your updater is... wait... says here that I am more up to date than the latest release? How did you manage to do that...? HOW??")

	def downloadLatestGithubRelease(github_data):
		rmmud_data = [asset for asset in github_data["assets"] if asset["name"]  == "RMMUD.py"]
		try:
			rmmud_data[0]
		except:
			log.warn(f"	[WARN] Error retreiving RMMUD.py asset from GitHub. Canceling auto-update.")
			return

		download_url = rmmud_data["browser_download_url"]
		file_name = rmmud_data["name"]

		log.info(f"	Downloading RMMUD.py...")
		try:
			open(file_name, "wb").write(requests.get(download_url).content).close()
			log.info(f"	Downloaded {file_name} V{github_data['tag_name']}")
			import RMMUD
			exit()
		except Exception as e:
			log.warn(f"	[WARN] Error downloading RMMUD.py. Canceling auto-update. {repr(e)}")

def loadInstances():
	log.header(f"LOADING INSTANCES...")
	try:
		with open("RMMUDInstances.yaml", "r") as f:
			instances = yaml.safe_load(f)
			f.close()
	except Exception as e:
		log.exit(f"	[WARN] Could not load instances file. {repr(e)}")

	enabled_instances = {}
	if instances and len(instances) >= 1:
		for instance_name, instance in instances.items():
			keys = ["Loader", "Enabled", "Version", "Client Directory", "Server Directory", "Client and Server Mods", "Client Mods", "Server Mods"]
			if not all(key in instance.keys() for key in keys):
				missing_keys = [key for key in keys if key not in instance]
				if len(missing_keys)  == 1:
					log.warn(f"	[WARN] Cannot load instance \"{instance_name}\". It is missing the key: {missing_keys[0]}")
				else:
					log.warn(f"	[WARN] Cannot load instance \"{instance_name}\". It is missing the keys: {', '.join(missing_keys)}")
			else:
				if instance["Enabled"]:
					log.info(f"	Loading instance \"{instance_name}\"...")

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

					enabled_instances[instance_name] = instance

				else:
					log.info(f"	Ignoring instance \"{instance_name}\".")

	if len(enabled_instances)  == 1:
		log.completed(f"	Done loading {len(enabled_instances)} instance.")
	else:
		log.completed(f"	Done loading {len(enabled_instances)} instances.")
	return enabled_instances

def loadConfig():
	log.header(f"LOADING CONFIG...")
	try:
		with open("RMMUDConfig.yaml", "r") as f:
			config = yaml.safe_load(f)
			f.close()
		keys = ["Download Mods Location", "Check for RMMUD Updates", "CurseForge API Key"]
		if not all(key in config.keys() for key in keys):
			missing_keys = [key for key in keys if key not in config]
			if len(missing_keys)  == 1:
				log.warn(f"	[WARN] Cannot load config due to missing key: {missing_keys[0]}")
			else:
				log.warn(f"	[WARN] Cannot load config due to missing keys: {', '.join(missing_keys)}")
			exit()
			return

		downloads_location = str(config["Download Mods Location"] or "")
		enable_rmmud_updates = bool(config["Check for RMMUD Updates"])
		curseforge_api_key = str(config["CurseForge API Key"] or "")

		log.completed(f"	Done reading config.")
		return {"download_mods_location": downloads_location, "check_for_updates": enable_rmmud_updates, "headers": {"Accept": "application/json", "x-api-key": curseforge_api_key}}

	except Exception as e:
		log.warn(f"	[WARN] Could not load config. {repr(e)}")
		exit()
		return

def modsList(instances):
	log.header(f"LOADING MODS...")
	mods = {}
	total_loaded_mods = 0
	for instance_name, instance in instances.items():
		loader = str(instance["Loader"])
		version = str(instance["Version"])
		if loader not in mods:
			mods[loader] = {}
		if version not in mods[loader]:
			mods[loader][version] = {}

		for section in [i for i in instance if isinstance(instance[i], list)]:
			#debug(f"	{section = }")
			for mod in instance[section]:
				#debug(f"	{mod = }")
				if mod not in mods[loader][version]:
					log.info(f"	Loading url \"{mod}\"...")
					mods[loader][version][mod] = []
				loaded_mod = False
				if section  == "Client and Server Mods" or section  == "Client Mods":
					if instance["Client Directory"] not in mods[loader][version][mod]:
						mods[loader][version][mod].append(instance["Client Directory"])
						loaded_mod = True
				if section  == "Client and Server Mods" or section  == "Server Mods":
					if instance["Server Directory"] not in mods[loader][version][mod]:
						mods[loader][version][mod].append(instance["Server Directory"])
						loaded_mod = True
				if loaded_mod: total_loaded_mods += 1
	if total_loaded_mods  == 1:
		log.completed(f"	Loaded {total_loaded_mods} mod.")
	else:
		log.completed(f"	Loaded {total_loaded_mods} mods.")
	return mods

def downloadMods(mods, config):
		log.header(f"DOWNLOADING MODS...")
		cache = {}
		#debug(f"	mods = {json.dumps(mods)}")
		#debug(f"	config = {json.dumps(config)}")

		def fabricModrinth(url, config):
			pass
		
		for loader in mods:
			#debug(f"	{loader = }")
			if loader not in cache:
				cache[loader] = {}
			for version in mods[loader]:
				#debug(f"	{version = }")
				if version not in cache[loader]:
					cache[loader][version] = {}
				for url in mods[loader][version]:
					log.info(f"	Processing {url}")
					try:
						if url[-1]  == "/": url = url[:-1] #Remove trailing / from link sif it has one at the end
					except: pass

					if url.startswith("https://modrinth.com"):
						debug(f"	{url.startswith('https://modrinth.com') = }")
					
					
					
					#if link[0:25]  == "https://modrinth.com/mod/" and link[25:len(link)] != "":
					#	slug = link[25:len(link)]
					#	if not any(x in slug for x in ["/", " ", "\\"]):
					#		log.info(f"		Processing: {slug}")
							
							
							
							
							
							
#							if link not in cache or version not in cache[link]['versions']:
#								#log.info(f"			Caching {slug} for {version}...")
#								try:
#									modrinth_versions = requests.get(f'https://api.modrinth.com/v2/project/{slug}/version?game_versions = ["{version}"]&loaders = ["{loader}"]').json()
#									if len(modrinth_versions) > 0:
#										latest_modrinth_version = modrinth_versions[0]
#										files = latest_modrinth_version["files"]
#										if any(file["primary"] for file in files):
#											files = [file for file in files if file["primary"]  == True]
#										file_name = files[0]['filename']
#										download_url = files[0]['url']
#										if not os.path.exists(f'{download_mods_location}/{loader}/{version}/{file_name}'):
#											try:
#												open(f"{download_mods_location}/{loader}/{version}/{file_name}", "wb").write(requests.get(download_url).content)
#												log.info(f"			Downloaded {file_name} to {download_mods_location}/{loader}/{version}")
#											except Exception as e:
#												log.info(f"			[WARN] Could not download file. {repr(e)}")
#										cache[link] = {"versions": {}}
#										cache[link]["versions"][version] = f"{download_mods_location}/{loader}/{version}/{file_name}"
#									else: log.info(f"			[WARN] Cannot find any {version} compatable versions of this mod.")
#								except Exception as e:
#									log.info(f"			[WARN] Cannot access the Modrinth API.")
#							if link in cache:
#								if not os.path.exists(f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}"):
#									try:
#										shutil.copyfile(cache[link]["versions"][version], f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}")
#										log.info(f"			Copied \"{cache[link]['versions'][version]}\" into \"{mods_directory}\"")
#									except Exception as e:
#										log.info(f"			[WARN] Something went wrong copying \"{cache[link]['versions'][version]}\" into \"{mods_directory}\". {repr(e)}")
#								else: log.info(f"			{slug} is already up to date.")
#							else: log.info(f'		[WARN] Invlalid slug: "{slug}"')
#						else: log.warn(f"	[WARN] Links must be to a mod page. {link} is not a valid mod page link.")
#									if link[0:45]  == "https://www.curseforge.com/minecraft/mc-mods/":
#										if link[45:len(link)] != "":
#											slug = link[45:len(link)]
#											if not any(x in slug for x in ["/", " ", "\\"]):
#												log.info(f"		Processing: {slug}")
#												if link not in cache or version not in cache[link]['versions']:
#													#log.info(f"			Caching {slug} for {version}...")
#													try:
#														curseforge_mod = requests.get("https://api.curseforge.com/v1/mods/search", params = {"gameId": "432","slug": slug, "classId": "6"}, headers = headers).json()["data"]
#														if len(curseforge_mod) > 0:
#															curseforge_id = curseforge_mod[0]["id"]
#															curseforge_files = requests.get(f"https://api.curseforge.com/v1/mods/{curseforge_id}/files", params = {"gameVersion": version, "modLoaderType": curseforge_modLoaderType}, headers = headers).json()["data"]
#															if len(curseforge_files) > 0:
#																curseforge_files = list(file for file in curseforge_files if version in file["gameVersions"])
#																latest_curseforge_file = curseforge_files[0]
#																file_name = latest_curseforge_file["fileName"]
#																download_url = latest_curseforge_file["downloadUrl"]
#																if download_url  == None:
#																	download_url = f"https://edge.forgecdn.net/files/{str(latest_curseforge_file['id'])[0:4]}/{str(latest_curseforge_file['id'])[4:7]}/{file_name}"
#																	pass
#																if not os.path.exists(f"{download_mods_location}/{loader}/{version}/{file_name}"):
#																	try:
#																		open(f"{download_mods_location}/{loader}/{version}/{file_name}", "wb").write(requests.get(download_url).content)
#																		log.info(f"			Downloaded {file_name} to {download_mods_location}/{loader}/{version}")
#																	except Exception as e:
#																		log.info(f"			[WARN] Could not download file. {repr(e)}")
#																cache[link] = {"versions": {}}
#																cache[link]["versions"][version] = f"{download_mods_location}/{loader}/{version}/{file_name}"
#															else: log.info(f"			[WARN] Cannot find any {version} compatable versions of this mod.")
#														else:
#															log.info(f"		[WARN] Could not find mod {slug}. Make sure the url {link} is valid and not a redirect!")
#													except Exception as e:
#														log.info(f"			[WARN] Cannot access the CurseForge API.")
#												if link in cache:
#													if not os.path.exists(f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}"):
#														try:
#															shutil.copyfile(cache[link]["versions"][version], f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}")
#															log.info(f"			Copied \"{cache[link]['versions'][version]}\" into \"{mods_directory}\"")
#														except Exception as e:
#															log.info(f"			[WARN] Something went wrong copying \"{cache[link]['versions'][version]}\" into \"{mods_directory}\". {repr(e)}")
#													else: log.info(f"			{slug} is already up to date.")
#											else: log.info(f'		[WARN] Invlalid slug: "{slug}"')
#										else: log.warn(f"	[WARN] Links must be to a mod page. {link} is not a valid mod page link.")
#							elif loader  == "forge":
#								curseforge_modLoaderType = 1
#								log.warn(f"	[WARN] Script does not currently support {loader} mods yet. Ignoring instance {instance_text}.")
#							else:
#								log.warn(f"	[WARN] Script does not support {loader} mods. Ignoring instance {instance_text}. Suggest support via github under the issue tracker https://github.com/RandomGgames/MMUD")




		debug(f"	cache = {json.dumps(cache)}")

def downloadFabricModrinthMod():
	pass

def main():
	if os.path.exists("RMMUDLogs/latest.log"): open("RMMUDLogs/latest.log", "w").close() #Clears latest.log
	log.info(f"[{datetime.now()}] RUNNING RMMUD")

	config = loadConfig()
	#debug(f"	{config = }")

	if config["check_for_updates"]: github.checkForGithubUpdate()

	instances = loadInstances()
	#debug(f"	{instances = }")

	mods = modsList(instances)
	debug(f"	mods = {json.dumps(mods)}")

	downloadMods(mods, config)

	#
	#"""
	#LOAD CONFIG
	#"""
	#log.info("LOADING CONFIG:")
	#try:
	#	with open("RMMUDConfig.json") as f:
	#		config = json.load(f)
	#		download_mods_location = config["download_mods_location"]
	#		instances = config["instances"]
	#		check_for_updates = config["check_for_rmmud_updates"]
	#		headers = {"Accept": "application/json", "x-api-key": config["x-api-key"]}
	#		log.info("	Config read successfully.")
	#except Exception as e:
	#	log.warnExit(f"	[WARN] Could not read config file. Please fix the following error: {repr(e)}")
	#
	#if not os.path.exists(download_mods_location):
	#	os.makedirs(download_mods_location)
	#	log.info(f"	Created folder {download_mods_location}")
	#
	#"""
	#CHECKING FOR UPDATE
	#"""
	#if check_for_updates: checkForGithubUpdate()
	#
	#"""UPDATING/DOWNLOADING MODS"""
	#log.info("PROCESSING LIST OF MODS:")
	#cache = {}
	#for instance_index, instance in enumerate(instances):
	#	instance_text = instance_index + 1
	#	try:
	#		loader = instance['loader'].lower()
	#		version = instance['version']
	#		mods_directory = f"{instance['directory']}/mods"
	#		links = instance['mod_links']
	#	except Exception as e:
	#		log.warnExit(f"	[WARN] Instance {instance_text} is missing the key: {repr(e)}")
	#
	#	#for dir in [mods_directory, resource_packs_directory, shaderpacks_directory]:
	#	#	if not os.path.exists(dir):
	#	#		log.warn(f"	[WARN]: Could not find dir \"{dir}\".")
	#
	#	if not os.path.exists(f"{download_mods_location}/{loader}/{version}"):
	#		try:
	#			os.makedirs(f"{download_mods_location}/{loader}/{version}")
	#			log.info(f"	Created folder {download_mods_location}/{loader}/{version}")
	#		except Exception as e:
	#			log.warn(f"	[WARN] Could not create {download_mods_location}/{loader}/{version}. {repr(e)}")
	#
	#	if loader  == "fabric":
	#		curseforge_modLoaderType = 4
	#		log.info(f"	Processing {version} mods in {mods_directory}...")
	#
	#		for link in links:
	#			try:
	#				if link[-1]  == "/": link = link[:-1] #Remove trailing / from link sif it has one at the end
	#			except: pass
	#
	#			if link[0:45]  == "https://www.curseforge.com/minecraft/mc-mods/":
	#				if link[45:len(link)] != "":
	#					slug = link[45:len(link)]
	#					if not any(x in slug for x in ["/", " ", "\\"]):
	#						log.info(f"		Processing: {slug}")
	#
	#						if link not in cache or version not in cache[link]['versions']:
	#							#log.info(f"			Caching {slug} for {version}...")
	#
	#							try:
	#								curseforge_mod = requests.get("https://api.curseforge.com/v1/mods/search", params = {"gameId": "432","slug": slug, "classId": "6"}, headers = headers).json()["data"]
	#								if len(curseforge_mod) > 0:
	#									curseforge_id = curseforge_mod[0]["id"]
	#
	#									curseforge_files = requests.get(f"https://api.curseforge.com/v1/mods/{curseforge_id}/files", params = {"gameVersion": version, "modLoaderType": curseforge_modLoaderType}, headers = headers).json()["data"]
	#									if len(curseforge_files) > 0:
	#										curseforge_files = list(file for file in curseforge_files if version in file["gameVersions"])
	#
	#										latest_curseforge_file = curseforge_files[0]
	#										file_name = latest_curseforge_file["fileName"]
	#										download_url = latest_curseforge_file["downloadUrl"]
	#										if download_url  == None:
	#											download_url = f"https://edge.forgecdn.net/files/{str(latest_curseforge_file['id'])[0:4]}/{str(latest_curseforge_file['id'])[4:7]}/{file_name}"
	#											pass
	#
	#										if not os.path.exists(f"{download_mods_location}/{loader}/{version}/{file_name}"):
	#											try:
	#												open(f"{download_mods_location}/{loader}/{version}/{file_name}", "wb").write(requests.get(download_url).content)
	#												log.info(f"			Downloaded {file_name} to {download_mods_location}/{loader}/{version}")
	#											except Exception as e:
	#												log.info(f"			[WARN] Could not download file. {repr(e)}")
	#
	#										cache[link] = {"versions": {}}
	#										cache[link]["versions"][version] = f"{download_mods_location}/{loader}/{version}/{file_name}"
	#
	#									else: log.info(f"			[WARN] Cannot find any {version} compatable versions of this mod.")
	#
	#								else:
	#									log.info(f"		[WARN] Could not find mod {slug}. Make sure the url {link} is valid and not a redirect!")
	#							except Exception as e:
	#								log.info(f"			[WARN] Cannot access the CurseForge API.")
	#
	#						if link in cache:
	#							if not os.path.exists(f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}"):
	#								try:
	#									shutil.copyfile(cache[link]["versions"][version], f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}")
	#									log.info(f"			Copied \"{cache[link]['versions'][version]}\" into \"{mods_directory}\"")
	#								except Exception as e:
	#									log.info(f"			[WARN] Something went wrong copying \"{cache[link]['versions'][version]}\" into \"{mods_directory}\". {repr(e)}")
	#							else: log.info(f"			{slug} is already up to date.")
	#
	#					else: log.info(f'		[WARN] Invlalid slug: "{slug}"')
	#
	#				else: log.warn(f"	[WARN] Links must be to a mod page. {link} is not a valid mod page link.")
	#
	#			elif link[0:25]  == "https://modrinth.com/mod/":
	#				if link[25:len(link)] != "":
	#					slug = link[25:len(link)]
	#					if not any(x in slug for x in ["/", " ", "\\"]):
	#						log.info(f"		Processing: {slug}")
	#
	#						if link not in cache or version not in cache[link]['versions']:
	#							#log.info(f"			Caching {slug} for {version}...")
	#
	#							try:
	#								modrinth_versions = requests.get(f'https://api.modrinth.com/v2/project/{slug}/version?game_versions = ["{version}"]&loaders = ["{loader}"]').json()
	#								if len(modrinth_versions) > 0:
	#									latest_modrinth_version = modrinth_versions[0]
	#									files = latest_modrinth_version["files"]
	#
	#									if any(file["primary"] for file in files):
	#										files = [file for file in files if file["primary"]  == True]
	#
	#									file_name = files[0]['filename']
	#									download_url = files[0]['url']
	#
	#									if not os.path.exists(f'{download_mods_location}/{loader}/{version}/{file_name}'):
	#										try:
	#											open(f"{download_mods_location}/{loader}/{version}/{file_name}", "wb").write(requests.get(download_url).content)
	#											log.info(f"			Downloaded {file_name} to {download_mods_location}/{loader}/{version}")
	#										except Exception as e:
	#											log.info(f"			[WARN] Could not download file. {repr(e)}")
	#
	#									cache[link] = {"versions": {}}
	#									cache[link]["versions"][version] = f"{download_mods_location}/{loader}/{version}/{file_name}"
	#
	#								else: log.info(f"			[WARN] Cannot find any {version} compatable versions of this mod.")
	#							except Exception as e:
	#								log.info(f"			[WARN] Cannot access the Modrinth API.")
	#
	#						if link in cache:
	#							if not os.path.exists(f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}"):
	#								try:
	#									shutil.copyfile(cache[link]["versions"][version], f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}")
	#									log.info(f"			Copied \"{cache[link]['versions'][version]}\" into \"{mods_directory}\"")
	#								except Exception as e:
	#									log.info(f"			[WARN] Something went wrong copying \"{cache[link]['versions'][version]}\" into \"{mods_directory}\". {repr(e)}")
	#							else: log.info(f"			{slug} is already up to date.")
	#
	#					else: log.info(f'		[WARN] Invlalid slug: "{slug}"')
	#
	#				else: log.warn(f"	[WARN] Links must be to a mod page. {link} is not a valid mod page link.")
	#
	#	elif loader  == "forge":
	#		curseforge_modLoaderType = 1
	#		log.warn(f"	[WARN] Script does not currently support {loader} mods yet. Ignoring instance {instance_text}.")
	#
	#	else:
	#		log.warn(f"	[WARN] Script does not support {loader} mods. Ignoring instance {instance_text}. Suggest support via github under the issue tracker https://github.com/RandomGgames/MMUD")
	#
	#"""DELETE OLD MODS"""
	#log.info("DELETING OLD MODS")
	#
	#directories = []
	#for instance in instances:
	#	mods_directory = f"{instance['directory']}/mods"
	#	version = instance['version']
	#	loader = instance['loader'].lower()
	#
	#	if loader  == "fabric":
	#		if f"{config['download_mods_location']}/{loader}/{version}" not in directories:
	#			directories.append(f"{config['download_mods_location']}/{loader}/{version}")
	#		if mods_directory not in directories:
	#			directories.append(mods_directory)
	#
	#	elif loader  == "forge": log.warn(f"	[WARN] Loader does not support {loader} yet.")
	#
	#	else: log.warn(f"	[WARN] Loader does not support {loader}.")
	#
	#for directory in directories:
	#	log.info(f"	Scanning {directory}...")
	#	cache = {}
	#	if os.path.exists(directory):
	#		for mod in [file for file in os.listdir(directory) if file.endswith(".jar")]:
	#			path = f"{directory}/{mod}"
	#			tmodified = os.path.getmtime(path)
	#			try:
	#				with ZipFile(path, "r") as modzip:
	#					try:
	#						with modzip.open("fabric.mod.json", "r") as modinfo:
	#							mod_id = json.load(modinfo, strict = False)["id"]
	#					except Exception as e:
	#						log.info(f"		[WARN] Could not read the fabric.mod.json file within {path}")
	#					modinfo.close()
	#				modzip.close()
	#				if mod_id not in cache:
	#					cache[mod_id] = {'path': path, 'tmodified': tmodified}
	#				else:
	#					if tmodified > cache[mod_id]['tmodified']:
	#						os.remove(cache[mod_id]['path'])
	#						log.info(f"		Deleted {os.path.basename(cache[mod_id]['path'])}")
	#						cache[mod_id] = {'path': path, 'tmodified': tmodified}
	#					else:
	#						os.remove(path)
	#						log.info(f"		Deleted {os.path.basename(path)}")
	#			except Exception as e:
	#				log.warn(f"	[WARN] An error occured while scanning {path}. {repr(e)}")
	#
	#	else: log.info(f"		[WARN] Could not find {directory}.")
	#
	#log.info("DONE\n")
	#print("RMMUD will close in 10 seconds...")
	#time.sleep(10)
	#exit()

if __name__  == "__main__":
	main()
