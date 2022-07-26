import time
from datetime import datetime
import json
import os
import requests
import shutil
from zipfile import ZipFile

CHECK_FOR_UPDATES = True
VERSION = "3.6WIP" #DO NOT CHANGE THIS YOURSELF!


run_time = datetime.now().strftime("%Y-%m-%d")
def log(text, end = "\n"):
	"""
	Prints text to the console and appends date, time, and text to a logs.txt file text. class str. The text to log
	"""
	if not os.path.exists("RMMUDLogs"): os.makedirs("RMMUDLogs")
	print(str(text), end = end)
	with open(f"RMMUDLogs/{run_time}.log", "a", encoding="UTF-8") as file: file.write(f"{str(text)}\n")
	with open(f"RMMUDLogs/latest.log", "a", encoding="UTF-8") as file: file.write(f"{str(text)}\n")


def logExit(text, end = "\n"):
	log(text, end = end)
	input("PRESS ANY KEY TO EXIT.")
	exit()


def checkForScriptUpdate():
	print("[INFO] CHECKING FOR SCRIPT UPDATES:")
	try:
		github_latest_version = requests.get("https://api.github.com/repos/RandomGgames/RMMUD/releases/latest").json()
		github_version = str(github_latest_version['tag_name'])
	except Exception as e:
		if github_latest_version["message"][:23] == "API rate limit exceeded":
			reset_time = round((requests.get("https://api.github.com/rate_limit").json()["resources"]["core"]["reset"] - datetime.now().timestamp()) / 60, 1)
			print(f"	[WARN] Could not retreive latest GitHub release version due to exceeding API limit. It wil reset in {reset_time} minutes. Canceling auto-update.")
		else:
			print(f"	[WARN] Could not retreive latest GitHub release version. Canceling auto-update. {repr(e)}")
		return

	if VERSION == github_version:
		print(f"	You have the latest release!")
	elif len(VERSION) > 3 and VERSION[:3] <= github_version:
		print(f"	Your updater is out of date ({VERSION} vs {github_version}). Updating now!")
		downloadLatestRelease(github_latest_version)
	elif len(VERSION) > 3 and not VERSION[:3] <= github_version:
		print(f"	Working on a new release ay? Good luck!")
	elif VERSION < github_version:
		print(f"	Your updater is out of date ({VERSION} vs {github_version}). Updating now!")
		downloadLatestRelease(github_latest_version)
	elif VERSION > github_version:
		print(f"	Your updater is... wait... says here that I am more up to date than the latest release? How did you manage to do that...? HOW??")


def downloadLatestRelease(github_data):
	rmmud_data = [asset for asset in github_data["assets"] if asset["name"] == "RMMUD.py"]
	try:
		rmmud_data[0]
	except:
		print(f"	[WARN] Error retreiving RMMUD.py asset from GitHub. Canceling auto-update.")
		return

	download_url = rmmud_data["browser_download_url"]
	file_name = rmmud_data["name"]

	print(f"	Downloading RMMUD.py...")
	try:
		open(file_name, "wb").write(requests.get(download_url).content).close()
		print(f"	[Info] Downloaded {file_name} V{github_data['tag_name']}")
		import RMMUD
		exit()
	except Exception as e:
		print(f"	[WARN] Error downloading RMMUD.py. Canceling auto-update. {repr(e)}")


