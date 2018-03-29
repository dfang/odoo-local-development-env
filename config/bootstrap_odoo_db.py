#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to bootstrap an Odoo database."""
import odoorpc
import logging

# Odoo connection
SUPER_PWD = 'admin'
HOST = 'localhost'
PORT = 8069
DB = 'odoo_production'
USER = 'admin'
PWD = 'password'
LANG = 'en_US'
COMPANY = u"武汉守正科级有限公司"
TIMEZONE = u"Asia/Shanghai"

MODULES_TO_INSTALL = [
    'admin_auto_debug_mode', 'debranding', 'developer_tweaks', 'fusion_admin'
]

MODULES_TO_UNINSTALL = [
    'im_livechat'
]

def get_session(login=True):
    odoo = odoorpc.ODOO(HOST, port=PORT)
    odoo.config['timeout'] = 120
    if login:
        odoo.login(DB, USER, PWD)
    return odoo


def create_database():
    logging.warning('Watch out! creating database ......')
    odoo = get_session(login=False)
    if DB not in odoo.db.list():
        odoo.db.create(
            SUPER_PWD, DB, demo=False, lang=LANG, admin_password=PWD)


def uninstall_modules():
    logging.warning('Watch out! uninstalling modules ......')
    odoo = get_session()
    Module = odoo.env['ir.module.module']
    for module_name in MODULES_TO_UNINSTALL:
        module_ids = Module.search(
            [('name', '=', module_name),
             ('state', 'in', ['installed', 'to upgrade',
                              'to remove', 'to install'])])
        if module_ids:
            Module.button_immediate_uninstall(module_ids)


def update_company():
    logging.warning('Watch out! updating company information')
    odoo = get_session()
    company = odoo.env.user.company_id
    company.name = COMPANY

def load_translation():
    odoo = get_session()
    LangInstall = odoo.env['base.language.install']
    lang_id = LangInstall.create({'lang': 'zh_CN'})
    LangInstall.lang_install([lang_id])

def update_admin_user():
    logging.warning('Watch out! updating super user ......')
    odoo = get_session()
    admin = odoo.env.user
    # group_technical_feature = odoo.env.ref('base.group_no_one')
    # group_sale_manager = odoo.env.ref('base.group_sale_manager')
    # if group_technical_feature not in admin.groups_id:
    #     admin.groups_id += group_technical_feature
    # if group_sale_manager not in admin.groups_id:
    #     admin.groups_id += group_sale_manager
    if not admin.tz:
        admin.tz = TIMEZONE
    # import pdb; pdb.set_trace()
    admin.lang = 'zh_CN'


def install_modules():
    logging.warning('Watch out! installing default modules .....')
    odoo = get_session()
    # Installation
    Module = odoo.env['ir.module.module']
    for module_name in MODULES_TO_INSTALL:
        module_ids = Module.search(
            [('name', '=', module_name),
             ('state', 'not in', ['installed', 'to upgrade'])])
        if module_ids:
            Module.button_immediate_install(module_ids)

def configure_account():
    logging.warning('Watch out! configuring account')
    odoo = get_session()
    #   account.installer
    Wizard = odoo.env['account.installer']
    config = Wizard.default_get(list(Wizard.fields_get()))
    config['charts'] = 'l10n_fr'
    wiz_id = Wizard.create(config)
    Wizard.action_next([wiz_id])
    #   wizard.multi.charts.accounts
    Wizard = odoo.env['wizard.multi.charts.accounts']
    config = Wizard.default_get(list(Wizard.fields_get()))
    config['chart_template_id'] = odoo.env.ref(
        'l10n_fr.l10n_fr_pcg_chart_template').id
    values = Wizard.onchange_chart_template_id(
        [], config['chart_template_id'])['value']
    config.update(values)
    config['sale_tax'] = odoo.env.ref('l10n_fr.tva_normale').id
    config['purchase_tax'] = odoo.env.ref('l10n_fr.tva_acq_normale').id
    config['code_digits'] = 8
    del config['bank_accounts_id']
    wiz_id = Wizard.create(config)
    try:
        Wizard.action_next([wiz_id])
    except odoorpc.error.RPCError:
        print "Accounting already configured"


def main():
    create_database()
    # uninstall_modules()
    load_translation()
    update_company()
    update_admin_user()
    install_modules()
    # configure_account()


if __name__ == '__main__':
    main()

# >> python
# import odoorpc
# odoo = odoorpc.ODOO('localhost', port=8069)
# odoo.login('test', 'admin', 'password')
