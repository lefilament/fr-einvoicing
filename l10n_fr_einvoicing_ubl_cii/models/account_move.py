# Copyright 2026 Le Filament (https://le-filament.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _fr_ctc_send_invoice_prepare_flow_facturx(self):
        self.ensure_one()
        vals = {
            "syntax": "Factur-X",
            "filename": self.invoice_pdf_report_id.name,
            "processing_rule": "B2B",
            "type": "CustomerInvoice",
            "direction": "out",
            "file_bin": self.invoice_pdf_report_id.datas,
            "company_id": self.company_id.id,
        }
        return vals
