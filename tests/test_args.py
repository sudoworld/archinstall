from pathlib import Path

from pytest import MonkeyPatch

from archinstall.default_profiles.profile import GreeterType
from archinstall.lib.args import ArchConfig, ArchConfigHandler, Arguments
from archinstall.lib.hardware import GfxDriver
from archinstall.lib.mirrors import MirrorConfiguration, MirrorRegion
from archinstall.lib.models import Audio, AudioConfiguration, Bootloader, DiskLayoutConfiguration, DiskLayoutType, NetworkConfiguration, User
from archinstall.lib.models.locale import LocaleConfiguration
from archinstall.lib.models.network_configuration import Nic, NicType
from archinstall.lib.models.profile_model import ProfileConfiguration
from archinstall.lib.profile.profiles_handler import profile_handler
from archinstall.lib.translationhandler import translation_handler


def test_default_args(monkeypatch: MonkeyPatch) -> None:
	monkeypatch.setattr('sys.argv', ['archinstall'])
	handler = ArchConfigHandler()
	args = handler.args
	assert args == Arguments(
		config=None,
		config_url=None,
		creds=None,
		silent=False,
		dry_run=False,
		script='guided',
		mountpoint=Path('/mnt'),
		skip_ntp=False,
		debug=False,
		offline=False,
		no_pkg_lookups=False,
		plugin=None,
		skip_version_check=False,
		advanced=False
	)


def test_correct_parsing_args(
	monkeypatch: MonkeyPatch,
	config_fixture: Path,
	creds_fixture: Path
) -> None:
	monkeypatch.setattr('sys.argv', [
		'archinstall',
		'--config',
		str(config_fixture),
		'--config-url',
		'https://example.com',
		'--creds',
		str(creds_fixture),
		'--script',
		'execution_script',
		'--mount-point',
		'/tmp',
		'--skip-ntp',
		'--debug',
		'--offline',
		'--no-pkg-lookups',
		'--plugin',
		'pytest_plugin.py',
		'--skip-version-check',
		'--advanced',
		'--dry-run',
		'--silent'
	])

	handler = ArchConfigHandler()
	args = handler.args

	assert args == Arguments(
		config=config_fixture,
		config_url='https://example.com',
		creds=creds_fixture,
		silent=True,
		dry_run=True,
		script='execution_script',
		mountpoint=Path('/mnt'),
		skip_ntp=True,
		debug=True,
		offline=True,
		no_pkg_lookups=True,
		plugin='pytest_plugin.py',
		skip_version_check=True,
		advanced=True
	)


def test_config_file_parsing(
	monkeypatch: MonkeyPatch,
	config_fixture: Path,
	creds_fixture: Path
) -> None:
	monkeypatch.setattr('sys.argv', [
		'archinstall',
		'--config',
		str(config_fixture),
		'--creds',
		str(creds_fixture),
	])

	handler = ArchConfigHandler()
	arch_config = handler.config

	# TODO: Use the real values from the test fixture instead of clearing out the entries
	arch_config.disk_config.device_modifications = []  # type: ignore[union-attr]

	assert arch_config == ArchConfig(
		version='3.0.2',
		locale_config=LocaleConfiguration(
			kb_layout='us',
			sys_lang='en_US',
			sys_enc='UTF-8'
		),
		archinstall_language=translation_handler.get_language_by_abbr('en'),
		disk_config=DiskLayoutConfiguration(
			config_type=DiskLayoutType.Default,
			device_modifications=[],
			lvm_config=None,
			mountpoint=None
		),
		profile_config=ProfileConfiguration(
			profile=profile_handler.parse_profile_config({
				"custom_settings": {
					"Hyprland": {
						"seat_access": "polkit"
					},
					"Sway": {
						"seat_access": "seatd"
					}
				},
				"details": [
					"Sway",
					"Hyprland"
				],
				"main": "Desktop"
			}),
			gfx_driver=GfxDriver.AllOpenSource,
			greeter=GreeterType.Lightdm
		),
		mirror_config=MirrorConfiguration(
			mirror_regions=[
				MirrorRegion(
					name='Australia',
					urls=['http://archlinux.mirror.digitalpacific.com.au/$repo/os/$arch']
				)
			],
			custom_mirrors=[]
		),
		network_config=NetworkConfiguration(
			type=NicType.MANUAL,
			nics=[
				Nic(
					iface='eno1',
					ip='192.168.1.15/24',
					dhcp=True,
					gateway='192.168.1.1',
					dns=[
						'192.168.1.1',
						'9.9.9.9'
					]
				)
			]
		),
		bootloader=Bootloader.Systemd,
		uki=False,
		audio_config=AudioConfiguration(Audio.PIPEWIRE),
		hostname='archy',
		kernels=['linux-zen'],
		ntp=True,
		packages=["firefox"],
		parallel_downloads=66,
		swap=False,
		timezone='UTC',
		additional_repositories=["testing"],
		users=[User(username='user_name', password='user_pwd', sudo=True)],
		disk_encryption=None,
		services=['service_1', 'service_2'],
		root_password='super_pwd',
		custom_commands=["echo 'Hello, World!'"]
	)
