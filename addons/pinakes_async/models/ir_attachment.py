# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import datetime
import logging
import pandas as pd

from odoo import models, _

_logger = logging.getLogger(__name__)
SPLIT_LOT = 400
# List of column excel vis fields odoo
# List : (field, column_excel,type of field)
# column name must be in lower case in the list
TRX_COLUMN_NAMES = [('name', 'ORDERID', str),
                    ('carrier_tracking_ref', 'TRACKING', str)]


def now_in_time_range(time_range):
    """Return true if x is in the range [start, end]"""

    if (isinstance(time_range, list)
            and len(time_range) == 2 and isinstance(time_range[0], int)
            and isinstance(time_range[1], int)
            and 0 <= time_range[0] < 24
            and 0 <= time_range[1] < 24):
        time_now = datetime.datetime.now().time()
        start = datetime.time(time_range[0], 0, 0)
        end = datetime.time(time_range[1], 0, 0)
        if start <= end:
            return start <= time_now <= end
        else:
            return start <= time_now or time_now <= end
    return False


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def sync_transactions(self, from_date='', last_days=None,
                          sleep_range=None, limit=10):

        if sleep_range and now_in_time_range(sleep_range):
            return

        StockObj = self.env['stock.picking'].sudo()
        res = {}
        # Sort and Truncate the records to `limit`
        all_records = self.sorted(key='id', reverse=True)
        to_sync_records = all_records[:limit]
        for rec in to_sync_records:
            rec.action_progress()
            rec.env.cr.commit()  # pylint: disable=E8102
            self.clear_caches()

            exception = False
            try:
                if rec.name.lower().endswith(".csv"):
                    # We can read also from csv file
                    # if the extention is csv
                    df = rec.get_csv_dataframe()
                else:
                    # By Default we read from excel file.
                    df = rec.get_excel_dataframe()

            except Exception as e:
                message = _("Format file Excel invalid, ") % e
                rec.action_fail(message=message)
                continue

            if not isinstance(df, pd.DataFrame):
                message = "Format file Excel invalid, No dataframe founded"
                rec.action_fail(message=message)
                continue

            ctr_failed = 0
            counter = 0

            for tup in df.itertuples():
                counter += 1
                if counter > SPLIT_LOT:
                    counter = 0
                    rec.env.cr.commit()  # pylint: disable=E8102
                    self.clear_caches()

                try:
                    fields = tup._1.split(';')
                    ORDERID = fields[0]
                    TRACKING = fields[1]

                    result = StockObj.search([('name', '=ilike', ORDERID)],
                                             limit=1)
                    if result:
                        result.write({'carrier_tracking_ref': str(TRACKING)})

                except Exception as e:
                    message = ("Ignored/ %s: System error\n"
                               "Error: %s") % (result, e)

                    rec._log(message=message, type="danger")
                    ctr_failed += 1
                    exception = True
                    continue

            if len(df) == 0:
                res.update({rec.id: {'state': "done", 'message': ''}})
                message = "____Done But ths File is empty____"
                rec.action_done(message=message, exception=exception)
            elif ctr_failed == len(df):
                message = "_____All lines was failed to be imported___"
                res.update({rec.id: {'state': "fail", 'message': ''}})
                rec.action_fail(message=message)
            elif ctr_failed == 0:
                message = "____Done____"
                res.update({rec.id: {'state': "done", 'message': ''}})
                rec.action_done(message=message, exception=exception)
            else:
                message = "_Partial Done: one or more lines have been ignored_"
                res.update({rec.id: {'state': "partial_done", 'message': ''}})
                rec.action_partial_done(message=message)

        return res
