# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TeamQuestUser'
        db.create_table('teamquest_teamquestuser', (
            ('player_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user.Player'], unique=True, primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='users', null=True, blank=True, to=orm['teamquest.TeamQuestGroup'])),
        ))
        db.send_create_signal('teamquest', ['TeamQuestUser'])

        # Adding model 'TeamQuestGroup'
        db.create_table('teamquest_teamquestgroup', (
            ('playergroup_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user.PlayerGroup'], unique=True, primary_key=True)),
            ('group_owner', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['teamquest.TeamQuestUser'], unique=True, null=True)),
        ))
        db.send_create_signal('teamquest', ['TeamQuestGroup'])

        # Adding model 'TeamQuestLevel'
        db.create_table('teamquest_teamquestlevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='levels', null=True, to=orm['teamquest.TeamQuest'])),
            ('bonus', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('teamquest', ['TeamQuestLevel'])

        # Adding M2M table for field questions on 'TeamQuestLevel'
        m2m_table_name = db.shorten_name('teamquest_teamquestlevel_questions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('teamquestlevel', models.ForeignKey(orm['teamquest.teamquestlevel'], null=False)),
            ('question', models.ForeignKey(orm['qpool.question'], null=False))
        ))
        db.create_unique(m2m_table_name, ['teamquestlevel_id', 'question_id'])

        # Adding model 'TeamQuest'
        db.create_table('teamquest_teamquest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal('teamquest', ['TeamQuest'])

        # Adding model 'TeamQuestQuestion'
        db.create_table('teamquest_teamquestquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='U', max_length=1)),
            ('lock', self.gf('django.db.models.fields.CharField')(default='L', max_length=1)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', null=True, to=orm['teamquest.TeamQuestLevelStatus'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qpool.Question'], null=True)),
        ))
        db.send_create_signal('teamquest', ['TeamQuestQuestion'])

        # Adding model 'TeamQuestLevelStatus'
        db.create_table('teamquest_teamquestlevelstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actives', to=orm['teamquest.TeamQuestLevel'])),
            ('quest_status', self.gf('django.db.models.fields.related.ForeignKey')(related_name='levels', to=orm['teamquest.TeamQuestStatus'])),
        ))
        db.send_create_signal('teamquest', ['TeamQuestLevelStatus'])

        # Adding model 'TeamQuestStatus'
        db.create_table('teamquest_teamqueststatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamquest.TeamQuestGroup'])),
            ('quest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamquest.TeamQuest'])),
            ('time_started', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 4, 8, 0, 0))),
            ('time_finished', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('teamquest', ['TeamQuestStatus'])

        # Adding model 'TeamQuestInvitation'
        db.create_table('teamquest_teamquestinvitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamquest.TeamQuestGroup'], null=True)),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamquest.TeamQuestUser'], null=True)),
        ))
        db.send_create_signal('teamquest', ['TeamQuestInvitation'])

        # Adding model 'TeamQuestInvitationRequest'
        db.create_table('teamquest_teamquestinvitationrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamquest.TeamQuestGroup'], null=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamquest.TeamQuestUser'], null=True)),
        ))
        db.send_create_signal('teamquest', ['TeamQuestInvitationRequest'])


    def backwards(self, orm):
        # Deleting model 'TeamQuestUser'
        db.delete_table('teamquest_teamquestuser')

        # Deleting model 'TeamQuestGroup'
        db.delete_table('teamquest_teamquestgroup')

        # Deleting model 'TeamQuestLevel'
        db.delete_table('teamquest_teamquestlevel')

        # Removing M2M table for field questions on 'TeamQuestLevel'
        db.delete_table(db.shorten_name('teamquest_teamquestlevel_questions'))

        # Deleting model 'TeamQuest'
        db.delete_table('teamquest_teamquest')

        # Deleting model 'TeamQuestQuestion'
        db.delete_table('teamquest_teamquestquestion')

        # Deleting model 'TeamQuestLevelStatus'
        db.delete_table('teamquest_teamquestlevelstatus')

        # Deleting model 'TeamQuestStatus'
        db.delete_table('teamquest_teamqueststatus')

        # Deleting model 'TeamQuestInvitation'
        db.delete_table('teamquest_teamquestinvitation')

        # Deleting model 'TeamQuestInvitationRequest'
        db.delete_table('teamquest_teamquestinvitationrequest')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'game.game': {
            'Meta': {'object_name': 'Game'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'magic.artifact': {
            'Meta': {'unique_together': "(('name', 'group', 'percents'),)", 'object_name': 'Artifact'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['magic.ArtifactGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'percents': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'magic.artifactgroup': {
            'Meta': {'object_name': 'ArtifactGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'magic.groupartifactamount': {
            'Meta': {'unique_together': "(('group', 'artifact'),)", 'object_name': 'GroupArtifactAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'artifact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Artifact']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.PlayerGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'magic.playerartifactamount': {
            'Meta': {'unique_together': "(('player', 'artifact'),)", 'object_name': 'PlayerArtifactAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'artifact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Artifact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Player']"})
        },
        'magic.playerspellamount': {
            'Meta': {'unique_together': "(('player', 'spell'),)", 'object_name': 'PlayerSpellAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Player']"}),
            'spell': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Spell']"})
        },
        'magic.raceartifactamount': {
            'Meta': {'unique_together': "(('race', 'artifact'),)", 'object_name': 'RaceArtifactAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'artifact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Artifact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Race']"})
        },
        'magic.spell': {
            'Meta': {'object_name': 'Spell'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'due_days': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'level_required': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mass': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'percents': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': '1'})
        },
        'qpool.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'qpool.question': {
            'Meta': {'object_name': 'Question'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'endorsed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_endorsedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_proposedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'rich_text': ('ckeditor.fields.RichTextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'})
        },
        'qpool.tag': {
            'Meta': {'object_name': 'Tag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'teamquest.teamquest': {
            'Meta': {'object_name': 'TeamQuest'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        'teamquest.teamquestgroup': {
            'Meta': {'object_name': 'TeamQuestGroup', '_ormbases': ['user.PlayerGroup']},
            'group_owner': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['teamquest.TeamQuestUser']", 'unique': 'True', 'null': 'True'}),
            'playergroup_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user.PlayerGroup']", 'unique': 'True', 'primary_key': 'True'})
        },
        'teamquest.teamquestinvitation': {
            'Meta': {'object_name': 'TeamQuestInvitation'},
            'from_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teamquest.TeamQuestGroup']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teamquest.TeamQuestUser']", 'null': 'True'})
        },
        'teamquest.teamquestinvitationrequest': {
            'Meta': {'object_name': 'TeamQuestInvitationRequest'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teamquest.TeamQuestUser']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teamquest.TeamQuestGroup']", 'null': 'True'})
        },
        'teamquest.teamquestlevel': {
            'Meta': {'object_name': 'TeamQuestLevel'},
            'bonus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'levels'", 'null': 'True', 'to': "orm['teamquest.TeamQuest']"}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Question']", 'symmetrical': 'False'})
        },
        'teamquest.teamquestlevelstatus': {
            'Meta': {'object_name': 'TeamQuestLevelStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actives'", 'to': "orm['teamquest.TeamQuestLevel']"}),
            'quest_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'levels'", 'to': "orm['teamquest.TeamQuestStatus']"})
        },
        'teamquest.teamquestquestion': {
            'Meta': {'object_name': 'TeamQuestQuestion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'null': 'True', 'to': "orm['teamquest.TeamQuestLevelStatus']"}),
            'lock': ('django.db.models.fields.CharField', [], {'default': "'L'", 'max_length': '1'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Question']", 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'})
        },
        'teamquest.teamqueststatus': {
            'Meta': {'object_name': 'TeamQuestStatus'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teamquest.TeamQuestGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teamquest.TeamQuest']"}),
            'time_finished': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'time_started': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 4, 8, 0, 0)'})
        },
        'teamquest.teamquestuser': {
            'Meta': {'object_name': 'TeamQuestUser', '_ormbases': ['user.Player']},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'users'", 'null': 'True', 'blank': 'True', 'to': "orm['teamquest.TeamQuestGroup']"}),
            'player_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user.Player']", 'unique': 'True', 'primary_key': 'True'})
        },
        'user.player': {
            'Meta': {'object_name': 'Player'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.PlayerArtifactAmount']", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '600', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'level_no': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'max_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '20', 'null': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['user.Race']", 'null': 'True'}),
            'spells_collection': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'spell_collection'", 'blank': 'True', 'through': "orm['magic.PlayerSpellAmount']", 'to': "orm['magic.Spell']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_related'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'user.playergroup': {
            'Meta': {'object_name': 'PlayerGroup'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.GroupArtifactAmount']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Game']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['user.Race']", 'null': 'True', 'blank': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['user.Player']", 'symmetrical': 'False', 'blank': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        'user.race': {
            'Meta': {'object_name': 'Race'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.RaceArtifactAmount']", 'blank': 'True'}),
            'can_play': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['teamquest']