from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import platform

class RtAudioConan(ConanFile):
    name = 'rtaudio'

    source_version = '4.1.2'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.music.mcgill.ca/~gary/rtaudio/'
    license = 'http://www.music.mcgill.ca/~gary/rtaudio/license.html'
    description = 'A cross-platform library for realtime audio input/output'
    source_dir = 'rtaudio-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    exports_sources = '*.patch'

    def source(self):
        tools.get('http://www.music.mcgill.ca/~gary/rtaudio/release/rtaudio-%s.tar.gz' % self.source_version,
                  sha256='294d044da313a430c44d311175a4f51c15d56d87ecf72ad9c236f57772ecffb8')

        tools.patch(patch_file='modeluid.patch', base_path=self.source_dir)

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = []

            autotools.cxx_flags.append('-Oz')
            autotools.cxx_flags.append('-DUNICODE')

            if platform.system() == 'Darwin':
                autotools.cxx_flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-headerpad_max_install_names')
                autotools.link_flags.append('-Wl,-install_name,@rpath/librtaudio.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
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

    def package(self):
        self.copy('*.h', src='%s/include/rtaudio' % self.install_dir, dst='include/RtAudio')
        self.copy('librtaudio.dylib', src='%s/lib' % self.install_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['rtaudio']
