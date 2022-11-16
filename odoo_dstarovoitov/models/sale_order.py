import json
import random

import pytz

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools import misc


class SaleOrder(models.Model):
    _inherit = "sale.order"
    test_field = fields.Text(string='Test')

    _sql_constraints = [
        ('check_test_field', 'CHECK(char_length(test_field) < 50)',
         'Длина текста должна быть меньше 50 символов!'),
    ]

    # Если пользователь меняет строки (продукты) Quotations или изменяет Quotation Date,
    # то значение меняется на лету на текст в формате «Total - Date» (пример значения: 8,287.50 - 02/06/2022 16:33:53)
    @api.onchange('date_order', 'order_line')
    def _onchange_date_or_order(self):
        if self.state == 'draft':
            # переводим self.date_order из временной зоны БД во временную зону пользователя
            user_tz = pytz.timezone(self.env.user.tz)
            converted_tz = pytz.utc.localize(self.date_order).astimezone(user_tz).strftime(
                misc.DEFAULT_SERVER_DATETIME_FORMAT)
            self.test_field = f'{json.loads(self.tax_totals_json)["amount_total"]} - {converted_tz}'

    # Если пользователь вручную вводит текст длиной более 50 символов, то появляется сообщение «Длина текста должна быть меньше 50 символов!»
    @api.onchange('test_field')
    def _onchange_test_field(self):
        if len(self.test_field) > 50:
            raise ValidationError("Длина текста должна быть меньше 50 символов!")

    # По умолчанию, когда пользователь создает новый Quotation поле «Test» заполняется случайным числом.
    @api.model
    def create(self, vals):
        vals['test_field'] = random.randrange(100)
        return super().create(vals)
