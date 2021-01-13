# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import timedelta


class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'OpenAcademy Courses'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    copyright = fields.Text(string="Copyright")

    responsible_id = fields.Many2one('res.users',
        ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="Sessions"
        )

    # Overwrite the default copy method with one that ensures unique names.
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))]
        )
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)
        
        default['name'] = new_name
        return super(Course, self).copy(default)


    _sql_constraints = [
        ('name_description_check',
        'CHECK(name != description)',
        "The title of the course should not be the description"),

        ('name_unique',
        'UNIQUE(name)',
        "This course title is already taken. Each course title must be unique."),
    ]


class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'OpenAcademy Sessions'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    colour = fields.Integer()

    instructor_id = fields.Many2one('res.partner', string="Instructor",
        domain=['|', ('instructor', '=', True),
            ('category_id.name', 'ilike', "Teacher")])
    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    end_date = fields.Date(string="End Date", store=True,
        compute='_get_end_date', inverse='_set_end_date')
    attendees_count = fields.Integer(
        string="Attendees Count", compute='_get_attendees_count', store=True
    )

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for record in self:
            if not (record.start_date and record.duration):
                record.end_date = record.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=record.duration, seconds=-1)
            record.end_date = record.start_date + duration
    

    def _set_end_date(self):
        for record in self:
            if not (record.start_date and record.end_date):
                continue
            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 instead.
            record.duration = (record.end_date - record.start_date).days + 1


    
    @api.depends('seats', 'attendee_ids')
    # Below function will update when these values do.
    def _taken_seats(self):
        for record in self:
            if not record.seats:
                record.taken_seats = 0.0
            else:
                record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Invalid 'seats' value",
                    'message': "The number of available seats cannot be a negative number"
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Over-subscribed",
                    'message': "There are more attendees than available seats. Increase seats or remove attendees."
                },
            }
    
    # Check if start date occurs before today's date
    @api.onchange('start_date')
    def _verify_valid_start_date(self):
        today = fields.Date.today()
        if self.start_date < today:
            return {
                'warning': {
                    'title': "Start date in past",
                    'message': "You're chose start date occurs in the past."
                }
            }

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for record in self:
            record.attendees_count = len(record.attendee_ids)

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for record in self:
            if record.instructor_id and record.instructor_id in record.attendee_ids:
                raise exceptions.ValidationError("The session's instructor cannot attend their own session.")