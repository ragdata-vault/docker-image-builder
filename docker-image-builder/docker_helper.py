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

import docker
import tarfile
import tempfile
from dockerfile_parse import DockerfileParser


def create_context_archive(context, docker_file, base_image):

	original_dockerfile = open(context + '/' + docker_file, 'r')
	dfp = DockerfileParser()
	dfp.lines = original_dockerfile.readlines()
	original_dockerfile.close()

	dfp.baseimage = base_image

	new_file = tempfile.NamedTemporaryFile()
	new_file.write(dfp.content.encode('utf-8'))
	new_file.flush()

	context_archive = docker.utils.tar(context, dockerfile=docker_file)

	t = tarfile.open(name=context_archive.name, mode='a')
	t.add(new_file.name, arcname=docker_file)
	t.close()

	return context_archive


def build(contexts, build_prefix, docker_file, client):
	i = 0
	last_build = ''
	builds = []
	for item in contexts:

		context = item['context']
		args = item['args']

		context_path = None
		context_archive = None
		custom_context = False

		if i > 0:
			custom_context = True
			context_archive = create_context_archive(context, docker_file, last_build)
		else:
			context_path = context

		last_build = '%s%d' % (build_prefix, i)
		print('*** BUILD: %s' % (last_build,))
		print(args)

		for line in client.api.build(
			path=context_path,
			fileobj=context_archive,
			custom_context=custom_context,
			dockerfile=docker_file,
			tag=last_build,
			decode=True,
			rm=True,
			buildargs=args
		):
			try:
				print('%s' % line['stream'].encode().decode('ascii', 'ignore').rstrip())
			except KeyError:
				''' key "stream" doesn't exist - nothing to print '''
				''' [TODO] it is bad practice '''
				pass

		builds.append(last_build)
		i += 1

	return builds
