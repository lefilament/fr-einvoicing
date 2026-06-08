{
    "name": "France - UBL/CII formats",
    "category": "Accounting/Localizations/EDI",
    "website": "https://github.com/lefilament/fr-einvoicing",
    "description": """
        - Adds mandatory fields in Factur-x for France invoices
        - Adds UBL 21 for France invoices
    """,
    "author": "Odoo SA",
    "depends": [
        "l10n_fr_account",
        "account_edi_ubl_cii_tax_extension",
    ],
    "data": [],
    "license": "LGPL-3",
    "post_init_hook": "_post_init",
    "uninstall_hook": "uninstall_hook",
}
