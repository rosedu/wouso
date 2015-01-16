from django.conf.urls.defaults import *
from wouso.interface.cpanel import get_cpanel_games

upat = [
    # Customization
    url(r'^$', 'wouso.interface.cpanel.views.status', name='status'),
    url(r'^customization/$', 'wouso.interface.cpanel.views.customization_home', name='customization_home'),
    url(r'^customization/games/$', 'wouso.interface.cpanel.views.customization_games', name='customization_games'),
    url(r'^customization/features/$', 'wouso.interface.cpanel.views.customization_features', name='customization_features'),
    url(r'^customization/display/$', 'wouso.interface.cpanel.views.customization_display', name='customization_display'),
    url(r'^customization/levels/$', 'wouso.interface.cpanel.views.customization_levels', name='customization_levels'),
    url(r'^customization/set_levels/$', 'wouso.interface.cpanel.views.customization_set_levels', name='customization_set_levels'),

    url(r'^leaderboards/$', 'wouso.interface.cpanel.views.leaderboards', name='leaderboards'),

    url(r'^karma/$', 'wouso.interface.cpanel.views.karma_view', name='karma'),
    url(r'^karma/group/(?P<group>\d+)/$', 'wouso.interface.cpanel.views.karma_group_view', name='karma_group'),

    url(r'^qpool/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/(?P<page>\d+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/tag_questions/$', 'wouso.interface.cpanel.views.qpool_tag_questions', name='tag_questions'),
    url(r'^qpool/del/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.qpool_delete', name='question_del'),
    url(r'^qpool/set_active_categories', 'wouso.interface.cpanel.views.qpool_set_active_categories', name='set_active_categories'),
    url(r'^qpool/switch_active/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.question_switch', name='switch_active'),
    url(r'^qpool/importer/$', 'wouso.interface.cpanel.views.qpool_importer', name='importer'),
    url(r'^qpool/importer/send$', 'wouso.interface.cpanel.views.qpool_import_from_upload', name='importer_send'),
    url(r'^qpool/exporter/(?P<cat>\w+)/$', 'wouso.interface.cpanel.views.qpool_export', name='qpool_export'),
    url(r'^qpool/qotd/schedule$', 'wouso.interface.cpanel.views.qotd_schedule', name='qotd_schedule'),
    url(r'^qpool/cat/(?P<cat>\w+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/cat/(?P<cat>\w+)/(?P<page>\d+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/cat/(?P<cat>\w+)/tag=(?P<tag>\d+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/qpool_remove_all/(?P<cat>\w+)/$', 'wouso.interface.cpanel.views.qpool_remove_all', name='remove_all'),
    url(r'^qpool/manage_tags/$', 'wouso.interface.cpanel.views.qpool_managetags', name='qpool_manage_tags'),
    url(r'^qpool/newtag/$','wouso.interface.cpanel.views.qpool_add_tag', name='qpool_add_tag'),
    url(r'^qpool/edit_tag/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.qpool_edit_tag', name='qpool_edit_tag'),
    url(r'^qpool/del_tag/(?P<tag>\d+)/$', 'wouso.interface.cpanel.views.qpool_delete_tag', name='qpool_del_tag'),
    url(r'^qpool/set_tag/$', 'wouso.interface.cpanel.views.qpool_settag', name='qpool_set_tag'),
    url(r'^qpool/action/$', 'wouso.interface.cpanel.views.qpool_actions', name='qpool_actions'),

    url(r'^qpool/add_question/$', 'wouso.interface.cpanel.views.add_question', name='add_question'),
    url(r'^qpool/edit_question/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.edit_question', name='edit_question'),

    url(r'^artifact/$', 'wouso.interface.cpanel.views.artifact_home', name='artifact_home'),
    url(r'^artifact/user_set/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.artifactset', name='artifact_set'),
    url(r'^artifact/new/$', 'wouso.interface.cpanel.views.artifact_edit', name='artifact_new'),
    url(r'^artifact/edit/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.artifact_edit', name='artifact_edit'),
    url(r'^artifact/del/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.artifact_del', name='artifact_del'),
    url(r'^artifact/(?P<group>\w+)/$', 'wouso.interface.cpanel.views.artifact_home', name='artifact_home'),

    url(r'^spells/$','wouso.interface.cpanel.views.spells', name='spells'),
    url(r'^spells/edit_spell/(?P<pk>\d+)$','wouso.interface.cpanel.views.edit_spell',name='edit_spell'),
    url(r'^spells/add_spell/$', 'wouso.interface.cpanel.views.add_spell',name='add_spell'),
    url(r'^spells/del/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.spell_delete', name='spell_dell'),

    url(r'^formulas/$','wouso.interface.cpanel.views.formulas',name='formulas'),
    url(r'^formulas/edit_formula/(?P<pk>\d+)/$','wouso.interface.cpanel.views.edit_formula',name='edit_formula'),
    url(r'^formulas/del/(?P<id>\d+)/$','wouso.interface.cpanel.views.formula_delete',name='formula_del'),
    url(r'^formulas/add_formula/$','wouso.interface.cpanel.views.add_formula',name='add_formula'),

    url(r'^group/set/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.groupset', name='group_set'),
    url(r'^staff/toggle/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.stafftoggle', name='staff_toggle'),

    url(r'^players/$', 'wouso.interface.cpanel.views.players', name='all_players'),
    url(r'^players/fwd/$', 'wouso.interface.cpanel.views.fwd', name='manage_fwd'),
    url(r'^players/(?P<player_id>\d+)/bonus/$', 'wouso.interface.cpanel.views.bonus', name='bonus'),
    url(r'^players/add_player/$', 'wouso.interface.cpanel.views.add_player', name='add_player'),
    url(r'^players/infractions/(?P<user_id>\d+)/$', 'wouso.interface.cpanel.views.infraction_history', name='infraction_history'),
    url(r'^players/infractions_clear/(?P<user_id>\d+)/(?P<infraction_id>\d+)/$', 'wouso.interface.cpanel.views.infraction_clear', name='infraction_clear'),
    url(r'^players/infractions_recheck/$', 'wouso.interface.cpanel.views.infraction_recheck', name='infraction_recheck'),
    url(r'^players/manage_player/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.manage_player', name='manage_player'),

    url(r'^races/all/$', 'wouso.interface.cpanel.views.races_groups', name='races_groups'),
    url(r'^races/add/$', 'wouso.interface.cpanel.views.races_add', name='races_add'),
    url(r'^races/groups/add/$', 'wouso.interface.cpanel.views.group_add', name='group_add'),

    url(r'^roles/$', 'wouso.interface.cpanel.views.roles', name='roles'),
    url(r'^roles/(?P<id>\d+)/$', 'wouso.interface.cpanel.views.roles_update', name='roles_update'),
    url(r'^roles/(?P<id>\d+)/kick/player=(?P<player_id>\d+)/$', 'wouso.interface.cpanel.views.roles_update_kick', name='roles_update_kick'),
    url(r'^roles/roles_create$', 'wouso.interface.cpanel.views.roles_create',
name='roles_create'),

    (r'^lessons/', include('wouso.interface.apps.lesson.cpanel_urls')),
    (r'^files/', include('wouso.interface.apps.files.cpanel_urls')),
    (r'^forum/', include('wouso.interface.forum.cpanel_urls')),

    url(r'^activity_monitor/$', 'wouso.interface.cpanel.views.activity_monitor', name='activity_monitor'),

    # misc
    url(r'^tools/clear-cache/$', 'wouso.interface.cpanel.views.clear_cache', name='clear_cache'),

    url(r'^reports/$', 'wouso.interface.cpanel.views.reports', name='reports'),
    url(r'^reports/edit/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.edit_report', name='edit_report'),

    url(r'^system_message/group/(?P<group>\d+)/$', 'wouso.interface.cpanel.views.system_message_group', name='system_message_group'),

    url(r'^impersonate/(?P<player_id>\d+)/$', 'wouso.interface.cpanel.views.impersonate', name='impersonate'),
    url(r'^impersonate/clear/$', 'wouso.interface.cpanel.views.clean_impersonation', name='impersonate_clear'),

    url(r'^static_pages/$', 'wouso.interface.cpanel.views.static_pages', name='static_pages'),
    url(r'^static_pages/add_static_page/$', 'wouso.interface.cpanel.views.add_static_page', name='add_static_page'),
    url(r'^static_pages/edit_static_page/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.edit_static_page', name='edit_static_page'),
    url(r'^static_pages/del_static_page/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.del_static_page', name='del_static_page'),

    url(r'^news/$', 'wouso.interface.cpanel.views.news', name='news'),
    url(r'^news/add_news/$', 'wouso.interface.cpanel.views.add_news', name='add_news'),
    url(r'^news/edit_news/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.edit_news', name='edit_news'),
    url(r'^news/del_news/(?P<pk>\d+)/$', 'wouso.interface.cpanel.views.del_news', name='del_news'),
]

for g, trash in get_cpanel_games().items():
    upat.append((r'{game}/'.format(game=g), include('wouso.{game}.cpanel_urls'.format(game=g.replace('/','.')))))
urlpatterns = patterns('', *upat)
