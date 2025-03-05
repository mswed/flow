import sgtk
import os
from pathlib import Path
from dotenv import load_dotenv


class Flow(object):
    """
    An object representing the SG connection
    """

    @classmethod
    def connect(
        cls, script_key=None, user=False, path=None, host=None, dotenv_path=None
    ):
        """
        Create a connection to Shotgrid

        @param script_key: str, name of key (e.g. Nuke, Maya, etc)
        @param user: bool, should we connect as the current desktop user?
        @param path: str, path to get the toolkit instance from
        @return: A configured Flow instance
        """

        if dotenv_path:
            print(f"Using specified dotenv path: {dotenv_path}")
            load_dotenv(dotenv_path)
        else:
            # Try to find .env file in current directory or any parent directory
            current_dir = Path.cwd()
            while current_dir != current_dir.parent:
                env_file = current_dir / ".env"
                if env_file.exists():
                    load_dotenv(env_file)
                    break
                current_dir = current_dir.parent

        flow = cls()

        # Assume we are in a DCC grab the engine
        flow.get_engine()

        if flow.engine is None:
            # We are not working with an engine. Try to get the user.
            sg_user = None
            if user:
                # we are connecting as a user
                sg_user = flow.get_user()

            else:
                # we are connecting as a script
                if script_key is None:
                    # ask for a key if we don't have one
                    raise ValueError(
                        "Script key is required when not connecting as a user. Please provide a valid script_key parameter."
                    )

                # Get the script name and key from the environment
                script_name_env_var = f"{script_key.upper()}_SCRIPT_NAME"
                script_key_env_var = f"{script_key.upper()}_SCRIPT_KEY"
                script_name = os.environ.get(script_name_env_var)
                api_key = os.environ.get(script_key_env_var)

                if not script_name:
                    raise ValueError(
                        f'Missing environment variable "{script_name_env_var}"'
                    )
                if not api_key:
                    raise ValueError(
                        f'Missing environment variable "{script_key_env_var}"'
                    )

                else:
                    sg_host = host or os.environ.get("SHOTGUN_HOST")
                    if not sg_host:
                        raise ValueError(
                            "Missing ShotGrid host URL. Please provide one via the 'host' parameter or set SHOTGUN_HOST environment variable"
                        )
                    sa = sgtk.authentication.ShotgunAuthenticator()
                    sg_user = sa.create_script_user(
                        api_script=script_name, api_key=api_key, host=sg_host
                    )

            # Authenticate as a user or script
            sgtk.set_authenticated_user(sg_user)
            flow.api = sg_user.create_sg_connection()

            if path is not None:
                flow.toolkit_from_path(path)

        return flow

    def __init__(self):
        self.api = None
        self.engine = None
        self.engine_info = None
        self.tk = sgtk

    def get_engine(self):
        """
        If we are in a DCC get the engine
        """
        self.engine = sgtk.platform.current_engine()
        # first try to get the connection from the engine
        if self.engine is not None:
            self.api = self.engine.shotgun
            self.tk = self.engine.sgtk
            self.engine_info = self.engine.get_metrics_properties()

    def get_user(self):
        """
        Get the user from SG Desktop
        """
        sa = sgtk.authentication.ShotgunAuthenticator()
        user = sa.get_user()
        return user

    def toolkit_from_path(self, path):
        """
        Get the toolkit from the provided path
        :param path: str, path inside the project
        """
        self.tk = sgtk.sgtk_from_path(path)

    def get_next_version_number(self, template_name, fields, skip_fields=["version"]):
        """
        Finds the next available version of a file using its SG template
        @param template_name: str, name of SG template
        @param fields: list(str), list of fields to apply to the template to build the path
        @param skip_fields: list(str), list of fields to ignore (defaults to 'version'
        @return: int, next available version of the file
        """
        template = self.tk.templates[template_name]

        # Get a list of existing file paths on disk that match the template and provided fields
        # Skip the version field as we want to find all versions, not a specific version.
        file_paths = self.tk.paths_from_template(
            template, fields, skip_fields, skip_missing_optional_keys=True
        )

        versions = []
        for a_file in file_paths:
            # extract the values from the path so we can read the version.
            path_fields = template.get_fields(a_file)
            versions.append(path_fields["version"])

        if not versions:
            versions = [0]
        # find the highest version in the list and add one.
        return max(versions) + 1
