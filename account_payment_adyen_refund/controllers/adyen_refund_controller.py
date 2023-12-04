# Copyright - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""WebHook for Adyen notifications."""
import logging
import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment_adyen_paybylink.controllers.main import (
    AdyenPayByLinkController,
)

_logger = logging.getLogger(__name__)


class AdyenRefundController(AdyenPayByLinkController):
    """Inherit AdyenPayByLinkController and added code to handle refund webhook call"""

    @http.route()
    def adyen_notification(self, **post):
        """Largely ad copy of super method, but for refunds and updating invoice."""
        event_code = post["eventCode"]
        if not event_code == "REFUND":
            return super().adyen_notification(**post)
        # Below this many of the same steps as in super method.
        _logger.info(
            "notification received from Adyen with data:\n%s", pprint.pformat(post)
        )
        try:
            # Check the integrity of the notification
            tx_sudo = (
                request.env["payment.transaction"]
                .sudo()
                ._adyen_form_get_tx_from_data(post)
            )
            self._verify_notification_signature(post, tx_sudo)
            # Check whether the event of the notification succeeded and reshape the notification
            # data for parsing
            if post["success"] != "true":
                tx_sudo.invoice_ids.write(
                    {
                        "refund_status": "failed",
                        "refund_failure_reason": post["reason"],
                    }
                )
            else:
                tx_sudo.invoice_ids.write(
                    {"refund_status": "done", "refund_failure_reason": False}
                )
                post["authResult"] = "AUTHORISED"
                # Handle the notification data
                request.env["payment.transaction"].sudo().form_feedback(post, "adyen")
        except ValidationError:  # Acknowledge the notification to avoid getting spammed
            _logger.exception(
                "unable to handle the notification data; skipping to acknowledge"
            )
        return "[accepted]"  # Acknowledge the notification
