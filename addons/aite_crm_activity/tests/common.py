# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, new_test_user


class AiteCrmActivityCase(TransactionCase):
    """ Jeu d'essai isolé dans sa propre équipe commerciale, pour que les
    comptages ne dépendent pas des données déjà présentes dans la base.

    - manager      : responsable commercial (voit tout) ;
    - alice, bob   : commerciaux limités à leurs propres opportunités ;
    - lead_alice   : 1 activité en retard + 1 du jour + 1 lointaine (J+30) ;
    - lead_bob     : 1 activité à venir (J+3) ;
    - lead_quiet   : opportunité d'Alice sans activité ;
    - lead_won     : opportunité gagnée sans activité (pas « à relancer ») ;
    - act_on_bob_for_alice : activité assignée à Alice sur l'opportunité
      de Bob, qu'elle ne peut pas ouvrir.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, mail_activity_quick_update=True,
                                       mail_create_nolog=True, tracking_disable=True))
        # Les utilisateurs de test sont en UTC : « aujourd'hui » est le même pour tous.
        cls.today = fields.Date.context_today(cls.env['res.users'].with_context(tz='UTC'))
        cls.manager = new_test_user(
            cls.env, login='aite_cad_manager', groups='sales_team.group_sale_manager',
            name="Responsable Commercial", email='manager@aite.example', tz='UTC')
        cls.alice = new_test_user(
            cls.env, login='aite_cad_alice', groups='sales_team.group_sale_salesman',
            name="Alice Commerciale", email='alice@aite.example', tz='UTC')
        cls.bob = new_test_user(
            cls.env, login='aite_cad_bob', groups='sales_team.group_sale_salesman',
            name="Bob Commercial", email='bob@aite.example', tz='UTC')
        cls.team = cls.env['crm.team'].create({
            'name': "Équipe de test AITE",
            'member_ids': [(6, 0, (cls.alice | cls.bob).ids)],
        })
        cls.partner = cls.env['res.partner'].create({'name': "Client Test"})
        Lead = cls.env['crm.lead']
        cls.lead_alice = Lead.create({
            'name': "Opportunité Alice", 'type': 'opportunity', 'user_id': cls.alice.id,
            'team_id': cls.team.id, 'partner_id': cls.partner.id, 'expected_revenue': 1500000,
        })
        cls.lead_bob = Lead.create({
            'name': "Opportunité Bob", 'type': 'opportunity', 'user_id': cls.bob.id,
            'team_id': cls.team.id, 'expected_revenue': 800000,
        })
        cls.lead_quiet = Lead.create({
            'name': "Opportunité à relancer", 'type': 'opportunity', 'user_id': cls.alice.id,
            'team_id': cls.team.id,
        })
        cls.lead_won = Lead.create({
            'name': "Opportunité gagnée", 'type': 'opportunity', 'user_id': cls.alice.id,
            'team_id': cls.team.id,
        })
        cls.lead_won.action_set_won()

        cls.type_call = cls.env.ref('mail.mail_activity_data_call')
        cls.type_todo = cls.env.ref('mail.mail_activity_data_todo')
        cls.act_overdue = cls._activity(cls.lead_alice, cls.alice, -2, cls.type_call, "Rappeler le client")
        cls.act_today = cls._activity(cls.lead_alice, cls.alice, 0, cls.type_todo, "Envoyer le devis")
        cls.act_far = cls._activity(cls.lead_alice, cls.alice, 30, cls.type_todo, "Point trimestriel")
        cls.act_bob = cls._activity(cls.lead_bob, cls.bob, 3, cls.type_call, "Démonstration")
        cls.act_on_bob_for_alice = cls._activity(cls.lead_bob, cls.alice, 1, cls.type_todo, "Aider Bob")

    @classmethod
    def _activity(cls, lead, user, days, activity_type, summary):
        return cls.env['mail.activity'].create({
            'res_model_id': cls.env['ir.model']._get_id('crm.lead'),
            'res_id': lead.id,
            'user_id': user.id,
            'activity_type_id': activity_type.id,
            'summary': summary,
            'date_deadline': cls.today + timedelta(days=days),
        })

    def dashboard(self, user=None, **filters):
        model = self.env['aite.crm.activity.dashboard']
        if user:
            model = model.with_user(user)
        filters.setdefault('team_id', self.team.id)
        return model.get_dashboard_data(filters)
