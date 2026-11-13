# -*- coding: utf-8 -*-
"""Socle commun des tests de la caisse du restaurant (spécification, partie 6.2).

La caisse de test de ``TestPoSCommon`` passe en « Service à table contrôlé ».
Cinq employés aux quatre niveaux, **sans courriel** (le client n'en a pas pour
ses serveurs) : Awa 1111 et Moussa 2222 (serveurs), Carine 3333 (caissière),
Paul 4444 (chef de salle), Fanta 5555 (manager).

Deux comptes Odoo, comme les pose AITE (partie 4.4) :
* le compte de la caisse : « Utilisateur » du Point de Vente, avec un courriel
  et le droit Facturation (sans lui, les entrées et sorties d'espèces
  échouent) ; aucun droit sur les Employés ;
* le compte du manager : Administrateur du Point de Vente et Employés
  « Agent » (il saisit les niveaux et les codes).
"""
import json
from uuid import uuid4

from odoo import fields

from odoo.addons.point_of_sale.tests.common import TestPoSCommon


class Addition:
    """La copie d'une addition sur un poste de la caisse (incrément 3).

    Elle tient ce que la caisse envoie au serveur (``sync_from_ui``) : les
    lignes, la dernière préparation envoyée (``last_order_preparation_change``)
    et les champs de l'addition ; après chaque synchronisation, elle reprend
    ce que le serveur rend, comme le fait la caisse. Seules les lignes
    modifiées depuis la dernière synchronisation partent en ``[1, id, …]`` ;
    une ligne retirée part en ``[2, id]``. Une copie peut donc rester
    ancienne : c'est le cas d'un second poste.
    """

    def __init__(self, table=None, personnes=4, ouverte_par=None, nom=False):
        self.uuid = str(uuid4())
        self.valeurs = {
            'table_id': table.id if table else False,
            'customer_count': personnes,
            'aite_ouverte_par_id': ouverte_par.id if ouverte_par else False,
            'employee_id': ouverte_par.id if ouverte_par else False,
            'floating_order_name': nom,
            'aite_heure_ouverture': False,
            'aite_origine_uuid': False,
        }
        self.lignes = {}        # uuid de ligne → {'id', 'produit', 'qty', 'modifiee'}
        self.supprimees = []    # identifiants des lignes retirées depuis la synchronisation
        self.preparation = {'lines': {}, 'metadata': {}, 'generalNote': '',
                            'sittingMode': 'dine in'}
        self.record = None

    def ajouter(self, produit, qty):
        uuid = str(uuid4())
        self.lignes[uuid] = {'id': False, 'produit': produit, 'qty': qty, 'modifiee': True}
        return uuid

    def changer(self, uuid, qty):
        self.lignes[uuid].update(qty=qty, modifiee=True)

    def supprimer(self, uuid):
        ligne = self.lignes.pop(uuid)
        if ligne['id']:
            self.supprimees.append(ligne['id'])

    def envoyer(self):
        """« J'envoie » : la caisse note ce qui est parti
        (``updateLastOrderChange``)."""
        self.preparation['lines'] = {
            uuid: {'uuid': uuid, 'product_id': ligne['produit'].id,
                   'name': ligne['produit'].display_name, 'note': '',
                   'quantity': ligne['qty'], 'attribute_value_ids': []}
            for uuid, ligne in self.lignes.items()
        }
        self.preparation['metadata'] = {
            'serverDate': fields.Datetime.to_string(fields.Datetime.now())}

    def quantite(self, uuid):
        return self.lignes[uuid]['qty']


