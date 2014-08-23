from django.conf.urls.defaults import *
from wouso.interface.cpanel import get_cpanel_games

upat = [
    url(r'^$', 'games.dashboard', name='dashboard'),
    url(r'^customization/$', 'games.customization', name='customization'),
    url(r'^display/$', 'games.display', name='cpanel_display'),

    url(r'^qpool/$', 'games.qpool_home', name='qpool_home'),
    url(r'^qpool/(?P<page>\d+)/$', 'games.qpool_home', name='qpool_home'),
    url(r'^qpool/tag_questions/$', 'games.qpool_tag_questions', name='tag_questions'),
    url(r'^qpool/edit/(?P<pk>\d+)/add_answer', 'games.qpool_add_answer', name='add_answer'),
    url(r'^qpool/edit/(?P<id>\d+)/$', 'games.qpool_edit', name='question_edit'),
    url(r'^qpool/del/(?P<id>\d+)/$', 'games.qpool_delete', name='question_del'),
    url(r'^qpool/del/(?P<question_id>\d+)/(?P<answer_id>\d+)/$', 'games.qpool_delete_answer', name='answer_del'),
    url(r'^qpool/set_active_categories', 'games.qpool_set_active_categories', name='set_active_categories'),
    url(r'^qpool/new/$', 'games.qpool_new', name='question_new'),
    url(r'^qpool/switch_active/(?P<id>\d+)/$', 'games.question_switch', name='switch_active'),
    url(r'^qpool/importer/$', 'games.qpool_importer', name='importer'),
    url(r'^qpool/importer/send$', 'games.qpool_import_from_upload', name='importer_send'),
    url(r'^qpool/exporter/(?P<cat>\w+)/$', 'games.qpool_export', name='qpool_export'),
    url(r'^qpool/qotd/schedule$', 'games.qotd_schedule', name='qotd_schedule'),
    url(r'^qpool/cat/(?P<cat>\w+)/$', 'games.qpool_home', name='qpool_home'),
    url(r'^qpool/cat/(?P<cat>\w+)/(?P<page>\d+)/$', 'games.qpool_home', name='qpool_home'),
    url(r'^qpool/cat/(?P<cat>\w+)/tag=(?P<tag>\d+)/$', 'games.qpool_home', name='qpool_home'),
    url(r'^qpool/qpool_remove_all/(?P<cat>\w+)/$', 'games.qpool_remove_all', name='remove_all'),
    url(r'^qpool/manage_tags/$', 'games.qpool_managetags', name='qpool_manage_tags'),
    url(r'^qpool/newtag/$','games.qpool_add_tag', name='qpool_add_tag'),
    url(r'^qpool/edit_tag/(?P<pk>\d+)/$', 'games.qpool_edit_tag', name='qpool_edit_tag'),
    url(r'^qpool/del_tag/(?P<tag>\d+)/$', 'games.qpool_delete_tag', name='qpool_del_tag'),
    url(r'^qpool/set_tag/$', 'games.qpool_settag', name='qpool_set_tag'),
    url(r'^qpool/action/$', 'games.qpool_actions', name='qpool_actions'),


    url(r'^artifact/$', 'games.artifact_home', name='artifact_home'),
    url(r'^artifact/user_set/(?P<id>\d+)/$', 'games.artifactset', name='artifact_set'),
    url(r'^artifact/new/$', 'games.artifact_edit', name='artifact_new'),
    url(r'^artifact/edit/(?P<id>\d+)/$', 'games.artifact_edit', name='artifact_edit'),
    url(r'^artifact/del/(?P<id>\d+)/$', 'games.artifact_del', name='artifact_del'),
    url(r'^artifact/(?P<group>\w+)/$', 'games.artifact_home', name='artifact_home'),

    url(r'^spells/$','games.spells', name='spells'),
    url(r'^edit_spell/(?P<pk>\d+)$','games.edit_spell',name='edit_spell'),
    url(r'^add_spell/$', 'games.add_spell',name='add_spell'),
    url(r'^spells/del/(?P<id>\d+)/$', 'games.spell_delete', name='spell_dell'),

    url(r'^formulas/$','games.formulas',name='formulas'),
    url(r'^edit_formula/(?P<pk>\d+)/$','games.edit_formula',name='edit_formula'),
    url(r'^formulas/del/(?P<id>\d+)/$','games.formula_delete',name='formula_del'),
    url(r'^add_formula/$','games.add_formula',name='add_formula'),

    url(r'^group/set/(?P<id>\d*)/$', 'games.groupset', name='group_set'),
    url(r'^staff/toggle/(?P<id>\d+)/$', 'games.stafftoggle', name='staff_toggle'),

    url(r'^players/$', 'games.players', name='all_players'),
    url(r'^players/fwd/$', 'games.fwd', name='manage_fwd'),
    url(r'^player/(?P<player_id>\d+)/bonus/$', 'games.bonus', name='bonus'),
    url(r'^add_player/$', 'games.add_player', name='add_player'),
    url(r'^manage_player/(?P<pk>\d+)/$', 'games.manage_player', name='manage_player'),
    url(r'^infractions/(?P<user_id>\d+)/$', 'games.infraction_history', name='infraction_history'),
    url(r'^infractions_clear/(?P<user_id>\d+)/(?P<infraction_id>\d+)/$', 'games.infraction_clear', name='infraction_clear'),
    url(r'^infractions_recheck/$', 'games.infraction_recheck', name='infraction_recheck'),
    url(r'^manage_player/(?P<user_id>\d+)/$', 'games.manage_player', name='manage_player'),
    url(r'^races/all/$', 'games.races_groups',
        name='races_groups'),
    url(r'^races/add/$', 'games.races_add',
        name='races_add'),
    url(r'^races/groups/add/$', 'games.group_add',
        name='group_add'),
    url(r'^roles/$', 'games.roles', name='roles'),
    url(r'^roles/(?P<id>\d+)/$', 'games.roles_update', name='roles_update'),
    url(r'^roles/(?P<id>\d+)/kick/player=(?P<player_id>\d+)/$', 'games.roles_update_kick', name='roles_update_kick'),
    url(r'^roles_create$', 'games.roles_create',
name='roles_create'),

    # misc
    url(r'^tools/clear-cache/$', 'games.clear_cache', name='clear_cache'),

    url(r'^reports/$', 'games.reports', name='reports'),
    url(r'^reports/edit/(?P<pk>\d+)/$', 'games.edit_report', name='edit_report'),

    url(r'^system_message/group/(?P<group>\d+)/$', 'games.system_message_group', name='system_message_group'),

    url(r'^impersonate/(?P<player_id>\d+)/$', 'games.impersonate', name='impersonate'),
    url(r'^impersonate/clear/$', 'games.clean_impersonation', name='impersonate_clear'),

    # Static pages
    url(r'^static_pages/$', 'static.static_pages', name='static_pages'),
    url(r'^add_static_page/$', 'static.add_static_page', name='add_static_page'),
    url(r'^edit_static_page/(?P<pk>\d+)/$', 'static.edit_static_page', name='edit_static_page'),
    url(r'^del_static_page/(?P<pk>\d+)/$', 'static.del_static_page', name='del_static_page'),

    # News Items
    url(r'^news/$', 'static.news', name='news'),
    url(r'^add_news/$', 'static.add_news', name='add_news'),
    url(r'^edit_news/(?P<pk>\d+)/$', 'static.edit_news', name='edit_news'),
    url(r'^del_news/(?P<pk>\d+)/$', 'static.del_news', name='del_news'),
]

for g in get_cpanel_games():
    upat.append((r'games/{game}/'.format(game=g), include('wouso.games.{game}.cpanel_urls'.format(game=g))))
upat.append(url(r'^games/', 'games.games', name='games_home'))

urlpatterns = patterns('wouso.interface.cpanel.views', *upat)
