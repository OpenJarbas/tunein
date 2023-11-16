from setuptools import setup
import os


def get_requirements(requirements_filename: str):
    requirements_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  requirements_filename)
    with open(requirements_file, 'r', encoding='utf-8') as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip()
                    and not r.strip().startswith("#")]
    if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
        print('USING LOOSE REQUIREMENTS!')
        requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
    return requirements


def get_version():
    """ Find the version of this skill"""
    version_file = os.path.join(os.path.dirname(__file__), 'tunein', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="tunein",
    version=get_version(),
    description="TuneIn radio api",
    license='Apache-2.0',
    author="JarbasAi",
    url="https://github.com/OpenJarbas/tunein",
    packages=["tunein", "tunein/subcommands"],
    include_package_data=True,
    install_requires=get_requirements("requirements.txt"),
    keywords='TuneIn internet radio',
    entry_points={
    'console_scripts': [
        'tunein = tunein.cli:main',
    ],
},
)
