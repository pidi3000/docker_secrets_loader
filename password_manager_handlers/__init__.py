
import os
from pathlib import Path

import config


class PM_Field_Base:
    # pm_entry_id: str
    pm_field_id: str
    pm_field_type: str

    service_prefix: str

    field_name: str
    field_value: str
    field_slug: str

    def __init__(self,
                 #  pm_entry_id: str,
                 pm_field_id: str,
                 pm_field_type: str,

                 service_prefix: str,

                 field_name: str,
                 field_value: str
                 ):

        # self.pm_entry_id = pm_entry_id
        self.pm_field_id = pm_field_id
        self.pm_field_type = pm_field_type

        self.service_prefix = service_prefix

        self.field_name = field_name
        self.field_value = field_value

    @property
    def slug(self) -> str:
        return f"{config.GLOBAL_SLUG_PREFIX}__{self.service_prefix}__{self.field_name}"

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"pm_field_id='{self.pm_field_id}', "
                f"pm_field_type='{self.pm_field_type}', "
                f"service_prefix='{self.service_prefix}', "
                f"field_name='{self.field_name}', "
                f"field_value='{self.field_value}', "
                f"slug='{self.slug}')")


class PM_Entry_Base:
    service_name: str
    service_prefix: str

    pm_entry_id: str
    pm_vault_id: str

    pm_fileds: list[PM_Field_Base] = []

    def __init__(self,
                 service_name: str,
                 service_prefix: str,
                 pm_entry_id: str,
                 ):

        self.service_name = service_name
        self.service_prefix = service_prefix

        self.pm_entry_id = pm_entry_id

    def __repr__(self) -> str:
        fields_repr = ',\n    '.join(repr(field) for field in self.pm_fileds)
        return (f"{self.__class__.__name__}(\n"
                f"  service_name='{self.service_name}',\n"
                f"  service_prefix='{self.service_prefix}',\n"
                f"  pm_entry_id='{self.pm_entry_id}',\n"
                f"  pm_fileds=[\n    {fields_repr}\n  ]\n)")

class Password_Manager_handler_base:

    @classmethod
    def load_auth_token(cls) -> str:
        _access_token = None
        if "PM_ACCESS_TOKEN" in os.environ:
            _access_token = os.environ.get("PM_ACCESS_TOKEN")
            return _access_token

        else:
            access_token_file = config.PM_ACCESS_TOKEN_FILE
            # if access_token_file is not None:
            if Path(access_token_file).exists():
                with open(access_token_file, "r") as tf:
                    _access_token = tf.read().strip()

                return _access_token

            else:
                raise FileNotFoundError(
                    f"token file path does not exist: {access_token_file}")

        raise ValueError(f"coud not load access token")

    def get_all_entry_ids(self) -> dict[str, str]:
        raise NotImplementedError

    def get_all_entries(self) -> list[PM_Entry_Base]:
        raise NotImplementedError

    def get_entry(self, entry_id: str) -> PM_Entry_Base:
        raise NotImplementedError

    def _get_entry_details(self, entry_id: str) -> any:
        """ Get an entries raw details as given by the PM
        only meant to be used by the same PM_handler class
        to create a `PM_Entry` and it's `PM_Field`

        Parameters
        ----------
        entry_id : str
            used to identefy an entry in the Password Manager

        Returns
        -------
        any
            raw data from the Password Manager API

        """
        raise NotImplementedError

    def set_field_slug(self, pm_entry: PM_Entry_Base, pm_field: PM_Field_Base):
        raise NotImplementedError

    def set_all_field_slugs(self, pm_entry: PM_Entry_Base):
        # raise NotImplementedError
        for field in pm_entry.pm_fileds:
            self.set_field_slug(pm_entry=pm_entry,  pm_field=field)


def get_PM_handler(pm_handler_name) -> Password_Manager_handler_base:

    if pm_handler_name in ["1password", "onepassword"]:
        from password_manager_handlers.onepassword import onepassword_handler
        return onepassword_handler()

    # elif pm_handler_name is "bitwarden":
        # return

    else:
        raise ValueError(
            f"No matching password manager handler found for `{pm_handler_name}`")
    # match pm_handler_name:
    #     case "":
