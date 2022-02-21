# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from copy import deepcopy

from odoo import api, fields, models

# format: field_from_supplierinfo:field_from_group
MAPPING_RELATED = {
    "company_id": "company_id",
    "product_tmpl_id": "product_tmpl_id",
    "name": "partner_id",
    "product_id": "product_id",
    "product_name": "product_name",
    "product_code": "product_code",
    "sequence": "sequence",
}

MAPPING_MATCH_GROUP = {
    "company_id": "company_id",
    "product_tmpl_id": "product_tmpl_id",
    "name": "partner_id",
    "product_id": "product_id",
    "product_name": "product_name",
    "product_code": "product_code",
}
_logger = logging.getLogger(__name__)


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    supplierinfo_group_id = fields.Many2one("product.supplierinfo.group", required=True)
    company_id = fields.Many2one(related="supplierinfo_group_id.company_id", store=True)
    product_tmpl_id = fields.Many2one(
        related="supplierinfo_group_id.product_tmpl_id", store=True
    )
    name = fields.Many2one(
        related="supplierinfo_group_id.partner_id", store=True, required=False
    )
    product_id = fields.Many2one(related="supplierinfo_group_id.product_id", store=True)
    product_name = fields.Char(related="supplierinfo_group_id.product_name", store=True)
    product_code = fields.Char(related="supplierinfo_group_id.product_code", store=True)
    sequence = fields.Integer(related="supplierinfo_group_id.sequence", store=True)

    _sql_constraints = [
        (
            "uniq_price_per_qty",
            "unique(supplierinfo_group_id, min_qty, date_start, date_end)",
            "You can not have a two price for the same qty",
        )
    ]

    def _get_group_domain(self, vals):
        return [
            (field_group, "=", vals.get(field_supplierinfo))
            for field_supplierinfo, field_group in MAPPING_MATCH_GROUP.items()
        ]

    def _prepare_group_vals(self, vals):
        return {
            field_group: vals.get(field_supplierinfo)
            for field_supplierinfo, field_group in MAPPING_MATCH_GROUP.items()
        }

    def _set_group_id(self, vals):
        id_in_vals = vals.get("supplierinfo_group_id")
        if id_in_vals:
            vals["supplierinfo_group_id"] = id_in_vals
            return

        group = self.env["product.supplierinfo.group"].search(
            self._get_group_domain(vals)
        )
        if group:
            vals["supplierinfo_group_id"] = group.id
            return

        new_group = self.env["product.supplierinfo.group"].create(
            self._prepare_group_vals(vals)
        )
        vals["supplierinfo_group_id"] = new_group.id

    def to_supplierinfo_group(self, vals):
        new_val = deepcopy(vals)
        self._set_group_id(new_val)
        for field_supplierinfo in MAPPING_RELATED.keys():
            if field_supplierinfo in new_val:
                del new_val[field_supplierinfo]
        return new_val

    @api.model_create_multi
    def create(self, vals):
        new_vals = []
        for el in vals:
            new_vals.append(self.to_supplierinfo_group(el))
        return super().create(new_vals)
