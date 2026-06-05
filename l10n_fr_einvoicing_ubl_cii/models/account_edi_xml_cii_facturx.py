# Copyright 2026 Le Filament (https://le-filament.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import html2plaintext


class AccountEdiXmlCII(models.AbstractModel):
    _inherit = "account.edi.xml.cii"

    def _get_exchanged_document_vals(self, invoice):
        # Extend `account_edi_xml_cii` to add mandatory default notes [BR-FR-05]
        result = super()._get_exchanged_document_vals(invoice)

        result["included_note_list"].extend(
            [
                {
                    "PMT": self.env._(
                        "In the event of late payment, a flat-rate fee of €40 for "
                        "collection costs will be charged "
                        "(Articles L.441-10 and D.441-5 of the Code de commerce)."
                    )
                },
                {
                    "PMD": self.env._(
                        "Late payment penalties at an annual rate of 10% are applied "
                        "if the payment is made after the due date."
                    )
                },
                {
                    "AAB": html2plaintext(invoice.invoice_payment_term_id.note)
                    if invoice.invoice_payment_term_id.early_discount
                    else self.env._("No discount for early payment.")
                },
            ]
        )

        return result

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
