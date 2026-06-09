# Copyright 2026 Le Filament (https://le-filament.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging

from odoo import models

logger = logging.getLogger(__name__)


class FrEinvoicingFlow(models.Model):
    _inherit = "fr.einvoicing.flow"

    def _import_supplier_invoice(self):
        invoice_id = super()._import_supplier_invoice()
        if not invoice_id:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": self.filename,
                    "raw": base64.b64decode(self.file_bin),
                    "type": "binary",
                }
            )
            journal = self.env.ref(f"account.{self.env.company.id}_purchase")
            move_type = "in_invoice"
            invoice = self.env["account.move"].create(
                {
                    "journal_id": journal.id,
                    "move_type": move_type,
                    "fr_einvoicing_flow_id": self.id,
                }
            )
            invoice._extend_with_attachments(attachment, new=True)
            invoice._message_log(
                body=self.env._("Facture reçue depuis la PA"),
                attachment_ids=attachment.ids,
            )
        return invoice.id
