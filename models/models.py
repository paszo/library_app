# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError

class Book(models.Model):
    _name = 'library.book'
    _description = 'Book'
    _order = 'name, date_published desc'
    #String fields
    name = fields.Char(
        'Title',
        default=None,
        index=True,
        help='Book cover title.',
        readonly=False,
        required=True,
        translate=False,
        )
    isbn = fields.Char('ISBN')
    book_type = fields.Selection(
        [('paper','Paperback'),
        ('hard','Hardcover'),
        ('electronic','Electronic'),
        ('other','Other')],
        'Type')
    notes = fields.Text('Internal Notes')
    descr = fields.Html('Description')

    # Numeric fields
    copies = fields.Integer(default=1)
    avg_rating = fields.Float('Average Rating', (3, 2))
    price = fields.Monetary('Price', 'currency_id')
    currency_id  = fields.Many2one('res.currency') #price helper

    # Date and time fields:
    date_published = fields.Date()
    last_borrow_date = fields.Datetime(
        'Last Borrowed On',
        default=lambda self: fields.Datetime.now())

    # Other fields
    active = fields.Boolean('Active?', default=True)
    date_published = fields.Date()
    image = fields.Binary('Cover')
    publisher_id = fields.Many2one('res.partner', string='Publisher')
    author_ids = fields.Many2many('res.partner', string='Authors')

    @api.multi
    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderators = [1, 3] * 6
            total = sum(a * b for a, b in zip(digits[:12], ponderators))
            remain = total % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    @api.multi
    def button_check_isbn(self):
        for book in self:
            if not book.isbn:
                raise Warning(
                'Please provide an ISBN13 for %s' % book.name)
            if book.isbn and not book._check_isbn():
                raise Warning(
                '%s is an invalid ISBN' % book.isbn)
            return True

    category_id = category_id = fields.Many2one('library.book.category', string='Category')

    publisher_country_id = fields.Many2one(
        'res.country',
        string='Publisher Country',
        compute='_compute_publisher_country',
        inverse='_inverse_publisher_country',
        search='_search_publisher_country',
    )

    @api.depends('publisher_id.country_id')
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id

    @api.depends('publisher_country_id')
    def _inverse_publisher_country(self):
        for book in self:
            if book.publisher_id:
                book.publisher_id.country_id = book.publisher_country_id

    def _search_publisher_country(self, operator, value):
        return [('publisher_id.country_id', operator, value)]

    publisher_country_related = fields.Many2one(
        'res.country',
        string='Publisher Country (related)',
        related='publisher_id.country_id',
    )

    _sql_constraints = [
        ('library_book_name_date_uq',
        'UNIQUE (name, date_published)',
        'Book title and publication date must be unique.'),
        ('library_book_check_date',
        'CHECK (date_published <= current_date)',
        'Publication date must not be in the future.'),
    ]

    @api.constrains('isbn')
    def _constrain_isbn_valid(self):
        for book in self:
            if book.isbn and not book._check_isbn():
                raise ValidationError(
                '%s is an invalid ISBN' % book.isbn)







    class Partner(models.Model):
        _inherit = 'res.partner'
        published_book_ids = fields.One2many(
            'library.book', #related model
            'publisher_id', #field for this in the related model
            string='Published Books')

        book_ids = fields.Many2many(
            'library.book',
            string='Authored Books')

    class BookCategory(models.Model):
        _name = 'library.book.category'
        _description = 'Book Category'
        _parent_store = True

        name = fields.Char(translate=True, required=True)
        # Hierarchy fields
        parent_id = fields.Many2one(
            'library.book.category',
            'Parent Category',
            ondelete='restrict')
        parent_path = fields.Char(index=True)

        # Optional but good to have:
        child_ids = fields.One2many(
            'library.book.category',
            'parent_id',
            'Subcategories')

        highlighted_id = fields.Reference(
            [('library.book', 'Book'), ('res.partner', 'Author')],
            'Category Highlight',)





# class library_app(models.Model):
#     _name = 'library_app.library_app'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
