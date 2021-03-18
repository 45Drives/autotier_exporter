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
			sys.exit(1)
		if child.wait() != 0:
			print("Error: autotier exited with code {}".format(child.returncode))
			sys.exit(child.returncode)
		return json.loads(child.stdout.read())

class AutotierCollector(object):
	def __init__(self):
		pass
	
	def collect(self):
		status = get_status()
		usage_gauge = GaugeMetricFamily("tier_usage_bytes", 'Usage of tier in bytes', labels=['name', 'number'])
		capacity_gauge = GaugeMetricFamily("tier_capacity_bytes", 'Capacity of tier in bytes', labels=['name', 'number'])
		quota_gauge = GaugeMetricFamily("tier_quota_bytes", 'Quota of tier in bytes', labels=['name', 'number'])
		for i in range(len(status["tiers"])):
			tier = status["tiers"][i]
			usage_gauge.add_metric([tier["name"], str(i)], tier["usage"])
			capacity_gauge.add_metric([tier["name"], str(i)], tier["capacity"])
			quota_gauge.add_metric([tier["name"], str(i)], tier["quota"])
		yield usage_gauge
		yield capacity_gauge
		yield quota_gauge

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

