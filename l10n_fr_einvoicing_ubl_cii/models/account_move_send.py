# Copyright 2026 Le Filament (https://le-filament.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import logging

from odoo import api, models

logger = logging.getLogger(__name__)


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_default_sending_method(self, move) -> str:
        # EXTENDS 'account'
        preferred_method = move.commercial_partner_id.with_company(
            move.company_id
        ).invoice_sending_method
        if not preferred_method and self._is_applicable_to_move("fr_pa", move):
            return "fr_pa"
        return super()._get_default_sending_method(move)

    # -------------------------------------------------------------------------
    # SENDING METHODS
    # -------------------------------------------------------------------------
    def _is_applicable_to_company(self, method, company):
        # EXTENDS 'account'
        if method == "fr_pa":
            return (
                company.partner_id.with_company(company.id).fr_directory_entity_type
                == "private"
            )
        else:
            return super()._is_applicable_to_company(method, company)

    def _is_applicable_to_move(self, method, move, **move_data):
        # EXTENDS 'account'
        if method == "fr_pa":
            if move_data:
                invoice_edi_format = move_data.get("invoice_edi_format", False)
            else:
                invoice_edi_format = "factur-x"
            result = all(
                [
                    self._is_applicable_to_company(method, move.company_id),
                    move.fr_einvoicing_required,
                    invoice_edi_format in ["facturx", "ubl_21_fr"]
                    and not move.fr_einvoicing_flow_id,
                ]
            )
            return result
        else:
            return super()._is_applicable_to_move(method, move, **move_data)

    def _call_web_service_after_invoice_pdf_render(self, invoices_data):
        # EXTENDS 'account'
        res = super()._call_web_service_after_invoice_pdf_render(invoices_data)

        for invoice, invoice_data in invoices_data.items():
            if "fr_pa" in invoice_data["sending_methods"]:
                if not self._is_applicable_to_move("fr_pa", invoice, **invoice_data):
                    continue

                flow_vals = {
                    "processing_rule": "B2B",
                    "type": "CustomerInvoice",
                    "direction": "out",
                    "company_id": invoice.company_id.id,
                }
                if invoice_data["invoice_edi_format"] == "facturx":
                    flow_vals.update(
                        {
                            "syntax": "Factur-X",
                            "filename": invoice_data["pdf_attachment_values"]["name"],
                            "file_bin": base64.b64encode(
                                invoice_data["pdf_attachment_values"]["raw"]
                            ),
                        }
                    )
                else:
                    flow_vals.update(
                        {
                            "syntax": "UBL",
                            "filename": invoice_data["ubl_cii_xml_attachment_values"][
                                "name"
                            ],
                            "file_bin": base64.b64encode(
                                invoice_data["ubl_cii_xml_attachment_values"]["raw"]
                            ),
                        }
                    )
                flow = self.env["fr.einvoicing.flow"].sudo().create(flow_vals)
                flow.send()
                logger.info(
                    "Flow ID %s created to send invoice %s ID %d",
                    flow.id,
                    invoice.display_name,
                    invoice.id,
                )
                invoice.fr_einvoicing_flow_id = flow.id

        return res