class RestaurantCommon(TestPoSCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.basic_config
        cls.config.write({
            'module_pos_restaurant': True,
            'module_pos_hr': True,
            'aite_mode_restaurant': True,
        })

        Employe = cls.env['hr.employee']

        def employe(nom, code, niveau):
            return Employe.create({
                'name': nom,
                'pin': code,
                'aite_niveau_caisse': niveau,
                'company_id': cls.company.id,
            })

        cls.awa = employe("Awa", '1111', 'serveur')
        cls.moussa = employe("Moussa", '2222', 'serveur')
        cls.carine = employe("Carine", '3333', 'caissiere')
        cls.paul = employe("Paul", '4444', 'superviseur')
        cls.fanta = employe("Fanta", '5555', 'manager')
        cls.equipe = cls.awa | cls.moussa | cls.carine | cls.paul | cls.fanta

        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.compte_caisse = Users.create({
            'name': "Caisse du restaurant",
            'login': 'aite_caisse_resto',
            'email': 'caisse@restaurant.example',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('point_of_sale.group_pos_user').id,
                cls.env.ref('account.group_account_invoice').id,
            ])],
        })
        cls.compte_manager = Users.create({
            'name': "Manager du restaurant",
            'login': 'aite_manager_resto',
            'email': 'manager@restaurant.example',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('point_of_sale.group_pos_manager').id,
                cls.env.ref('hr.group_hr_user').id,
            ])],
        })

        # Le plan et la carte (incrément 3) : la salle posée par pos_restaurant
        # reçoit les tables 7 et 12 ; deux produits sans taxe.
        salle = cls.config.floor_ids[:1]
        Table = cls.env['restaurant.table']
        cls.table_7 = Table.create({'floor_id': salle.id, 'table_number': 7, 'seats': 4})
        cls.table_12 = Table.create({'floor_id': salle.id, 'table_number': 12, 'seats': 4})
        Produit = cls.env['product.product']
        cls.castel = Produit.create({
            'name': "Castel", 'type': 'consu', 'available_in_pos': True,
            'list_price': 1000.0, 'taxes_id': [(5, 0, 0)]})
        cls.poulet = Produit.create({
            'name': "Poulet DG", 'type': 'consu', 'available_in_pos': True,
            'list_price': 6500.0, 'taxes_id': [(5, 0, 0)]})

    # ------------------------------------------------------------------
    # Aides
    # ------------------------------------------------------------------

    def _ouvrir_session(self, config=None, code='3333'):
        """Session ouverte comme le fait la caisse : en mode, le code d'une
        personne qui peut ouvrir (Carine par défaut) est vérifié par le
        serveur (``aite_ouvrir_caisse``), puis le contrôle d'ouverture
        d'Odoo est validé (incrément 2)."""
        config = config or self.config
        config.open_ui()
        session = config.current_session_id
        caisse = session.with_user(self.compte_caisse)
        if config._aite_actif():
            self.assertNotIn('erreur', caisse.aite_ouvrir_caisse(code))
        caisse.set_opening_control(0, None)
        return session

    def _commande_caisse(self, addition, employe=None, contexte=True, deplacement=False,
                         etat='draft', payer=None, en_plus=None, en_plus_lignes=None,
                         config=None):
        """L'addition ``addition`` telle que la caisse l'envoie
        (``sync_from_ui``), sous le compte de la caisse, avec le contexte
        posé par la caisse : ``aite_employee_id`` (la personne identifiée
        sur le poste) et ``aite_deplacement`` (division, réunion).

        ``employe`` est aussi l'employé de l'addition (``employee_id`` : pos_hr
        y met la personne qui ajoute un produit, et celle qui valide le
        paiement) ; ``contexte=False`` l'envoie sans le contexte d'AITE
        (synchronisation lancée par Odoo, poste verrouillé). ``payer`` : le
        mode de paiement d'un encaissement du total (``etat='paid'``).
        ``en_plus`` et ``en_plus_lignes`` : des valeurs de plus dans
        l'addition et dans chaque ligne envoyée (requête forgée). ``config`` :
        une autre caisse que celle du restaurant. Rend l'addition enregistrée
        sur le serveur ; la copie ``addition`` reprend ce que le serveur
        rend."""
        config = config or self.config
        session = config.current_session_id
        maintenant = fields.Datetime.to_string(fields.Datetime.now())
        if employe:
            addition.valeurs['employee_id'] = employe.id
        lignes, total = [], 0.0
        for uuid, ligne in addition.lignes.items():
            prix = ligne['produit'].lst_price
            total += prix * ligne['qty']
            valeurs = {
                'uuid': uuid, 'product_id': ligne['produit'].id, 'qty': ligne['qty'],
                'price_unit': prix, 'discount': 0.0, 'tax_ids': [(6, 0, [])],
                'price_subtotal': prix * ligne['qty'],
                'price_subtotal_incl': prix * ligne['qty'],
                'full_product_name': ligne['produit'].display_name,
                **(en_plus_lignes or {}),
            }
            if not ligne['id']:
                lignes.append([0, 0, valeurs])
            elif ligne['modifiee'] or en_plus_lignes:
                lignes.append([1, ligne['id'], valeurs])
        lignes += [[2, identifiant] for identifiant in addition.supprimees]
        paiements = []
        if payer:
            paiements = [[0, 0, {'amount': total, 'name': maintenant,
                                 'payment_method_id': payer.id}]]
        donnees = {
            'uuid': addition.uuid, 'name': "Commande %s" % addition.uuid,
            'session_id': session.id, 'state': etat,
            'user_id': self.compte_caisse.id, 'pricelist_id': config.pricelist_id.id,
            'fiscal_position_id': False, 'sequence_number': 1, 'to_invoice': False,
            'date_order': maintenant, 'amount_tax': 0.0, 'amount_total': total,
            'amount_paid': total if payer else 0.0, 'amount_return': 0.0,
            'last_order_preparation_change': json.dumps(addition.preparation),
            'lines': lignes, 'payment_ids': paiements,
            **addition.valeurs,
            **(en_plus or {}),
        }
        contexte_caisse = {'config_id': config.id}
        if contexte:
            contexte_caisse.update(aite_employee_id=employe.id if employe else False,
                                   aite_deplacement=deplacement)
        reponse = self.env['pos.order'].with_user(self.compte_caisse).with_context(
            **contexte_caisse).sync_from_ui([donnees])
        # Ce que la caisse reçoit : identifiants des lignes, préparation et
        # champs de l'addition tels que le serveur les a écrits.
        commande = self.env['pos.order'].browse(reponse['pos.order'][0]['id'])
        lu = reponse['pos.order'][0]
        par_uuid = {ligne['uuid']: ligne['id'] for ligne in reponse['pos.order.line']}
        for uuid, ligne in addition.lignes.items():
            ligne.update(id=par_uuid.get(uuid, ligne['id']), modifiee=False)
        addition.supprimees = []
        addition.preparation = json.loads(lu['last_order_preparation_change'] or '{}') \
            or addition.preparation
        for champ in ('customer_count', 'aite_ouverte_par_id', 'aite_origine_uuid',
                      'employee_id', 'table_id'):
            if champ in lu:
                addition.valeurs[champ] = lu[champ]
        heure = lu.get('aite_heure_ouverture')
        addition.valeurs['aite_heure_ouverture'] = (
            fields.Datetime.to_string(heure) if heure and not isinstance(heure, str) else heure)
        addition.record = commande
        return commande

    def _charger_caisse(self, config=None, user=None):
        """Ce que la caisse reçoit au démarrage : ``load_data`` sous le
        compte de la caisse (sans droit sur les Employés)."""
        config = config or self.config
        config.open_ui()
        session = config.current_session_id
        donnees = session.with_user(user or self.compte_caisse).load_data(
            ['pos.config', 'hr.employee'])
        return donnees
