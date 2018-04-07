from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import platform

class RtAudioConan(ConanFile):
    name = 'rtaudio'

    source_version = '4.1.2'
    package_version = '3'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable', \
               'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.music.mcgill.ca/~gary/rtaudio/'
    license = 'http://www.music.mcgill.ca/~gary/rtaudio/license.html'
    description = 'A cross-platform library for realtime audio input/output'
    source_dir = 'rtaudio-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    exports_sources = '*.patch'
    libs = {
        'rtaudio': 5,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.music.mcgill.ca/~gary/rtaudio/release/rtaudio-%s.tar.gz' % self.source_version,
                  sha256='294d044da313a430c44d311175a4f51c15d56d87ecf72ad9c236f57772ecffb8')

        tools.patch(patch_file='modeluid.patch', base_path=self.source_dir)

        self.run('mv %s/readme %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = ['c++abi']

            autotools.flags.append('-Oz')
            autotools.flags.append('-DUNICODE')

            autotools.cxx_flags.append('-lc++abi')

            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++ -stdlib=libc++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=['--quiet',
                                          '--enable-static',
                                          '--enable-shared',
                                          '--prefix=%s/../%s' % (os.getcwd(), self.install_dir)])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

        with tools.chdir('%s/lib' % self.install_dir):
            if platform.system() == 'Darwin':
                self.run('install_name_tool -change @rpath/libc++.dylib /usr/lib/libc++.1.dylib librtaudio.dylib')
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include/rtaudio' % self.install_dir, dst='include/RtAudio')
        self.copy('librtaudio.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['rtaudio']
