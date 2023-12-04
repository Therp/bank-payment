# Copyright - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""Support Adyen Refund."""
from odoo import _, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    """Support Adyen Refund."""

    _inherit = "account.payment"

    def post(self):
        """Actually transfer payment to Adyen, if that method selected."""
        for payment in self:
            if payment.payment_method_code != "adyen_refund":
                continue
            payment._check_adyen_refund_request()
            payment._send_adyen_refund_request()
        return super().post()

    def _check_adyen_refund_request(self):
        """validate payment for Adyen refund and send it."""
        self.ensure_one()
        # Refunds via Adyen work only for single invoices.
        if len(self.invoice_ids) != 1:
            raise UserError(
                _("You can only refund a single invoice per payment through Adyen")
            )
        # Check validity of invoices for adyen refund.
        invoice = self.invoice_ids[0]
        if invoice.refund_status != "none":
            raise UserError(_("Invoice %s already submitted for refund") % invoice.name)
        if invoice.type != "out_refund":
            raise UserError(_("Invoice %s is not a customer refund") % invoice.name)
        if not invoice.transaction_id:
            raise UserError(_("PsP number not filled in invoice %s") % invoice.name)

    def _send_adyen_refund_request(self):
        """Actually request refund from Adyen."""
        self.ensure_one()
        transaction_model = self.env["payment.transaction"]
        acquirer = self._get_acquirer()
        invoice = self.invoice_ids[0]
        reference = self._compute_reference(invoice.invoice_origin)
        values = {
            "acquirer_id": acquirer.id,
            "reference": reference,
            "amount": float(self.amount),
            "currency_id": self.currency_id.id,
            "partner_id": self.partner_id.id,
            "payment_id": self.id,
            "acquirer_reference": False,
            "invoice_ids": [(4, invoice.id)],
            "type": "form_save"
            if acquirer.save_token != "none" and self.partner_id
            else "form",
        }
        refund_tx = transaction_model.create(values)
        self.write({"payment_transaction_id": refund_tx.id})
        invoice.write({"refund_status": "send"})
        self.env.cr.commit()
        refund_tx._adyen_send_refund()
        invoice.refund_status = "submitted"

    def _get_acquirer(self):
        """Get acquirer linked to journal, if any."""
        acquirer_model = self.env["payment.acquirer"]
        journal = self.journal_id
        acquirer = acquirer_model.search([("journal_id", "=", journal.id)], limit=1)
        if not acquirer:
            raise UserError(
                _("No payment acquirer linked to journal %s") % journal.name
            )
        return acquirer

    def _compute_reference(self, reference):
        """Adjust reference to avoid uniqueness constraint"""
        existing_count = self.env["payment.transaction"].search_count(
            [("reference", "=like", reference + "%")]
        )
        if not existing_count:
            return reference
        return reference + "-" + str(existing_count)
