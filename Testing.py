import requests, json, time
from datetime import datetime

CHECK_FOR_UPDATES = True
VERSION = "3.3"

def download_latest_version():
	try:
		github_latest_version = requests.get("https://api.github.com/repos/RandomGgames/RMMUD/releases/latest").json()
		print(json.dumps(github_latest_version, indent = "\t"))
		#rmmud_download_url = github_latest_version["assets"]["browser_download_url"]
		#rmmud_file_name = github_latest_version["assets"]["name"]
		#open(rmmud_file_name, "wb").write(requests.get(rmmud_download_url).content).close()
		#with zipfile.ZipFile(rmmud_file_name, "r") as zip:
		#	zip.extractall().close()
	except Exception as e:
		print(f"	[WARN] Could not download latest version. {repr(e)}")

def main():
	"""CHECKING FOR LATEST RELEASE"""
	if CHECK_FOR_UPDATES:
		print("[INFO] CHECKING FOR SCRIPT UPDATES:")
		github_latest_version = requests.get("https://api.github.com/repos/RandomGgames/MMUD/releases/latest").json()
		if github_latest_version:
			github_version = str(github_latest_version['tag_name'])
		except Exception as e:
			if github_latest_version["message"][:23] == "API rate limit exceeded":
				r = requests.get("https://api.github.com/rate_limit").json()["resources"]["core"]["reset"]
				print(f"	[WARN] Could not retreive latest GitHub release version due to exceeding API limit. It wil reset in {round((r - datetime.now().timestamp())/60, 1)} minutes.")
			else:
				print(f"	[WARN] Could not retreive latest GitHub release version. {repr(e)}")
			exit()
		if github_version:
			try:
				current_version = VERSION
				if current_version == github_version:
					print(f"	You have the latest release!")
				elif len(current_version) > 3:
					if current_version[:3] <= github_version:
						print(f"	Your updater is out of date, running a developmental build! Please update to the latest release for the most recent features and fixes! {current_version} -> {github_version}. https://github.com/RandomGgames/MMUD/releases/latest")
					else:
						print(f"	Working on a new release ay? Good luck!")
				else:
					if current_version < github_version:
						print(f"	Your updater is out of date! Please update to the latest release for the most recent features and fixes! {current_version} -> {github_version}. https://github.com/RandomGgames/MMUD/releases/latest")
					else:
						print(f"	You updater is... more up to date than the latest release? {current_version} > {github_version}... How did you manage to do that...?")
			except:
				print(f"	Your updater is out of date! Please update to the latest release for the most recent features and fixes! {current_version} -> {github_version}. https://github.com/RandomGgames/MMUD/releases/latest")
		
if __name__ == "__main__":
	main()