def main():
	if os.path.exists("RMMUDLogs/latest.log"): open("RMMUDLogs/latest.log", "w").close() #Clears latest.log
	log(f"[{datetime.now()}] RUNNING RMMUD")

	"""
	LOAD CONFIG
	"""
	log("[INFO] LOADING CONFIG:")
	try:
		with open("RMMUDConfig.json") as f:
			config = json.load(f)
			download_mods_location = config["download_mods_location"]
			instances = config["instances"]
			check_for_updates = config["check_for_rmmud_updates"]
			headers = {"Accept": "application/json", "x-api-key": config["x-api-key"]}
			log("	Config read successfully.")
	except Exception as e:
		logExit(f"	[WARN] Could not read config file. Please fix the following error: {repr(e)}")

	if not os.path.exists(download_mods_location):
		os.makedirs(download_mods_location)
		log(f"	[INFO] Created folder {download_mods_location}")

	"""
	CHECKING FOR UPDATE
	"""
	if check_for_updates: checkForScriptUpdate()

	"""UPDATING/DOWNLOADING MODS"""
	log("[INFO] PROCESSING LIST OF MODS:")
	cache = {}
	for instance_index, instance in enumerate(instances):
		instance_text = instance_index + 1
		try:
			loader = instance['loader'].lower()
			version = instance['version']
			mods_directory = f"{instance['directory']}/mods"
			links = instance['mod_links']
		except Exception as e:
			logExit(f"	[WARN] Instance {instance_text} is missing the key: {repr(e)}")

		#for dir in [mods_directory, resource_packs_directory, shaderpacks_directory]:
		#	if not os.path.exists(dir):
		#		log(f"	[WARN]: Could not find dir \"{dir}\".")

		if not os.path.exists(f"{download_mods_location}/{loader}/{version}"):
			try:
				os.makedirs(f"{download_mods_location}/{loader}/{version}")
				log(f"	[INFO] Created folder {download_mods_location}/{loader}/{version}")
			except Exception as e:
				log(f"	[WARN] Could not create {download_mods_location}/{loader}/{version}. {repr(e)}")

		if loader == "fabric":
			curseforge_modLoaderType = 4
			log(f"	Processing {version} mods in {mods_directory}...")

			for link in links:
				try:
					if link[-1] == "/": link = link[:-1] #Remove trailing / from link sif it has one at the end
				except: pass

				if link[0:45] == "https://www.curseforge.com/minecraft/mc-mods/":
					if link[45:len(link)] != "":
						slug = link[45:len(link)]
						if not any(x in slug for x in ["/", " ", "\\"]):
							log(f"		Processing: {slug}")

							if link not in cache or version not in cache[link]['versions']:
								#log(f"			Caching {slug} for {version}...")

								try:
									curseforge_mod = requests.get("https://api.curseforge.com/v1/mods/search", params = {"gameId": "432","slug": slug, "classId": "6"}, headers = headers).json()["data"]
									if len(curseforge_mod) > 0:
										curseforge_id = curseforge_mod[0]["id"]

										curseforge_files = requests.get(f"https://api.curseforge.com/v1/mods/{curseforge_id}/files", params = {"gameVersion": version, "modLoaderType": curseforge_modLoaderType}, headers = headers).json()["data"]
										if len(curseforge_files) > 0:
											curseforge_files = list(file for file in curseforge_files if version in file["gameVersions"])

											latest_curseforge_file = curseforge_files[0]
											file_name = latest_curseforge_file["fileName"]
											download_url = latest_curseforge_file["downloadUrl"]
											if download_url == None:
												download_url = f"https://edge.forgecdn.net/files/{str(latest_curseforge_file['id'])[0:4]}/{str(latest_curseforge_file['id'])[4:7]}/{file_name}"
												pass

											if not os.path.exists(f"{download_mods_location}/{loader}/{version}/{file_name}"):
												try:
													open(f"{download_mods_location}/{loader}/{version}/{file_name}", "wb").write(requests.get(download_url).content)
													log(f"			[INFO] Downloaded {file_name} to {download_mods_location}/{loader}/{version}")
												except Exception as e:
													log(f"			[WARN] Could not download file. {repr(e)}")

											cache[link] = {"versions": {}}
											cache[link]["versions"][version] = f"{download_mods_location}/{loader}/{version}/{file_name}"

										else: log(f"			[WARN] Cannot find any {version} compatable versions of this mod.")

									else:
										log(f"		[WARN] Could not find mod {slug}. Make sure the url {link} is valid and not a redirect!")
								except Exception as e:
									log(f"			[WARN] Cannot access the CurseForge API.")

							if link in cache:
								if not os.path.exists(f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}"):
									try:
										shutil.copyfile(cache[link]["versions"][version], f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}")
										log(f"			[INFO] Copied \"{cache[link]['versions'][version]}\" into \"{mods_directory}\"")
									except Exception as e:
										log(f"			[WARN] Something went wrong copying \"{cache[link]['versions'][version]}\" into \"{mods_directory}\". {repr(e)}")
								else: log(f"			{slug} is already up to date.")

						else: log(f'		[WARN] Invlalid slug: "{slug}"')

					else:  log(f"	[WARN] Links must be to a mod page. {link} is not a valid mod page link.")

				elif link[0:25] == "https://modrinth.com/mod/":
					if link[25:len(link)] != "":
						slug = link[25:len(link)]
						if not any(x in slug for x in ["/", " ", "\\"]):
							log(f"		Processing: {slug}")

							if link not in cache or version not in cache[link]['versions']:
								#log(f"			Caching {slug} for {version}...")

								try:
									modrinth_versions = requests.get(f'https://api.modrinth.com/v2/project/{slug}/version?game_versions=["{version}"]&loaders=["{loader}"]').json()
									if len(modrinth_versions) > 0:
										latest_modrinth_version = modrinth_versions[0]
										files = latest_modrinth_version["files"]

										if any(file["primary"] for file in files):
											files = [file for file in files if file["primary"] == True]

										file_name = files[0]['filename']
										download_url = files[0]['url']

										if not os.path.exists(f'{download_mods_location}/{loader}/{version}/{file_name}'):
											try:
												open(f"{download_mods_location}/{loader}/{version}/{file_name}", "wb").write(requests.get(download_url).content)
												log(f"			[INFO] Downloaded {file_name} to {download_mods_location}/{loader}/{version}")
											except Exception as e:
												log(f"			[WARN] Could not download file. {repr(e)}")

										cache[link] = {"versions": {}}
										cache[link]["versions"][version] = f"{download_mods_location}/{loader}/{version}/{file_name}"

									else: log(f"			[WARN] Cannot find any {version} compatable versions of this mod.")
								except Exception as e:
									log(f"			[WARN] Cannot access the Modrinth API.")

							if link in cache:
								if not os.path.exists(f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}"):
									try:
										shutil.copyfile(cache[link]["versions"][version], f"{mods_directory}/{os.path.basename(cache[link]['versions'][version])}")
										log(f"			[INFO] Copied \"{cache[link]['versions'][version]}\" into \"{mods_directory}\"")
									except Exception as e:
										log(f"			[WARN] Something went wrong copying \"{cache[link]['versions'][version]}\" into \"{mods_directory}\". {repr(e)}")
								else: log(f"			{slug} is already up to date.")

						else: log(f'		[WARN] Invlalid slug: "{slug}"')

					else:  log(f"	[WARN] Links must be to a mod page. {link} is not a valid mod page link.")

		elif loader == "forge":
			curseforge_modLoaderType = 1
			log(f"	[WARN] Script does not currently support {loader} mods yet. Ignoring instance {instance_text}.")

		else:
			log(f"	[WARN] Script does not support {loader} mods. Ignoring instance {instance_text}. Suggest support via github under the issue tracker https://github.com/RandomGgames/MMUD")

	"""DELETE OLD MODS"""
	log("[INFO] DELETING OLD MODS")

	directories = []
	for instance in instances:
		mods_directory = f"{instance['directory']}/mods"
		version = instance['version']
		loader = instance['loader'].lower()

		if loader == "fabric":
			if f"{config['download_mods_location']}/{loader}/{version}" not in directories:
				directories.append(f"{config['download_mods_location']}/{loader}/{version}")
			if mods_directory not in directories:
				directories.append(mods_directory)

		elif loader == "forge": log(f"	[WARN] Loader does not support {loader} yet.")

		else: log(f"	[WARN] Loader does not support {loader}.")

	for directory in directories:
		log(f"	Scanning {directory}...")
		cache = {}
		if os.path.exists(directory):
			for mod in [file for file in os.listdir(directory) if file.endswith(".jar")]:
				path = f"{directory}/{mod}"
				tmodified = os.path.getmtime(path)
				try:
					with ZipFile(path, "r") as modzip:
						try:
							with modzip.open("fabric.mod.json", "r") as modinfo:
								mod_id = json.load(modinfo, strict=False)["id"]
						except Exception as e:
							log(f"		[WARN] Could not read the fabric.mod.json file within {path}")
						modinfo.close()
					modzip.close()
					if mod_id not in cache:
						cache[mod_id] = {'path': path, 'tmodified': tmodified}
					else:
						if tmodified > cache[mod_id]['tmodified']:
							os.remove(cache[mod_id]['path'])
							log(f"		[INFO] Deleted {os.path.basename(cache[mod_id]['path'])}")
							cache[mod_id] = {'path': path, 'tmodified': tmodified}
						else:
							os.remove(path)
							log(f"		[INFO] Deleted {os.path.basename(path)}")
				except Exception as e:
					log(f"	[WARN] An error occured while scanning {path}. {repr(e)}")

		else: log(f"		[WARN] Could not find {directory}.")

	log("DONE\n")
	print("RMMUD will close in 10 seconds...")
	time.sleep(10)
	exit()


if __name__ == "__main__":
	main()
