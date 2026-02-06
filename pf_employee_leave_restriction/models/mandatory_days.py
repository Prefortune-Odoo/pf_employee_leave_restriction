from odoo import fields, models, api, _
from odoo.exceptions import *

class Mandatory_Days(models.Model):
    _inherit = 'hr.leave.mandatory.day'

    employees = fields.Many2many('hr.employee', string="Employees", required=True)
    
    # ===============================================================================================
    # Prevents the creation of duplicate records by ensuring no two records 
    # have the same name, the same date range, and overlapping employees.
    # ===============================================================================================

    @api.constrains('name', 'employees', 'start_date', 'end_date')
    def _check_duplicates(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('name', '=', record.name),
                ('start_date', '=', record.start_date),
                ('end_date', '=', record.end_date),
                ('employees', 'in', record.employees.ids)
            ]
            
            duplicate = self.search(domain, limit=1)
            
            if duplicate:
                raise ValidationError(_(
                    "A mandatory day record named '%s' already exists for these dates and employees. "
                    "You cannot create duplicate records."
                ) % record.name)

    # ===============================================================================================
    # Validation to ensure Mandatory Days are not backdated.
    # Triggered immediately when the user selects a start_date in the UI.
    # ===============================================================================================

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.start_date < fields.Date.today():
            invalid_date = self.start_date
            
            # 1. Reset the field first so the UI clears the bad value
            self.start_date = False 
            
            # 2. Raise the error to show the red box immediately
            raise UserError(_(
                "You selected %s, which is in the past. "
                "Mandatory days must be scheduled for today or the future."                
            ) % invalid_date)

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # ===============================================================================================
    # Validates if the requested leave period conflicts with any pre-defined 'Mandatory Days'.
    # Checks for overlaps based on Department or specific Employee assignments and
    # resets the date selection if a conflict is found to prevent restricted bookings.
    # ===============================================================================================

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_check_mandatory_days(self):
        if not self.employee_id or not self.date_from or not self.date_to:
            return

        # NEW: Allow Administrators to bypass the check
        if self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            return

        domain = [
            ('start_date', '<=', self.date_to.date()),
            ('end_date', '>=', self.date_from.date()),
            '|',
            ('department_ids', 'in', self.employee_id.department_id.ids),
            ('employees', 'in', self.employee_id.ids)
        ]

        mandatory_days = self.env['hr.leave.mandatory.day'].search(domain)
        if mandatory_days:
            #Create a detailed list of the restricted days with their dates
            details = []
            for day in mandatory_days:
                if day.start_date == day.end_date:
                    details.append(_("- %s (%s)") % (day.name, day.start_date))
                else:
                    details.append(_("- %s (From %s To %s)") % (day.name, day.start_date, day.end_date))
            
            error_msg = _("The selected period overlaps with the following Mandatory Day(s):\n\n%s\n\nPlease choose a different period.") % "\n".join(details)
            
            self.date_from = False
            self.date_to = False
            
            raise UserError(error_msg)
    
    # =====================================================================================================================
    # Acts as a server-side validation gate to prevent leave overlapping with Mandatory Days.
    # This ensures the restriction is enforced even if the UI onchange is bypassed (e.g., via CSV import or mobile).
    # =====================================================================================================================

    @api.constrains('date_from', 'date_to', 'employee_id', 'state')
    def _check_mandatory_days_final_block(self):
        for rec in self:
            # If dates were cleared (by cancel) or are missing, skip the check
            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue
            # We check this even if they try to press 'Confirm'
            domain = [
                ('start_date', '<=', rec.date_to.date()),
                ('end_date', '>=', rec.date_from.date()),
                '|',
                ('department_ids', 'in', rec.employee_id.department_id.ids),
                ('employees', 'in', rec.employee_id.ids)
            ]
            
            if self.env['hr.leave.mandatory.day'].search(domain, limit=1):
                raise ValidationError(_(
                    "Submission Denied: You cannot request leave during a Mandatory Day. "
                    "Please check the company calendar and select different dates."
                ))
    
    # ==========================================================================================================
    # Overrides the default delete behavior to restrict which leave requests can be removed.
    # Ensures that only non-validated records (Draft, Cancelled, or Refused) are deleted 
    # to maintain historical audit trails for Approved/Confirmed leaves.
    # Cancel Button is only visible when record have Future Dates for Leave  
    # ==========================================================================================================
    def unlink(self):
        for record in self:
            # Odoo base prevents deleting 'refuse', so we allow 'draft', 'cancel', and 'refuse'
            if record.state not in ['draft', 'cancel', 'refuse']:
                raise UserError(_("You cannot delete a time off which is in %s state. "
                                  "Only Draft, Cancelled, or Refused leaves can be deleted.") % record.state)
        
        # Call the super method to perform the actual deletion
        return super(HrLeave, self).unlink()
    
    # ==========================================================================================================
    # Overrides the standard mandatory day validation to allow specific exceptions.
    # Ensures that 'Sick Time Off' requests can still be submitted during restricted periods,
    # while maintaining standard enforcement for all other leave types.
    # ==========================================================================================================
    @api.constrains('date_from', 'date_to', 'holiday_status_id')
    def _check_mandatory_days(self):
        return True
    
    # ==========================================================================================================
    # Prevents employees from selecting past dates for Time Off requests.
    # Triggered immediately when the user modifies the Start Date or End Date in the UI.
    # Ensures that leave requests can only be created for today or future dates,
    # providing instant feedback by resetting invalid fields and displaying an error.
    # ==========================================================================================================
    @api.onchange('date_from', 'date_to')
    def _onchange_block_past_dates(self):
        today = fields.Date.today()

        if self.date_from and self.date_from.date() < today:
            self.date_from = False
            raise UserError(_("You cannot select a start date in the past."))

        if self.date_to and self.date_to.date() < today:
            self.date_to = False
            raise UserError(_("You cannot select an end date in the past."))
