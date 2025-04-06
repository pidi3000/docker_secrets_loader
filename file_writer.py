

from pathlib import Path

import config
from password_manager_handlers import PM_Entry_Base, PM_Field_Base


class Base_File_Writer:

    OUTPUT_FILE_PATH: Path

    def __init__(self, file_path: Path | str):
        self.OUTPUT_FILE_PATH = Path(file_path)

    def format_section(self, entry: PM_Entry_Base) -> str:
        response = ""
        response += f"\n"
        response += f"{'#'*100}\n"
        response += f"# {entry.service_prefix}\n"
        response += f"{'#'*100}\n"

        return response

    def format_field(self, field: PM_Field_Base) -> str:
        response = ""
        response += f"{field.slug}={field.field_value}"
        return response

    def write_all_entry_fields(self, all_entries: list[PM_Entry_Base]):
        print(f"Writing with {'<' + self.__class__.__name__ + '>': <26} to: `{self.OUTPUT_FILE_PATH}`")

        try:

            self.OUTPUT_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(self.OUTPUT_FILE_PATH, "w") as f:
                for entry in all_entries:
                    previous_field: PM_Field_Base = None

                    for field in entry.pm_fileds:
                        if previous_field is None or field.service_prefix != previous_field.service_prefix:
                            f.write(self.format_section(entry=entry))

                        f.write(self.format_field(field=field))

                        f.write("\n")
                        previous_field = field

        except Exception as e:
            print(f"\nFailed to write to file: {self.OUTPUT_FILE_PATH}")
            print(e)

    def __repr__(self):
        return (f"<{self.__class__.__name__}>("
                f"pm_field_id='{self.OUTPUT_FILE_PATH}')")


class System_Secrets_Writer(Base_File_Writer):
    """
    Write the secrets to be loaded as env vars by the system
    adds `export ` before the filed and value
    """

    def format_field(self, field: PM_Field_Base) -> str:
        return f"export {field.slug}={field.field_value}"


class Template_Secrets_Writer(Base_File_Writer):
    """
    Write the fileds without any values
    """

    def format_field(self, field: PM_Field_Base) -> str:
        return f"{field.slug}="


def get_all_file_writers() -> list[Base_File_Writer]:
    all_file_writers = []

    def _get_file_writers(input, file_writer_class: Base_File_Writer):
        if input is None:
            return []
        elif isinstance(input, str):
            input: str
            if len(input.strip()) < 2:
                return []
            return [file_writer_class(input)]
        elif isinstance(input, list):
            writers = []
            for path in input:
                writers.extend(_get_file_writers(path, file_writer_class))
            return writers

        return []

    all_file_writers.extend(_get_file_writers(
        config.OUTPUT_FILE_SECRETS, Base_File_Writer))
    all_file_writers.extend(_get_file_writers(
        config.OUTPUT_FILE_SYSTEM, System_Secrets_Writer))
    all_file_writers.extend(_get_file_writers(
        config.OUTPUT_FILE_TEMPLATE, Template_Secrets_Writer))

    # config.OUTPUT_FILE_SECRETS = ""
    # config.OUTPUT_FILE_SYSTEM = ""
    # config.OUTPUT_FILE_TEMPLATE = ""
    
    all_file_writers = [item for item in all_file_writers if item is not None]


    return all_file_writers
