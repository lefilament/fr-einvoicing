# Copyright 2026 Le Filament (https://le-filament.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountEdiXmlCII(models.AbstractModel):
    _inherit = "account.edi.xml.cii"

    def _export_invoice_vals(self, invoice):
        # Extend `account_edi_xml_cii` to use SIREN as identifier iso siret
        template_vals = super()._export_invoice_vals(invoice)
        seller_siren = invoice.company_id.partner_id._get_siren()
        buyer_siren = invoice.commercial_partner_id._get_siren()
        template_vals.update(
            {
                "seller_specified_legal_organization": seller_siren,
                "buyer_specified_legal_organization": buyer_siren,
            }
        )
        return template_vals
