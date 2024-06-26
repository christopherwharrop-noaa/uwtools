"""
A driver for sfc_climo_gen.
"""

from pathlib import Path
from typing import Optional

from iotaa import asset, task, tasks

from uwtools.config.formats.nml import NMLConfig
from uwtools.drivers.driver import Driver
from uwtools.strings import STR
from uwtools.utils.tasks import file


class SfcClimoGen(Driver):
    """
    A driver for sfc_climo_gen.
    """

    def __init__(self, config: Optional[Path] = None, dry_run: bool = False, batch: bool = False):
        """
        The driver.

        :param config: Path to config file (read stdin if missing or None).
        :param dry_run: Run in dry-run mode?
        :param batch: Run component via the batch system?
        """
        super().__init__(config=config, dry_run=dry_run, batch=batch)

    # Workflow tasks

    @task
    def namelist_file(self):
        """
        The namelist file.
        """
        fn = "fort.41"
        yield self._taskname(f"namelist file {fn}")
        path = self._rundir / fn
        yield asset(path, path.is_file)
        vals = self._driver_config["namelist"]["update_values"]["config"]
        input_paths = [Path(v) for k, v in vals.items() if k.startswith("input_")]
        input_paths += [Path(vals["mosaic_file_mdl"])]
        input_paths += [Path(vals["orog_dir_mdl"]) / fn for fn in vals["orog_files_mdl"]]
        yield [file(input_path) for input_path in input_paths]
        self._create_user_updated_config(
            config_class=NMLConfig,
            config_values=self._driver_config["namelist"],
            path=path,
        )

    @tasks
    def provisioned_run_directory(self):
        """
        Run directory provisioned with all required content.
        """
        yield self._taskname("provisioned run directory")
        yield [
            self.namelist_file(),
            self.runscript(),
        ]

    @task
    def runscript(self):
        """
        The runscript.
        """
        path = self._runscript_path
        yield self._taskname(path.name)
        yield asset(path, path.is_file)
        yield None
        self._write_runscript(path=path, envvars={})

    # Private helper methods

    @property
    def _driver_name(self) -> str:
        """
        Returns the name of this driver.
        """
        return STR.sfcclimogen
