# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time


class account_cash_statement2(osv.osv):
    _inherit = 'account.bank.statement'

    print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x"
    print "x X x X x X x X x X x X x X x X x X x X x X x X x X x X x X"
    print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x"
    print "Necesito saber si esto se hereda correctamente..."
    print "x X x X x X x X x X x X x X x X x X x X x X x X x X x X x X"
    print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
    print "x X x X x X x X x X x X x X x X x X x X x X x X x X x X x X"
    
    def button_confirm_bank(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
        print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
        print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
        print "O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O "
        print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
        print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
        print "X x X x X x X x X x X x X x X x X x X x X x X x X x X x X x "
    
            
        return super(account_cash_statement, self).button_confirm_bank(cr, uid, ids, context=context)
    
        for st in self.browse(cr, uid, ids, context=context):
            j_type = st.journal_id.type
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue

            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error!'), _('Please verify that an account is defined in the journal.'))
            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise osv.except_osv(_('Error!'), _('The account entries lines are not in valid state.'))
            move_ids = []
            for st_line in st.line_ids:
                if not st_line.amount:
                    continue
                if st_line.account_id and not st_line.journal_entry_id.id:
                    #make an account move as before
                    vals = {
                        'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                        'credit': st_line.amount > 0 and st_line.amount or 0.0,
                        'account_id': st_line.account_id.id,
                        'name': st_line.name
                    }
                    self.pool.get('account.bank.statement.line').process_reconciliation(cr, uid, st_line.id, [vals], context=context)
                elif not st_line.journal_entry_id.id:
                    raise osv.except_osv(_('Error!'), _('All the account entries lines must be processed in order to close the statement.'))
                move_ids.append(st_line.journal_entry_id.id)
            if move_ids:
                self.pool.get('account.move').post(cr, uid, move_ids, context=context)
            self.message_post(cr, uid, [st.id], body=_('Statement %s confirmed, journal items were created.') % (st.name,), context=context)
        self.link_bank_to_partner(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'confirm', 'closing_date': time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)



        


class account_move(osv.osv):

    _inherit = 'account.move'

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_ids = ids
        for move in self.browse(cr, uid, ids):
            if move.journal_id.pos_dont_create_entries:
                self.unlink(cr, uid, [move.id])
                move_ids.remove(move.id)
        res = True
        if move_ids:
            res = super(account_move, self).post(cr, uid, move_ids, context)
        return res


class account_journal(osv.osv):
    _inherit = 'account.journal'
    """
	Adds check to indicate if Cash Account Journal will not create Account Entries
    """

    _columns = {
        'pos_dont_create_entries' : fields.boolean("POS - Don't Create Account Entries", 
                                               help="Related to POS Payment Journals. If you check this journal \n"+\
                                                    "and it's a POS Payment Journal then there will not be account \n"+\
                                                    "entries for POS Payments"),
        'pos_group_entries_by_statement' : fields.boolean("POS - Group Entries by Statement"),

    }

    


class product_uom(osv.osv):
    _inherit = 'product.uom'
    """
	Adds check to indicate if Partner is General Public
    """

    _columns = {
        'use_4_invoice_general_public' : fields.boolean('Use for General Public Invoice'),
    }
    
    def _check_use_4_invoice_general_public(self, cr, uid, ids, context=None):        
        for record in self.browse(cr, uid, ids, context=context):
            if record.use_4_invoice_general_public:
                res = self.search(cr, uid, [('use_4_invoice_general_public', '=', 1)], context=None)                
                if res and res[0] and res[0] != record.id:
                    return False
        return True

    
    _constraints = [
        (_check_use_4_invoice_general_public, 'Error ! You can have only one Unit of Measure checked to Use for General Public Invoice...', ['use_4_invoice_general_public']),
        ]



class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    """
	Adds check to indicate Partner is General Public
    """

    _columns = {
        'invoice_2_general_public'  : fields.boolean('Invoice to General Public Partner', help="Check this if this Customer will be invoiced as General Public"),
        'use_as_general_public'     : fields.boolean('Use as General Public Partner', help="Check this if this Customer will be used to create Daily Invoice for General Public"),
    }
    
    def _check_use_as_general_public(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.use_as_general_public:
                res = self.search(cr, uid, [('use_as_general_public', '=', 1)], context=None)                
                if res and res[0] and res[0] != record.id:
                    return False
        return True

    
    _constraints = [
        (_check_use_as_general_public, 'Error ! You can have only one Partner checked as Use as General Public...', ['use_as_general_public']),
        ]
        
    
    def on_change_use_as_general_public(self, cr, uid, ids, use_as_general_public=False, context=None):
        if context is None: context = {}
        res = {}
        if not use_as_general_public:
            return res
        
        if use_as_general_public:
            return {'value':{'invoice_2_general_public':False}}
    
    
    
class pos_order(osv.osv):
    _inherit = 'pos.order'
    
    
    _columns = {
        'invoice_2_general_public': fields.boolean('General Public', help="Check this if this Customer will be invoiced as General Public"),
    }


    
    def action_invoice2(self, cr, uid, ids, journal_id, context=None):
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []
        for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue
            if not order.partner_id:
                raise osv.except_osv(_('Error!'), _('Please provide a partner for the sale.'))
#############
            partner_obj = self.pool.get('res.partner')
            addr = partner_obj.address_get(cr, uid, order.partner_id.parent_id and order.partner_id.parent_id.id or order.partner_id.id, ['delivery', 'invoice', 'contact'])
            partner = partner_obj.browse(cr, uid, addr['invoice'])[0]
#############
            acc = partner.property_account_receivable.id
            inv = {
                'name': order.name,
                'origin': order.name,
                'account_id': acc,
                'journal_id': journal_id and journal_id or order.sale_journal.id,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': partner.id, #order.partner_id.id,
                'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                'payment_term' : partner.property_payment_term and partner.property_payment_term.id or False,
                'comment': order.note or '',
                'currency_id': order.pricelist_id.currency_id.id, # considering partner's sale pricelist's currency
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', partner.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)
            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
            inv_ids.append(inv_id)
            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id = partner.id,
                                                               fposition_id=partner.property_account_position.id)['value'])
                if not inv_line.get('account_analytic_id', False):
                    inv_line['account_analytic_id'] = \
                        self._prepare_analytic_account(cr, uid, line,
                                                       context=context)
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name
                inv_line['invoice_line_tax_id'] = [(6, 0, inv_line['invoice_line_tax_id'])]
                inv_line_ref.create(cr, uid, inv_line, context=context)
            inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
            self.signal_workflow(cr, uid, [order.id], 'invoice')
            inv_ref.signal_workflow(cr, uid, [inv_id], 'validate')
        return inv_ids and inv_ids[0] or False
    
    
    def action_invoice3(self, cr, uid, ids, date, journal_id=False, context=None):
        if context is None: context = {}
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []
        po_ids = []
        lines = {}
        for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue
            if not order.invoice_2_general_public:
                res = self.action_invoice2(cr, uid, [order.id], journal_id, context=context)
                inv_ids.append(res)
            else:
                po_ids.append(order.id)
                for line in order.lines:
                    ## Agrupamos las líneas según el impuesto
                    tax_names = ", ".join([x.name for x in line.product_id.taxes_id])
                    val={
                        'tax_names'           : ", ".join([x.name for x in line.product_id.taxes_id]),
                        'taxes_id'            : ",".join([str(x.id) for x in line.product_id.taxes_id]),
                        'price_subtotal'      : line.price_subtotal,
                        'price_subtotal_incl' : line.price_subtotal_incl,
                        }
                    key = (val['tax_names'],val['taxes_id'])
                    if not key in lines:
                        lines[key] = val
                        lines[key]['price_subtotal'] = val['price_subtotal']
                        lines[key]['price_subtotal_incl'] = val['price_subtotal_incl']

                    else:
                        lines[key]['price_subtotal'] += val['price_subtotal']
                        lines[key]['price_subtotal_incl'] += val['price_subtotal_incl']

        if po_ids:
            partner_obj = self.pool.get('res.partner')
            partner_id = partner_obj.search(cr, uid, [('use_as_general_public','=',1)], limit=1, context=context)
            if not partner_id:
                raise osv.except_osv(_('Error!'), _('Please configure a Partner as default for Use as General Public Partner.'))    

            addr = partner_obj.address_get(cr, uid, partner_id, ['delivery', 'invoice', 'contact'])
            partner = partner_obj.browse(cr, uid, addr['invoice'])[0]

            uom_obj = self.pool.get('product.uom')
            uom_id = uom_obj.search(cr, uid, [('use_4_invoice_general_public','=',1)], limit=1, context=context)
            if not uom_id:
                raise osv.except_osv(_('Error!'), _('Please configure an Unit of Measure as default for use as UoM in Invoice Lines.'))    
            
            acc = partner.property_account_receivable.id
            inv = {
                'name'      : _('Invoice from POS Orders'),
                'origin'    : _('POS Orders from %s' % (date[8:10]+'/'+date[5:7]+'/'+date[0:4])),
                'account_id': acc,
                'journal_id': journal_id or order.sale_journal.id,
                'type'      : 'out_invoice',
                'reference' : order.pos_reference,
                'partner_id': partner.id,
                'comment'   : _('Invoice created from POS Orders'),
                'currency_id': order.pricelist_id.currency_id.id, # considering partner's sale pricelist's currency
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', partner.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)

            self.write(cr, uid, po_ids, {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
            inv_ids.append(inv_id)
            for key, line in lines.iteritems():
                tax_name = ''
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': False,
                    'name'      : _('VENTA AL PUBLICO EN GENERAL DEL DIA %s DEL ALMACEN %s CON %s' % \
                                    #VENTA AL PUBLICO EN GENERAL DEL DIA %s DEL ALMACEN %s CON %S' % \
                                    (date[8:10]+'/'+date[5:7]+'/'+date[0:4], order.location_id.name, line['tax_names'])),
                    'quantity'  : 1,
                    'account_id': order.lines[0].product_id.property_account_income.id or order.lines[0].product_id.categ_id.property_account_income_categ.id,
                    'uos_id'    : uom_id[0],
                    'price_unit': line['price_subtotal'],
                    'discount'  : 0,
                    'invoice_line_tax_id' : [(6, 0, line['taxes_id'].split(','))]
                }
                inv_line_ref.create(cr, uid, inv_line, context=context)
            inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
            self.signal_workflow(cr, uid, po_ids, 'invoice')
            inv_ref.signal_workflow(cr, uid, [inv_id], 'validate')

        if not inv_ids: return {}
        
        ir_model_data = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = ir_model_data.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        context.update({'type':'out_invoice'})
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', [" + ','.join(map(str, inv_ids)) + "])]"
        return result
        


class pos_order_invoice_wizard(osv.osv_memory):
    _name = "pos.order.invoice_wizard"
    _description = "Wizard to create Invoices from several POS Tickets"

    """
    """

    def _get_journal(self, cr, uid, context=None):
        obj_journal = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        if context is None:
            context = {}
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        journal = obj_journal.search(cr, uid, [('type', '=', 'sale'), ('company_id','=',company_id)], limit=1, context=context)
        return journal and journal[0] or False
	
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(pos_order_invoice_wizard, self).default_get(cr, uid, fields, context=context)
        record_ids = context.get('active_ids', [])
        pos_order_obj = self.pool.get('pos.order')
        if not record_ids:
            return {}
        tickets = []
        for ticket in pos_order_obj.browse(cr, uid, record_ids, context):
            if ticket.state !='paid':
                continue
            tickets.append({
					'ticket_id'		: ticket.id,
					'date_order'	:  ticket.date_order,
					'session_id'	:  ticket.session_id.id,
					'pos_reference'	:  ticket.pos_reference,
					'user_id'		:  ticket.user_id.id,
                    'partner_id'	:  ticket.partner_id and ticket.partner_id.id or False,
					'amount_total'	:  ticket.amount_total,
					'invoice_2_general_public' : ticket.partner_id.invoice_2_general_public if ticket.partner_id else True,
					
					})
        res.update(ticket_ids=tickets)
        return res

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        res = {}
        cr.execute("""SELECT p.id
                      FROM account_period p
                      where p.date_start <= NOW()
					  and p.date_stop >= NOW()
                      AND p.special = false
					  AND p.company_id = %s
					  LIMIT 1
			""" % (self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id))
        data = cr.fetchall()
        period = data and data[0] or False
        return period

    _columns = {
	   'date'		: fields.date('Date', help='This date will be used as the invoice date and period will be chosen accordingly!', required=True),
       'period_id'	: fields.many2one('account.period', 'Force period', required=True),
       'journal_id'	: fields.many2one('account.journal', 'Invoice Journal', help='You can select here the journal to use for the Invoice that will be created.', required=True),
       'ticket_ids'	: fields.one2many('pos.order.invoice_wizard.line','wiz_id','Tickets to Invoice', required=True),
    }

    _defaults = {
        'date': lambda *a	: time.strftime('%Y-%m-%d'),
        'journal_id'		: _get_journal,
		'period_id'			: _get_period,
			}
	
	
    def on_change_date(self, cr, uid, ids, date=False, context=None):
        if context is None: context = {}
        res = {}
        if not date:
            return res
        cr.execute("""SELECT p.id
                      FROM account_period p
                      where p.date_start <= '%s'
					  and p.date_stop >= '%s'
                      AND p.special = false
					  AND p.company_id = %s
					  LIMIT 1
			""" % (date, date, self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id))
        data = cr.fetchall()
        period = data and data[0] or False
        return {'value': {'period_id': period}}

	
    def create_invoice(self, cr, uid, ids, context=None):
        if context is None: context = {}
        for rec in self.browse(cr, uid, ids):
            ids_to_set_as_general_public, ids_to_invoice = [], []
            for line in rec.ticket_ids:
                ids_to_invoice.append(line.ticket_id.id)
                if line.invoice_2_general_public:
                    ids_to_set_as_general_public.append(line.ticket_id.id)
            if ids_to_set_as_general_public:
                cr.execute("update pos_order set invoice_2_general_public=true where id IN %s",(tuple(ids_to_set_as_general_public),))                
        if ids_to_invoice:
            return self.pool.get('pos.order').action_invoice3(cr, uid, ids_to_invoice, rec.date, rec.journal_id.id)
        return False

        
class pos_order_invoice_wizard_line(osv.osv_memory):
    _name = "pos.order.invoice_wizard.line"
    _description = "Wizard to create Invoices from several POS Tickets2"

    """
    """
		
    _columns = {
        'wiz_id': fields.many2one('pos.order.invoice_wizard','Wizard'),		
		'ticket_id' 	: fields.many2one('pos.order', 'POS Ticket'),
		'date_order'	: fields.related('ticket_id', 'date_order', type="datetime", string="Date", readonly=True),
		'session_id'	: fields.related('ticket_id', 'session_id', type="many2one", relation="pos.session", string="Session", readonly=True),
		'pos_reference'	: fields.related('ticket_id', 'pos_reference', type="char", size=64, string="Reference", readonly=True),
		'user_id'		: fields.related('ticket_id', 'user_id', type="many2one", relation="res.users", string="Salesman", readonly=True),
		'amount_total'	: fields.related('ticket_id', 'amount_total', type="float", string="Total", readonly=True),
        'partner_id'	: fields.related('ticket_id', 'session_id', type="many2one", relation="res.partner", string="Partner", readonly=True),
		'invoice_2_general_public': fields.boolean('General Public'),
		
    }


class pos_session(osv.osv):
    _inherit = "pos.session"

    
    def wkf_action_close2(self, cr, uid, ids, context=None):
        # Close CashBox
        if context is None:
            context = {}
        res = super(pos_session,self).wkf_action_close(cr, uid, ids, context)
        am_obj = self.pool.get('account.move')
        
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('use_as_general_public','=',1)], limit=1, context=context)
        if not partner_id:
            raise osv.except_osv(_('Error!'), _('Please configure a Partner as default for Use as General Public Partner.'))    

        addr = partner_obj.address_get(cr, uid, partner_id, ['delivery', 'invoice', 'contact'])
        partner_id = partner_obj.browse(cr, uid, addr['invoice'])[0].id
        print "partner_id: ", partner_id
        
        
        for record in self.browse(cr, uid, ids, context=context):
            for st in record.statement_ids:
                if st.journal_id.pos_group_entries_by_statement:
                    move_ids = []
                    cr.execute("select distinct move_id from account_move_line where statement_id=%s limit 1;" % (st.id))
                    move_id = cr.fetchall()[0]
                    print "move_id: ", move_id[0]
                    cr.execute("select distinct move_id from account_move_line where statement_id=%s;" % (st.id))
                    for move in am_obj.browse(cr, uid, cr.fetchall()):
                        #if move.state=='posted':
                        #    move.button_cancel(cr, uid, move.id)
                        move_id != move.id and move_ids.append(move.id)
                    
                    print "move_id: ", move_id
                    print "st.id: ", st.id
                    print "partner_id: ", partner_id
                    print "move_ids: ", move_ids
                    print "move_ids: ", ', '.join(move_ids)
                    (move_id, st.id, partner_id, st.id, ', '.join(move_ids))
                    sql = """
                                            drop table if exists argil_account_move_line;
                        create table argil_account_move_line
                        as
                        select now() create_date, now() write_date, create_uid, write_uid, date, company_id,
                            statement_id, partner_id, blocked, journal_id, centralisation, 
                            state, account_id, period_id, not_move_diot, ref, 'Pagos de Sesion: ' || ref as name,
                            %s::integer as move_id,
                            case 
                            when sum(debit) - sum(credit) > 0 then sum(debit) - sum(credit)
                            else 0
                            end::float debit,
                            case 
                            when sum(credit) - sum(debit) > 0 then sum(credit) - sum(debit)
                            else 0
                            end::float credit
                            from account_move_line
                            where statement_id=%s
                            group by create_uid, write_uid, date, company_id, 
                            statement_id, partner_id, blocked, journal_id, centralisation, 
                            state, account_id, period_id, not_move_diot, ref);
                        
                        update argil_account_move_line
                        set partner_id = %s 
                        where partner_id is null;
                        
                        delete from account_move_line where statement_id=%s;
                        delete from account_move where id in %s;
                        
                        insert into account_move_line
                        (
                            create_date, write_date, create_uid,  write_uid, date, company_id, 
                            statement_id, partner_id, blocked, journal_id, centralisation,
                            state, account_id, period_id, not_move_diot, ref, name, move_id,
                            debit, credit)
                        (select create_date, write_date, create_uid,  write_uid, date, company_id, 
                            statement_id, partner_id, blocked, journal_id, centralisation,
                            state, account_id, period_id, not_move_diot, ref, name, move_id,
                            debit, credit
                        from argil_account_move_line);
                        drop table if exists argil_account_move_line;

                    """ % (move_id, st.id, partner_id, st.id, ', '.join(move_ids))
                    print "sql: ", sql
                    cr.execute("""
                        drop table if exists argil_account_move_line;
                        create table argil_account_move_line
                        as
                        select now() create_date, now() write_date, create_uid, write_uid, date, company_id,
                            statement_id, partner_id, blocked, journal_id, centralisation, 
                            state, account_id, period_id, not_move_diot, ref, 'Pagos de Sesion: ' || ref as name,
                            %s::integer as move_id,
                            case 
                            when sum(debit) - sum(credit) > 0 then sum(debit) - sum(credit)
                            else 0
                            end::float debit,
                            case 
                            when sum(credit) - sum(debit) > 0 then sum(credit) - sum(debit)
                            else 0
                            end::float credit
                            from account_move_line
                            where statement_id=%s
                            group by create_uid, write_uid, date, company_id, 
                            statement_id, partner_id, blocked, journal_id, centralisation, 
                            state, account_id, period_id, not_move_diot, ref);
                        
                        update argil_account_move_line
                        set partner_id = %s 
                        where partner_id is null;
                        
                        delete from account_move_line where statement_id=%s;
                        delete from account_move where id in %s;
                        
                        insert into account_move_line
                        (
                            create_date, write_date, create_uid,  write_uid, date, company_id, 
                            statement_id, partner_id, blocked, journal_id, centralisation,
                            state, account_id, period_id, not_move_diot, ref, name, move_id,
                            debit, credit)
                        (select create_date, write_date, create_uid,  write_uid, date, company_id, 
                            statement_id, partner_id, blocked, journal_id, centralisation,
                            state, account_id, period_id, not_move_diot, ref, name, move_id,
                            debit, credit
                        from argil_account_move_line);
                        drop table if exists argil_account_move_line;

                    """ % (move_id, st.id, partner_id, st.id, ', '.join(move_ids)))                    

        return res