# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    can_be_sold = fields.Boolean(
        string="Can be sold", compute="_compute_can_be_sold", readonly=False, store=True
    )

    @api.depends("packaging_level_id")
    def _compute_can_be_sold(self):
        for record in self:
            record.can_be_sold = record.packaging_level_id.can_be_sold
