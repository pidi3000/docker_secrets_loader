
####################################################################################################
# File writer config
####################################################################################################

OUTPUT_FILE_SECRETS = "secrets.txt"
OUTPUT_FILE_SYSTEM = "secrets_system.txt"
OUTPUT_FILE_TEMPLATE = ["secrets_template.txt"]

####################################################################################################
# Password Manager Vars
####################################################################################################
PM_NAME = "1password"
"""
Name of the Password manager handler to use
"""

PM_ACCESS_TOKEN_FILE = ".pm_access_token"
"""
Path to the file containing the an access token used by the handler to connect to the Password manager
for example the Service account token for 1Password
"""

# ! SET A VALUE HERE <----------------------------------------------------------------------------------------------------
PM_VAULT_NAME = "SET A VALUE"
"""
Name of the Vault containing all the secrets
"""

PM_SECRETS_SECTION_NAME = "ENV VARS"
"""
Name of the section where the secrets are saved in the Password Manager
"""

##################################################
# Slug config
##################################################
PM_WRITE_SLUGS = False
"""
write slugs to the password manger
"""

PM_WRITE_SLUGS_DRYRUN = False
"""
don't actually write slugs to the password manger, for testing
"""

PM_WRITE_SLUGS_FORCE = False
"""
force overwriting slugs even if they are the same
"""

# ! SET A VALUE HERE <----------------------------------------------------------------------------------------------------
GLOBAL_SLUG_PREFIX = "SET A VALUE"
"""
All slugs are prefixed with this value
to avoid potential naming conflicts
"""

PM_SLUG_SECTION_NAME = "ENV VAR SLUGS (Auto created)"
"""
Name of the section where the Slugs are saved in the Password Manager
"""
