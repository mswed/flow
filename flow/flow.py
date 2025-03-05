import sgtk
import os


class Flow(object):
    """
    An object representing the SG connection
    """

    @classmethod
    def connect(cls, script_key=None, user=False, path=None):
        """
        Create a connection to Shotgrid

        @param script_key: str, name of key (e.g. Nuke, Maya, etc)
        @param user: bool, should we connect as the current desktop user?
        @param path: str, path to get the toolkit instance from
        @return: A configured Flow instance
        """

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
                    print("Please provide a script key!")
                else:
                    key = f"SCRIPT_KEY_{script_key.upper()}"
                    sa = sgtk.authentication.ShotgunAuthenticator()
                    sg_user = sa.create_script_user(
                        api_script=key, api_key=os.environ.get(key)
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
