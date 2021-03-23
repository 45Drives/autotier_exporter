import time
import json
import argparse
import subprocess
import sys
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

def get_status():
		try:
			child = subprocess.Popen(["/opt/45drives/autotier/autotier", "status", "--json"],
				stdout=subprocess.PIPE, universal_newlines=True)
		except OSError:
			print("Error executing autotier. Is it installed?")
			return (127, {})
		if child.wait() != 0:
			print("Error: autotier exited with code {}".format(child.returncode))
			return (child.returncode, {})
		return (child.returncode, json.loads(child.stdout.read()))

class AutotierCollector(object):
	def __init__(self):
		pass
	
	def collect(self):
		exit_code, status = get_status()
		autotier_status = GaugeMetricFamily("autotier_status", "State of filesystem", labels=['field'])
		if exit_code == 0:
			autotier_status.add_metric(['mounted'], 1)
			autotier_status.add_metric(['exit-code'], exit_code)
			tier_status = GaugeMetricFamily("tier_status", 'Usage, Capacity, and Quota of tiers', labels=['name', 'number', 'field'])
			for i in range(len(status["tiers"])):
				tier = status["tiers"][i]
				tier_status.add_metric([tier["name"], str(i), 'usage'], tier["usage"])
				tier_status.add_metric([tier["name"], str(i), 'capacity'], tier["capacity"])
				tier_status.add_metric([tier["name"], str(i), 'quota'], tier["quota"])
			yield tier_status
		else:
			autotier_status.add_metric(['mounted'], 0)
			autotier_status.add_metric(['exit_code'], exit_code)
		yield autotier_status

def parse_args():
	parser = argparse.ArgumentParser(description = 'Prometheus metrics exporter for autotier.')
	parser.add_argument('-p', '--port', required = True, help = 'Port for server')
	return parser.parse_args()

def main():
	try:
		args = parse_args()
		port = None
		try:
			port = int(args.port)
		except ValueError:
			print("Invalid port: ", args.port)
			sys.exit(1)
		if port > 65535 or port <= 1023:
			print("Invalid port range: ", args.port)
			sys.exit(1)
		print("Serving autotier metrics to {}".format(port))
		start_http_server(port)
		REGISTRY.register(AutotierCollector())
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print("Interrupted.")
		sys.exit(0)

if __name__ == "__main__":
	main()

