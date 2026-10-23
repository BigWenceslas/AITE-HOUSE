# -*- coding: utf-8 -*-
"""
Hook post-installation : prépare la méthode de paiement « ardoise ».

La configuration comptable (journaux, comptes) dépend du plan comptable de
chaque société et n'est pas connue au moment du chargement des données XML.
Ce hook, exécuté après l'installation, prépare pour chaque société :

* le compte client à utiliser, quand le plan comptable est déjà là (celui
  des réglages, sinon le compte client par défaut de la société, sinon le
  premier compte client du plan) ;
* une méthode de paiement POS « Ardoise client » de type *pay_later*
  (« Compte client » : sans journal, « Identifier le client » coché)
  pointant sur ce compte s'il est connu ;
* l'ajout de cette méthode aux POS existants.

Tout est idempotent et défensif : sans plan comptable (cas d'une base
neuve, où Odoo 18 charge le plan après les hooks), le mode est créé sans
compte imposé ; un échec inattendu n'interrompt pas l'installation mais il
est journalisé (avertissement), pour que l'absence du mode « Ardoise
client » ne passe pas inaperçue.
"""
import logging

_logger = logging.getLogger(__name__)

# Nom du mode créé à l'installation : celui du cahier de recette (F01) et du
# jeu de démonstration (``aite_demo_data`` le retrouve par ce nom et ne le
# duplique pas).
CREDIT_METHOD_NAME = "Ardoise client"


def _setup_company(env, company):
    PaymentMethod = env['pos.payment.method']

    # Méthode déjà créée ?
    existing = PaymentMethod.search([
        ('is_aite_credit', '=', True),
        ('company_id', '=', company.id),
    ], limit=1)
    if existing:
        method = existing
    else:
        # Compte client (411) à utiliser pour l'encours : celui de la
        # société, sinon le compte client par défaut (fiche de la société).
        receivable = company._get_pos_credit_account(company.partner_id)
        if not receivable:
            # Pas de compte client par défaut → on cherche un asset_receivable.
            # Odoo 18 : un compte est partagé entre sociétés (``company_ids``,
            # many2many) ; ``company_id`` n'existe plus et la recherche
            # levait une erreur avalée — le mode n'était jamais créé.
            receivable = env['account.account'].search([
                ('account_type', '=', 'asset_receivable'),
                ('company_ids', 'in', company.id),
            ], limit=1)
        # Pas de compte client (encore) : le mode est créé quand même. Sur
        # une base neuve, Odoo 18 ne charge le plan comptable qu'à la fin de
        # l'installation (``_register_hook`` du module account), APRÈS ce
        # hook : s'abstenir laissait la base sans « Ardoise client ». Mode
        # « Identifier le client » oblige, la créance de session va de toute
        # façon au compte client de chaque client.

        vals = {
            'name': CREDIT_METHOD_NAME,
            'company_id': company.id,
            'is_aite_credit': True,
            # Comme le « Compte client » standard d'Odoo 18 : sans journal,
            # client obligatoire et créance au nom du client. Sans cette
            # case, la fiche du mode exige un journal et refuse d'être
            # enregistrée.
            'split_transactions': True,
        }
        # Le champ ``type`` existe sur les méthodes POS récentes ; on tente
        # de positionner pay_later, avec repli silencieux.
        if 'type' in PaymentMethod._fields:
            vals['type'] = 'pay_later'
        if receivable and 'receivable_account_id' in PaymentMethod._fields:
            vals['receivable_account_id'] = receivable.id

        method = PaymentMethod.create(vals)

        # Mémorise le compte client au niveau société si vide.
        if receivable and not company.pos_credit_account_id:
            company.pos_credit_account_id = receivable.id

    # Rattache la méthode aux POS existants de la société.
    configs = env['pos.config'].search([('company_id', '=', company.id)])
    for config in configs:
        if method not in config.payment_method_ids:
            try:
                with env.cr.savepoint():
                    config.payment_method_ids = [(4, method.id)]
            except Exception:
                # Certaines contraintes (devise/journal, session ouverte)
                # peuvent bloquer : on n'interrompt pas l'installation.
                _logger.warning(
                    "POS Crédit : mode « %s » non ajouté à la caisse %s.",
                    CREDIT_METHOD_NAME, config.name, exc_info=True)


def post_init_hook(env):
    """Point d'entrée appelé par Odoo après installation du module."""
    for company in env['res.company'].search([]):
        try:
            # Point de sauvegarde : une erreur SQL sur une société ne laisse
            # pas la transaction de l'installation dans un état avorté.
            with env.cr.savepoint():
                _setup_company(env, company)
        except Exception:
            # Robustesse : un souci sur une société ne casse pas l'install,
            # mais il est journalisé (il était avalé sans trace).
            _logger.warning(
                "POS Crédit : mode « %s » non créé pour la société %s.",
                CREDIT_METHOD_NAME, company.name, exc_info=True)
