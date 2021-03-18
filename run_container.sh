#!/usr/bin/env bash

if [[ "$(docker images -q autotier-exporter 2> /dev/null)" == "" ]]; then
	docker build -t autotier-exporter .
	res=$?
	if [ $res -ne 0 ]; then
		echo "Building docker image failed."
		exit $res
	fi
fi

docker run \
	-v /opt/45drives/autotier:/opt/45drives/autotier \
	-v /var/lib/autotier:/var/lib/autotier \
	-v /etc/autotier.conf:/etc/autotier.conf \
	--net=host --rm \
	autotier-exporter -p 9450
