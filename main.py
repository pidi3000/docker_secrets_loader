####################################################################################################
# Load Service secrets from a Password Mangaer and:
# 1. write the secrets environment slug used to Password Mangaer (for easy copy, paste)
# 2. create secrets environment file, containing all secrets to load
#
# Each service has it's own Password Mangaer entry.
# A entry has multiple fields, each corresponding to 1 secret
# The fields name is used for the naming the secret variable and the field content as the sectret itself
#
# Every entry must have a field named "SERVICE PREFIX", this prefix is used for the secrets environment slug
#
####################################################################################################

import os
from pathlib import Path

import config
import file_writer
import password_manager_handlers
# import password_manager_handlers.onepassword

# ! must set PM_ACCESS_TOKEN env
# ? export OP_SERVICE_ACCOUNT_TOKEN=token
# ! or set config PM_ACCESS_TOKEN_FILE


def main():

    # get password manager handler using config value
    pm_handler = password_manager_handlers.get_PM_handler(config.PM_NAME)
    # pm_handler: password_manager_handlers.onepassword.onepassword_handler

    # get all file writers
    file_writers = file_writer.get_all_file_writers()
    # print(file_writers)
    
    all_entries = pm_handler.get_all_entries()
    
    # write all fields to the set file writers
    for writer in file_writers:
        writer.write_all_entry_fields(all_entries)
        
    # write var slugs to password manger if enabled
    if config.PM_WRITE_SLUGS or config.PM_WRITE_SLUGS_FORCE:
        # pm_handler.set_all_field_slugs(all_entries[1])
        for entry in all_entries:
            pm_handler.set_all_field_slugs(entry)


if __name__ == "__main__":

    main()
