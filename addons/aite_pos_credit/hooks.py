# -*- coding: utf-8 -*-
"""
Hook post-installation : prépare la méthode de paiement « ardoise ».

La configuration comptable (journaux, comptes) dépend du plan comptable de
chaque société et n'est pas connue au moment du chargement des données XML.
Ce hook, exécuté après l'installation, crée pour chaque société dotée d'un
plan comptable :

* un compte client dédié si nécessaire (sinon réutilise le compte client
  par défaut) ;
* une méthode de paiement POS « Ardoise / Crédit » de type *pay_later*
  pointant sur ce compte ;
* l'ajout de cette méthode aux POS existants.

Tout est idempotent et défensif : en l'absence de comptabilité configurée,
le hook s'abstient sans lever d'erreur.
"""
from odoo import api, SUPERUSER_ID, _


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
        # Compte client (411) à utiliser pour l'encours.
        receivable = company._get_pos_credit_account()
        if not receivable:
            # Pas de compte client par défaut → on cherche un asset_receivable.
            receivable = env['account.account'].search([
                ('account_type', '=', 'asset_receivable'),
                ('company_id', '=', company.id),
            ], limit=1)
        if not receivable:
            # Comptabilité non configurée : on s'abstient pour cette société.
            return

        vals = {
            'name': _("Ardoise / Crédit"),
            'company_id': company.id,
            'is_aite_credit': True,
        }
        # Le champ ``type`` existe sur les méthodes POS récentes ; on tente
        # de positionner pay_later, avec repli silencieux.
        if 'type' in PaymentMethod._fields:
            vals['type'] = 'pay_later'
        if 'receivable_account_id' in PaymentMethod._fields:
            vals['receivable_account_id'] = receivable.id

        method = PaymentMethod.create(vals)

        # Mémorise le compte client au niveau société si vide.
        if not company.pos_credit_account_id:
            company.pos_credit_account_id = receivable.id

    # Rattache la méthode aux POS existants de la société.
    configs = env['pos.config'].search([('company_id', '=', company.id)])
    for config in configs:
        if method not in config.payment_method_ids:
            try:
                config.payment_method_ids = [(4, method.id)]
            except Exception:
                # Certaines contraintes (devise/journal) peuvent bloquer :
                # on n'interrompt pas l'installation.
                pass


def post_init_hook(env):
    """Point d'entrée appelé par Odoo après installation du module."""
    for company in env['res.company'].search([]):
        try:
            _setup_company(env, company)
        except Exception:
            # Robustesse : un souci sur une société ne casse pas l'install.
            continue
