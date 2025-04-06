
import config
from password_manager_handlers import Password_Manager_handler_base, PM_Entry_Base, PM_Field_Base

import asyncio
from onepassword.client import Client
from onepassword import (
    VaultOverview,
    ItemOverview,
    Item,
    ItemField,
    ItemFieldType,
    ItemSection,
    Secrets,
    PasswordRecipeRandom,
    PasswordRecipeRandomInner
)


class onepassword_handler(Password_Manager_handler_base):
    # ! https://github.com/1Password/onepassword-sdk-python?tab=readme-ov-file
    _token: str
    _client: Client

    def __init__(self):

        # if config.OP_SERVICE_ACCOUNT_TOKEN is not None or len(str(config.OP_SERVICE_ACCOUNT_TOKEN).strip()) < 5:
        #     self.token = config.OP_SERVICE_ACCOUNT_TOKEN
        # else:

        auth_token = self.load_auth_token()

        if not auth_token.startswith("ops_"):
            raise ValueError(
                "Auth Token has invalid format, must start with `ops_`for  1password service account tokens")
        self._token = auth_token

        self._client = asyncio.run(
            Client.authenticate(
                auth=self._token,
                integration_name="Docker Secrets loader",
                integration_version="v1.0.0"
            )
        )
        

    def _get_secrets_vault(self) -> VaultOverview:
        async def _temp():
            vaults = await self._client.vaults.list_all()
            async for vault in vaults:
                # print(vault.title)
                if vault.title.upper() == config.PM_VAULT_NAME.upper():
                    return vault

            return None

        vault = asyncio.run(_temp())

        # print(vault)
        if vault is None:
            raise ValueError(
                f"no matching vault found with name: `{config.PM_VAULT_NAME}`")

        return vault

    def _get_items_in_vault(self, vault: VaultOverview):
        async def _temp(vault: VaultOverview):
            items = await self._client.items.list_all(vault.id)
            _items: list[ItemOverview] = []
            async for item in items:
                # ! excluded conditions
                if not item.title.startswith("_") or "template".upper() not in item.title.upper():
                    # self._normalize_entrie_data(item)
                    # print(item.title)
                    _items.append(item)

            return _items

        items = asyncio.run(_temp(vault))

        print()
        print(f"Items found in vault '{vault.title}':")
        for item in items:
            print(f"\t- {item.title}")

        print()
        return items

    def get_all_entries(self) -> list[PM_Entry_Base]:
        secrets_vault = self._get_secrets_vault()
        items = self._get_items_in_vault(vault=secrets_vault)

        all_entries: list[PM_Entry_Base] = []
        for item in items:
            entry = self._normalize_entrie_data(item)
            all_entries.append(entry)

        all_entries = sorted(
            all_entries, key=lambda entry: entry.service_prefix)

        return all_entries

    def _get_entry_details_by_id(self, vault_id, entry_id) -> Item:
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

        async def _temp():
            # Retrieve an item from your vault.
            return await self._client.items.get(vault_id=vault_id, item_id=entry_id)

        return asyncio.run(_temp())

    def _get_entry_details(self, item: ItemOverview) -> Item:
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

        return self._get_entry_details_by_id(vault_id=item.vault_id, entry_id=item.id)

    ####################################################################################################

    def set_all_field_slugs(self, pm_entry: PM_Entry_Base):

        print()
        print(f"Writing slugs to PM for Entry: `{pm_entry.service_name}`")

        item_details = self._get_entry_details_by_id(
            vault_id=pm_entry.pm_vault_id, entry_id=pm_entry.pm_entry_id)

        try:
            slug_fields, slugs_section = self._get_fields_in_section(
                item=item_details,
                section_name=config.PM_SLUG_SECTION_NAME
            )

        except ValueError as identifier:
            print(
                f"  Creating slugs entry section with name: `{config.PM_SLUG_SECTION_NAME}`")
            slug_fields = []
            slugs_section = ItemSection(
                id=self._generate_password(),
                title=config.PM_SLUG_SECTION_NAME
            )

            item_details.sections.append(slugs_section)

        item_fields_to_add = []
        for pm_field in pm_entry.pm_fileds:
            field_exists = False

            for field in slug_fields:
                if field.title == pm_field.field_name:
                    if field.value == pm_field.slug and not config.PM_WRITE_SLUGS_FORCE:
                        # print(f"\tskiping field: \t\t`{pm_field.field_name}`")
                        field_exists = True

                    else:
                        print(
                            f"\toverwriting field: \t`{pm_field.field_name}`")
                        print(
                            f"\t\told=`{field.value}` \tnew=`{pm_field.slug}`")
                        field.value = pm_field.slug
                        field_exists = True

            if not field_exists:
                print(f"\tadding new field: \t`{pm_field.field_name}`")
                item_fields_to_add.append(
                    ItemField(
                        sectionId=slugs_section.id,
                        id=self._generate_password(),
                        title=pm_field.field_name,
                        value=pm_field.slug,
                        fieldType=ItemFieldType.TEXT
                    )
                )

        ##################################################
        # put the slug fields in the same order as the secrets fields
        ##################################################
        slug_fields.extend(item_fields_to_add)

        secrets_fields, secrets_section = self._get_fields_in_section(
            item=item_details,
            section_name=config.PM_SECRETS_SECTION_NAME
        )

        fields_order = {
            obj.title: index for index,
            obj in enumerate(secrets_fields)
        }
        slug_fields = sorted(
            slug_fields, key=lambda obj: fields_order.get(
                obj.title, float('inf')
            )
        )

        slug_field_ids = set(field.id for field in slug_fields)
        item_fields_no_slugs = [
            field for field in item_details.fields if field.id not in slug_field_ids
        ]

        item_details.fields = item_fields_no_slugs + slug_fields

        ##################################################

        if not config.PM_WRITE_SLUGS_DRYRUN:
            # ! to optimize API usage quota, this should only run if any actual cahnge was made
            # TODO
            updated_item = asyncio.run(self._client.items.put(item_details))

        print()

    ####################################################################################################

    def _get_fields_in_section(self, item: Item, section_id: str = None, section_name: str = None) -> tuple[list[ItemField], ItemSection]:

        if section_id is None and section_name is None:
            raise ValueError(
                f"either `section_id` or `section_name` must be set")

        target_section = None
        # print(item_details.sections)
        for section in item.sections:
            # print(section.title.upper().strip())
            if section_id is not None:
                if section.id.lower == section_id.lower():
                    target_section = section
                    break

            else:
                if section.title.upper().strip() == section_name.upper().strip():
                    target_section = section
                    break

        # print(target_section)

        if target_section is None:
            raise ValueError(
                f"no section found with `{section_id=}` or `{section_name=}`")

        fields_in_section: list[ItemField] = []
        for field in item.fields:
            # field in slugs section
            if field.section_id == target_section.id:
                fields_in_section.append(field)

        return fields_in_section, target_section

    ####################################################################################################

    def _generate_password(self, length: int = 26) -> str:
        password = Secrets.generate_password(
            PasswordRecipeRandom(
                parameters=PasswordRecipeRandomInner(
                    length=length,
                    includeDigits=True,
                    includeSymbols=False,
                )
            )
        )

        return password.password.lower()

    def _normalize_entrie_data(self, item: ItemOverview) -> PM_Entry_Base:
        """Takes the item object as given by 1Password SDK and converts it to a `PM_ENTRIE` object

        Parameters
        ----------
        item : _type_
            _description_
        """

        service_prefix = None
        all_item_fields: list[PM_Field_Base] = []

        item_details = self._get_entry_details(item)

        secret_fields, secrets_section = self._get_fields_in_section(
            item=item_details,
            section_name=config.PM_SECRETS_SECTION_NAME
        )

        # get service prefix
        for field in item_details.fields:
            # TODO maybe move service prefix to the "USERNAME" field
            if field.title.upper().strip() == "SERVICE PREFIX".upper():
                service_prefix = field.value.strip()
                break

        for field in secret_fields:
            if len(field.value.strip()) > 0 and field.title.upper().strip() != "SERVICE PREFIX".upper():
                pm_field = PM_Field_Base(
                    # pm_entry_id=item_details.id,
                    pm_field_id=field.id,
                    pm_field_type=field.field_type,
                    service_prefix=service_prefix,
                    field_name=field.title,
                    field_value=field.value
                )

                # print(pm_field)
                all_item_fields.append(pm_field)

        all_item_fields = sorted(
            all_item_fields, key=lambda field: field.field_name)

        pm_entry = PM_Entry_Base(
            pm_entry_id=item.id,
            service_name=item.title,
            service_prefix=service_prefix
        )
        
        pm_entry.pm_fileds = all_item_fields
        pm_entry.pm_vault_id = item.vault_id

        return pm_entry
