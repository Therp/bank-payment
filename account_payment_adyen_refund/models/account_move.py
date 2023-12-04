# Copyright - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""Support Adyen Refund."""
from odoo import fields, models


class AccountMove(models.Model):
    """Support Adyen Refund."""

    _inherit = "account.move"

    # This field is identical to the one in base_transaction_id,
    # but I do not want to add a dependency, but neither do
    # I want to have a field with the same purpose and another name.
    transaction_id = fields.Char(
        string="Transaction ID",
        index=True,
        copy=False,
        help="Transaction ID from the " "financial institute",
    )
    # This field will be used to keep track of Adyen refund status, but
    # conceivable might also be usefull for other payment types.
    refund_status = fields.Selection(
        selection=[
            ("none", "No refund submitted"),
            ("send", "Sending request to payment provider"),
            ("submitted", "Requested from payment provider"),
            ("done", "Confirmed by payment provider"),
            ("failed", "Payment provider rejected payment"),
        ],
        default="none",
        readonly=True,
    )
    refund_failure_reason = fields.Text(readonly=True)
