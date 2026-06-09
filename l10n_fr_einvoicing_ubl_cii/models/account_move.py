# Copyright 2026 Le Filament (https://le-filament.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _fr_ctc_send_invoice_prepare_flow_facturx(self):
        self.ensure_one()
        invoice_edi_format = self.commercial_partner_id.invoice_edi_format
        # If PDF and XML have not yet been generated, we force generation
        if invoice_edi_format not in ["facturx", "ubl_21_fr"]:
            raise ValidationError(
                self.env._(
                    "Your partner need to be configured with an EDI format "
                    "supported by French Accredited Platforms (UBL 2.1 or Factur-x)"
                )
            )
        if not self.invoice_pdf_report_id or not self.ubl_cii_xml_id:
            self.env["account.move.send"]._generate_and_send_invoices(self)
        vals = {
            "processing_rule": "B2B",
            "type": "CustomerInvoice",
            "direction": "out",
            "company_id": self.company_id.id,
        }
        if invoice_edi_format == "facturx" and self.invoice_pdf_report_id:
            vals.update(
                {
                    "syntax": "Factur-X",
                    "filename": self.invoice_pdf_report_id.name,
                    "file_bin": self.invoice_pdf_report_id.datas,
                }
            )
        elif invoice_edi_format == "ubl_21_fr" and self.ubl_cii_xml_id:
            vals.update(
                {
                    "syntax": "UBL",
                    "filename": self.ubl_cii_xml_id.name,
                    "file_bin": self.ubl_cii_xml_id.datas,
                }
            )
        else:
            raise ValidationError(self.env._("Error when generating Invoice XML file"))
        return vals
