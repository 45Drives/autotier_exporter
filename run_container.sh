#!/usr/bin/env bash

docker run \
	-v /opt/45drives/autotier:/opt/45drives/autotier \
	-v /var/lib/autotier:/var/lib/autotier \
	-v /etc/autotier.conf:/etc/autotier.conf \
	--net=host --rm \
	45drives/autotier_exporter -p 9450
