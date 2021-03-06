#!/usr/bin/env python
# coding: utf-8
# Copyright 2013,2017 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import defusedxml.lxml
import os
import logging


class UpstreamDirectory(object):
    """ Describes structure of upstream directory

    >>> upstream = UpstreamDirectory("tests/fixtures/upstream-example")
    >>> upstream.UFO
    ['Font-Regular.ufo']
    >>> upstream.TTX
    ['Font-Light.ttx']
    >>> upstream.BIN
    ['Font-SemiBold.ttf']
    >>> upstream.METADATA
    ['METADATA.pb']
    >>> sorted(upstream.LICENSE)
    ['APACHE.txt', 'LICENSE.txt']
    >>> upstream.SFD
    ['Font-Bold.sfd']
    >>> sorted(upstream.TXT)
    ['APACHE.txt', 'LICENSE.txt']
    """

    OFL = ['open font license.markdown', 'ofl.txt', 'ofl.md']
    LICENSE = ['license.txt', 'license.md', 'copyright.txt']
    APACHE = ['apache.txt', 'apache.md']
    UFL = ['ufl.txt', 'ufl.md']

    ALL_LICENSES = OFL + LICENSE + APACHE + UFL

    def __init__(self, upstream_path):
        self.upstream_path = upstream_path

        self.UFO = []
        self.TTX = []
        self.BIN = []
        self.LICENSE = []
        self.METADATA = []
        self.SFD = []
        self.TXT = []

        self.walk()

    def get_ttx(self):
        return self.TTX

    def get_binaries(self):
        return self.BIN

    def get_fonts(self):
        return self.UFO + self.TTX + self.BIN + self.SFD
    ALL_FONTS = property(get_fonts)

    def walk(self):
        l = len(self.upstream_path)
        exclude = ['build_info', ]
        for root, dirs, files in os.walk(self.upstream_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                fullpath = os.path.join(root, f)

                if f[-4:].lower() == '.ttx':
                    try:
                        doc = defusedxml.lxml.parse(fullpath)
                        el = doc.xpath('//ttFont[@sfntVersion]')
                        if not el:
                            continue
                    except Exception as exc:
                        msg = 'Failed to parse "{}". Error: {}'
                        logging.error(msg.format(fullpath, exc))
                        continue
                    self.TTX.append(fullpath[l:].strip('/'))

                if os.path.basename(f).lower() == 'metadata.pb':
                    self.METADATA.append(fullpath[l:].strip('/'))

                if f[-4:].lower() in ['.ttf', '.otf']:
                    self.BIN.append(fullpath[l:].strip('/'))

                if f[-4:].lower() == '.sfd':
                    self.SFD.append(fullpath[l:].strip('/'))

                if f[-4:].lower() in ['.txt', '.markdown', '.md', '.LICENSE']:
                    self.TXT.append(fullpath[l:].strip('/'))

                if os.path.basename(f).lower()\
                   in UpstreamDirectory.ALL_LICENSES:
                    self.LICENSE.append(fullpath[l:].strip('/'))

            for d in dirs:
                fullpath = os.path.join(root, d)
                if os.path.splitext(fullpath)[1].lower() == '.ufo':
                    self.UFO.append(fullpath[l:].strip('/'))
