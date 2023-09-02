# Copyright (C) 2017 Lukasz Bacik <mail@luka.sh>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import argparse
from docker_image_builder import docker_image_builder


def parse():

	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog='''
            source: https://github.com/lbacik/docker-image-builder
            -- 2017 Lukasz Bacik <mail@luka.sh>
        '''
	)
	parser.add_argument(
		'--version',
		action='version',
		help='print version and exit',
		version=docker_image_builder.VERSION
	)
	parser.add_argument(
		'-H',
		'--docker-host',
		help='URL to the Docker daemon (the same as `docker -H ...`)',
		default='unix://var/run/docker.sock'
	)
	parser.add_argument(
		'--tls',
		help='enable TLS (in communication with Docker daemon)',
		action='store_true'
	)
	parser.add_argument(
		'-p',
		'--images-name-prefix',
		help='''
            the default build name is created as {PREFIX}{BUILD_NUMBER} where the BUILD_NUMBER is added
            automatically (each Dockerfile provided as a parameter will be processed as separate build).
        ''',
		default='build-'
	)
	parser.add_argument(
		'-i',
		'--final-image-name',
		help='''
            optional name or name:tag - if provided, it will be used as a name[:tag] of the last build
            (beyond the default name: {PREFIX}{BUILD_NUMBER}).
        '''
	)
	parser.add_argument(
		'-r',
		'--remove-builds',
		help='''
            actually: remove all DEFAULT builds. This option has no sense without setting "final-image-name"
            since it requests to delete all {PREFIX}{BUILD_NUMBER} builds (see "images-name-prefix" option
            above) after successfully build last image.
        ''',
		action='store_true'
	)

	parser.add_argument(
		'params',
		help='context_path [ARG:foo=bar ...]',
		nargs='*'
	)

	args = parser.parse_args()

	return args


def parse_positional_args(positional_args):
	"""
	[TODO] really? It's so complicated?..
	"""

	contexts = []
	contexts_args = []
	build_args = {}

	context_args = {}

	for i in positional_args:
		if i.startswith('ARG:'):
			arg = i.replace('ARG:', '')
			build_args.update([arg.split('=', 1)])
		else:
			docker_build = {}
			context_args = {}
			docker_build['context'] = i
			if positional_args.index(i) > 0:
				context_args['args'] = build_args
				build_args = {}
				contexts_args.append(context_args)
			contexts.append(docker_build)

	if len(build_args) > 0:
		context_args = {}
		context_args['args'] = build_args
		contexts_args.append(context_args)

	i = 0
	for item in contexts:
		if i < len(contexts_args):
			item.update(contexts_args[i])
		else:
			item.update({'args': {}})
		i += 1

	return contexts
