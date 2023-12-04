# Copyright 2023 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Payment Adyen Refund",
    "version": "13.0.1.0.0",
    "category": "Banking addons",
    "license": "AGPL-3",
    "summary": "Adds method to refund payments made through Adyen",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "depends": ["payment_adyen_paybylink"],
    "data": ["data/account_payment_method.xml", "views/account_invoice.xml"],
    "installable": True,
    "auto_install": False,
}
